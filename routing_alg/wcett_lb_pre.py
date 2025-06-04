import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from log_config import get_logger
import routing_alg.wcett as wcett
from routing_alg.routing_utils import (
    CONGESTION_THRESHOLD, 
    LOAD_BALANCE_THRESHOLD,
    calculate_traffic_concentration, 
    compute_ql_b_term,
    get_min_ett,
    get_child_nodes,
    find_all_paths
)

logger = get_logger("lb_pre")

def predict_congestion(node, nw, routing_alg):
    """Predicts the node congestion status and multicasts WCETT-LB metrics if predicted to be congested
        Should be calculated periodiacally
        
    Args:
        node: The node to check for predicted congestion
        nw: The network graph
        routing_alg: The routing algorithm instance
        
    Returns:
        bool: True if congestion is predicted, False otherwise
    """
    ql_b_term = compute_ql_b_term(node, nw)
    
    was_predicted = node.predicted_congestion if hasattr(node, 'predicted_congestion') else False
    node.predicted_congestion = (ql_b_term >= CONGESTION_THRESHOLD)
    
    # Initialize last update time if not already set
    if not hasattr(node, 'last_wcett_lb_update_time'):
        node.last_wcett_lb_update_time = time.time()
    
    current_time = time.time()
    force_update = (current_time - node.last_wcett_lb_update_time) >= 3  # Force update every 5 seconds
    
    # If congestion prediction state changed OR forced update time reached
    if node.predicted_congestion != was_predicted or force_update:
        node.wcett_lb_update_time = current_time
        node.last_wcett_lb_update_time = current_time
        node.reported_congestion = node.predicted_congestion  # True if predicted congestion, False if not
        
        # Calculate WCETT-LB metrics for all paths from this node
        paths = []
        for dest_id in nw.nodes:
            if dest_id != node.id:
                current_path = routing_alg.path_cache.get((node.id, dest_id))
                if current_path:
                    edges = []
                    for i in range(len(current_path) - 1):
                        edge = nw.get_edge_between_nodes(current_path[i], current_path[i+1])
                        if edge:
                            edges.append(edge)
                    
                    if edges:
                        metric = compute_wcett_lb(edges, 1024, nw, current_path)
                        paths.append((dest_id, current_path, metric))
        
        child_nodes = get_child_nodes(node, nw)
        
        # Multicast WCETT-LB metrics to N_i
        for child_id in child_nodes:
            child = nw.nodes[child_id]
            if hasattr(child, 'receive_wcett_lb_update'):
                child.receive_wcett_lb_update(node.id, paths)

    return node.predicted_congestion

def compute_wcett_lb(edges, packet_sz, nw, path):
    """_summary_

    Args:
        edges (_type_): _description_
        packet_sz (_type_): _description_
        nw (_type_): _description_
        path (_type_): _description_

    Returns:
        _type_: _description_
    """
    base = wcett.compute_wcett(edges, packet_sz)
    
    traffic_concentration = calculate_traffic_concentration(nw)
    min_ett = get_min_ett(nw)
    
    load_penalty = 0
    
    for node_id in path[1:-1]:
        node = nw.nodes[node_id]
        ql_b_term = compute_ql_b_term(node, nw)
            
        # Traffic concentration term
        ni_term = min_ett * traffic_concentration[node_id]
        load_penalty += (ql_b_term + ni_term)
    
    # Final WCETT-LB value
    wcett_lb = base + load_penalty
    return wcett_lb

def update_path(node, nw, dest_id, routing_alg):
    """
    Update routing path based on congestion predictions and WCETT-LB metrics
    from nodes in the current path and child nodes.
    
    Args:
        node: The node that might update its routing table
        nw: The network graph
        dest_id: Destination node ID
        routing_alg: The routing algorithm instance
    """
    received_wcett_lb_update = False
    congestion_state_changed = False
    
    if hasattr(node, 'wcett_lb_updates'):
        current_time = time.time()
        for sender_id, update in node.wcett_lb_updates.items():
            if current_time - update['timestamp'] < 3: # Consider updates valid for 3 seconds
                received_wcett_lb_update = True
                # Check if this update represents a congestion state change
                if update.get('state_changed', False):
                    congestion_state_changed = True
    
    if not received_wcett_lb_update:
        return # No updates received, nothing to do
    
    current_path = routing_alg.path_cache.get((node.id, dest_id))
    if not current_path:
        return
    
    current_edges = []
    for i in range(len(current_path) - 1):
        edge = nw.get_edge_between_nodes(current_path[i], current_path[i+1])
        if edge:
            current_edges.append(edge)
    
    if not current_edges:
        return
    
    current_metric = compute_wcett_lb(current_edges, 1024, nw, current_path)
    
    all_paths = find_all_paths(nw, node.id, dest_id)
    if not all_paths or len(all_paths) <= 1:
        logger.error(f"⚠️ Node {node.id} could not find alternative path to {dest_id}")
        return # No alternatives available
    
    # Find path with best (lowest) WCETT-LB metric (WCETT_LB^i_best)
    best_path = None
    best_metric = float('inf')
    
    for path in all_paths:
        if path == current_path:
            continue
        
        path_edges = []
        for i in range(len(path) - 1):
            edge = nw.get_edge_between_nodes(path[i], path[i+1])
            if edge:
                path_edges.append(edge)
        
        if not path_edges:
            continue
        
        path_metric = compute_wcett_lb(path_edges, 1024, nw, path)
        
        if path_metric < best_metric:
            best_metric = path_metric
            best_path = path
    
    if not best_path:
        return

    # If WCETT-LB_current - WCETT-LB_best > threshold, make the switch
    if current_metric - best_metric >= LOAD_BALANCE_THRESHOLD:
        routing_alg.path_cache[(node.id, dest_id)] = best_path
        if len(best_path) >= 2:
            node.routing_table[dest_id] = best_path[1]
            logger.info(f"Proactively switched path for node {node.id}: {current_path} → {best_path}")
    elif congestion_state_changed:
        logger.error(f"⚠️ Node {node.id} failed to find an alternative path to node {dest_id} with sufficient improvement.")
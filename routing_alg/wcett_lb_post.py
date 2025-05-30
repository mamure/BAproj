from routing_alg import wcett
from routing_alg.routing_utils import calculate_traffic_concentration, get_min_ett, CONGESTION_THRESHOLD, LOAD_BALANCE_THRESHOLD
from log_config import get_logger
import time

logger = get_logger("lb_post")

def update_congest_status(node, nw):
    """Updates the node congestion status
        Should be calculated periodiacally
    """
    total_bw = 0
    count = 0
    for neighbor_id in node.neighbors:
        edge = nw.get_edge_between_nodes(node.id, neighbor_id)
        if edge and edge.active:
            total_bw += edge.bandwidth
            count += 1
    avg_tx_rate = total_bw / count if count > 0 else 0
    
    queue_length = node.queue.qsize()
    
    if avg_tx_rate > 0:
        ql_b_term = queue_length / avg_tx_rate
        is_congested = node.congest_status if hasattr(node, 'congest_status') else False
        node.congest_status = (ql_b_term >= CONGESTION_THRESHOLD)
        
        # multicast WCETT-LB to N_i
        if node.congest_status and not is_congested:
            node.wcett_lb_update_time = time.time()
            node.reported_congestion = True
    else:
        node.congest_status = True
    
    node.load = queue_length
    return node.congest_status

def compute_wcett_lb(edges, packet_sz, nw, path):
    base = wcett.compute_wcett(edges, packet_sz)
    
    traffic_concentration = calculate_traffic_concentration(nw)
    min_ett = get_min_ett(nw)
    
    load_penalty = 0
    
    for node_id in  path[1:-1]:
        node = nw.nodes[node_id]
        update_congest_status(node, nw)
        
        total_bw = 0
        for neighbor_id in node.neighbors:
            edge = nw.get_edge_between_nodes(node_id, neighbor_id)
            if edge and edge.active:
                total_bw += edge.bandwidth
        
        if total_bw > 0:
            ql_b_term = node.queue.qsize() / total_bw
        else:
            ql_b_term = node.queue.qsize()
            
        # Traffic concentration term
        ni_term = min_ett * traffic_concentration[node_id]
        load_penalty += (ql_b_term + ni_term)
    
    # Final WCETT-LB value
    wcett_lb = base + load_penalty
    return wcett_lb

def update_path(node, nw, dest_id, routing_alg):
    current_path = routing_alg.path_cache.get((node.id, dest_id))
    if not current_path:
        return False, None
    
    # Check if any nodes in current path have reported congestion
    received_congestion = False
    congested_nodes = []
    
    for node_id in current_path[1:-1]:
        transit_node = nw.nodes[node_id]

        if (hasattr(transit_node, 'reported_congestion') and 
            transit_node.reported_congestion and
            hasattr(transit_node, 'wcett_lb_update_time') and
            time.time() - transit_node.wcett_lb_update_time < 5):  # Consider warnings valid for 5 seconds
            
            received_congestion = True
            congested_nodes.append(node_id)
    
    if received_congestion:
        # Calculate WCETT-LB for current path
        current_edges = []
        for i in range(len(current_path) - 1):
            edge = nw.get_edge_between_nodes(current_path[i], current_path[i+1])
            if edge:
                current_edges.append(edge)
        
        current_metric = compute_wcett_lb(current_edges, 1024, nw, current_path)
        
        # Find alternative path avoiding congested nodes
        new_path = routing_alg.alternative_path(nw, node.id, dest_id, congested_nodes)
        
        if new_path and new_path != current_path:
            # Calculate WCETT-LB for new path
            new_edges = []
            for i in range(len(new_path) - 1):
                edge = nw.get_edge_between_nodes(new_path[i], new_path[i+1])
                if edge:
                    new_edges.append(edge)
            
            new_metric = compute_wcett_lb(new_edges, 1024, nw, new_path)
            
            # If WCETT-LB_current - WCETT-LB_best > threshold, make the switch
            if current_metric - new_metric > LOAD_BALANCE_THRESHOLD:
                routing_alg.path_cache[(node.id, dest_id)] = new_path
                if len(new_path) >= 2:
                    node.routing_table[dest_id] = new_path[1]
                    logger.info(f"Switched path for node {node.id}: {current_path} → {new_path}")
        else:
            logger.error(f"⚠️ Node {node.id} could not find alternative path to {dest_id} that avoids {congested_nodes}")
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from routing_alg import wcett

CONGESTION_THRESHOLD = 0.5 # Congestion level threshold for mesh routers, σ = 0.5, (prediction threshold)
LOAD_BALANCE_THRESHOLD = 0.4 # Load-balancing threshold for path switching in a mesh network, ẟ = 0.4

def find_all_paths(nw, src, dest, path=None, visited=None, max_depth=10):
    if path is None:
        path = [src]
    if visited is None:
        visited = set([src])
        
    if src == dest:
        return [path]
    if len(path) > max_depth:
        return []
    
    all_paths = []
    src_node = nw.nodes[src]
    
    for neighbor_id in src_node.neighbors:
        if neighbor_id not in visited:
            neighbor_node = nw.nodes[neighbor_id]
            if neighbor_node.type == "C" and neighbor_id != dest:
                continue
            edge = nw.get_edge_between_nodes(src, neighbor_id)
            if edge and edge.active:
                
                new_visited = visited.copy()
                new_visited.add(neighbor_id)
                new_path = path + [neighbor_id]
                
                next_paths = find_all_paths(nw, neighbor_id, dest, new_path, new_visited, max_depth)
                all_paths.extend(next_paths)
                
    return all_paths

def is_valid_path(nw, path):
    if len(path) <= 2:
        return True
        
    for node_id in path[1:-1]:
        node = nw.nodes[node_id]
        if node.type == "C":  # Client nodes can't be transit nodes
            return False
            
    return True

def calculate_traffic_concentration(nw):
    """
    Calculate Ni - the number of child nodes using each node as next hop
    """
    traffic_concentration = {node_id: 0 for node_id in nw.nodes}
    
    for node_id, node in nw.nodes.items():
        for dest_id, next_hop in node.routing_table.items():
            if next_hop in traffic_concentration:
                traffic_concentration[next_hop] += 1
                
    return traffic_concentration

def get_min_ett(nw):
    """Find the smallest ETT in the network"""
    min_ett = float('inf')
    
    for edge in nw.edges.values():
        if edge.active:
            ett = wcett.compute_ett(edge, 1024)
            min_ett = min(min_ett, ett)
    
    result = min_ett if min_ett != float('inf') else 1.0
    return result

def compute_ql_b_term(node, nw):
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
    else:
        ql_b_term = 0
    return ql_b_term

def get_child_nodes(node, nw):
    """Find nodes that use this node as their next hop (N_i)
    
    Args:
        node: The node to find children for
        nw: The network graph
        
    Returns:
        list: List of node IDs that use this node as next hop
    """
    child_nodes = []
    
    for potential_child_id in nw.nodes:
        potential_child = nw.nodes[potential_child_id]
        if potential_child_id != node.id and hasattr(potential_child, 'routing_table'):
            for dest_id, next_hop in potential_child.routing_table.items():
                if next_hop == node.id:
                    if potential_child_id not in child_nodes:
                        child_nodes.append(potential_child_id)
                    break
    
    return child_nodes
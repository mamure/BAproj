import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from routing_alg import wcett

CONGESTION_THRESHOLD = 0.005 # Congestion level threshold for mesh routers, σ = 0.005
LOAD_BALANCE_THRESHOLD = 0.004 # Load-balancing threshold for path switching in a mesh network, ẟ = 0.004

def find_all_paths(nw, src, dest, path=None, visited=None, max_depth=10):
    """Recursively finds all possible paths between source and destination nodes

    Args:
        nw (NetworkGraph): The network graph object
        src (int): ID of the source node
        dest (int): ID of the destination node
        path (list, optional): Current path being explored. Defaults to None.
        visited (set, optional): Set of visited nodes. Defaults to None.
        max_depth (int, optional): Maximum path length to consider. Defaults to 10.

    Returns:
        list: List of all valid paths from source to destination
    """
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
    """Validates if a path follows network constraints
    
    Checks if a path is valid by ensuring client nodes are not used as
    transit nodes (nodes in the middle of a path).

    Args:
        nw (NetworkGraph): The network graph object
        path (list): List of node IDs representing a path

    Returns:
        bool: True if the path is valid, False otherwise
    """
    if len(path) <= 2:
        return True
        
    for node_id in path[1:-1]:
        node = nw.nodes[node_id]
        if node.type == "C":  # Client nodes can't be transit nodes
            return False
            
    return True

def calculate_traffic_concentration(nw):
    """Calculate traffic concentration at each node based on routing tables

    Args:
        nw (NetworkGraph): The network graph object with routing tables

    Returns:
        dict: Dictionary mapping node IDs to their traffic concentration values
    """
    traffic_concentration = {node_id: 0 for node_id in nw.nodes}
    
    for node_id, node in nw.nodes.items():
        for dest_id, next_hop in node.routing_table.items():
            if next_hop in traffic_concentration:
                traffic_concentration[next_hop] += 1
                
    return traffic_concentration

def get_min_ett(nw):
    """Find the smallest ETT value in the network

    Args:
        nw (NetworkGraph): The network graph object

    Returns:
        float: The smallest ETT value in the network, or 1.0 if no active edges exist
    """
    min_ett = float('inf')
    
    for edge in nw.edges.values():
        if edge.active:
            ett = wcett.compute_ett(edge, 1024)
            min_ett = min(min_ett, ett)
    
    result = min_ett if min_ett != float('inf') else 1.0
    return result

def compute_ql_b_term(node, nw):
    """Calculate queue-length to bandwidth ratio term for congestion estimation
    
    Args:
        node (Node): The node object to calculate the term for
        nw (NetworkGraph): The network graph object

    Returns:
        float: The queue-length to bandwidth ratio term
    """
    total_bw = 0
    count = 0
    for neighbor_id in node.neighbors:
        edge = nw.get_edge_between_nodes(node.id, neighbor_id)
        if edge and edge.active:
            total_bw += edge.bandwidth
            count += 1
    # Calculate average bandwidth in bits per second
    avg_tx_rate = (total_bw / count) * 1_000_000 if count > 0 else 0

    # Convert queue length to bits
    queue_length = node.queue.qsize() * (1024 * 8)

    # Calculate queue length to bandwidth ratio
    ql_b_term = queue_length / avg_tx_rate  # bits / (bits/second) = seconds
    return ql_b_term

def get_child_nodes(node, nw):
    """Identify nodes that use the given node as their next hop

    Args:
        node (Node): The node to find children for
        nw (NetworkGraph): The network graph object
        
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
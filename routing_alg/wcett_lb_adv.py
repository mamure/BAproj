from routing_alg import wcett

CONGESTION_THRESHOLD = 0.75
LOAD_BALANCE_THRESHOLD = 0

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
            ett = wcett.calculate_ett(edge, 1024)
            min_ett = min(min_ett, ett)
    
    return min_ett if min_ett != float('inf') else 1.0

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
    
    node.load = node.queue.qsize()
    
    if avg_tx_rate <= 0:
        node.congest_status = True
    else:
        congestion_level = node.load / avg_tx_rate
        node.congest_status = (congestion_level >= CONGESTION_THRESHOLD)
        
def compute_wcett_lb(edges, packet_sz, nw, path):
    base = wcett.compute_wcett(edges, packet_sz)
    
    traffic_concentration = calculate_traffic_concentration(nw)
    min_ett = get_min_ett(nw)
    
    load_penalty = 0
    congested_node_count = 0
    
    for node_id in  path[1:-1]:
        node = nw.nodes[node_id]
        update_congest_status(node, nw)
        
        if node.congest_status:
            congested_node_count += 1
        
        total_bw = 0
        for neighbor_id in node.neighbors:
            edge = nw.get_edge_between_nodes(node_id, neighbor_id)
            if edge and edge.active:
                total_bw += edge.bandwidth
        
        if total_bw > 0:
            ql_b_term = node.queue.qsize() / total_bw
        else:
            ql_b_term = node.queue.qsize()  # Avoid division by zero
            
        # Traffic concentration term: min(ETT) * Ni
        ni_term = min_ett * traffic_concentration[node_id]
        
        # Add both terms to the load penalty
        load_penalty += (ql_b_term + ni_term)
    
    # Final WCETT-LB value
    wcett_lb = base + load_penalty
    
    return wcett_lb, congested_node_count

def get_congested_node_count(nw, path):
    """Count the number of congested nodes in a path
    """
    count = 0
    for node_id in path[1:-1]:
        node = nw.nodes[node_id]
        update_congest_status(node, nw)
        if node.congest_status:
            count += 1
    return count

def update_path(node, nw, dest_id, routing_alg):
    current_path = routing_alg.path_cache.get((node.id, dest_id))
    if not current_path:
        return False, None
    
    congested_nodes = []
    for node_id in current_path[1:-1]:
        if nw.nodes[node_id].congest_status:
            congested_nodes.append(node_id)
    if len(congested_nodes) > LOAD_BALANCE_THRESHOLD:
        new_path = routing_alg.alternative_path(nw, node.id, dest_id, congested_nodes)
        if new_path and new_path != current_path:
            routing_alg.path_cache[(node.id, dest_id)] = new_path
            if len(new_path) >= 2:
                node.routing_table[dest_id] = new_path[1]
                print(f"WCETT-LB PATH SWITCH: Node {node.id} switched path to {dest_id}: {current_path} → {new_path}")
                return True, (current_path, new_path)
        else:
            print(f"⚠️ Node {node.id} could not find alternative path to {dest_id} that avoids {congested_nodes}")
                
    return False, None
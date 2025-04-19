from routing_alg import wcett

CONGESTION_THRESHOLD = 0.75
LOAD_BALANCE_THRESHOLD = 1

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
    congested_nodes_count = 0
    penalty = 0
    
    for node_id in path[1:-1]:
        node = nw.nodes[node_id]
        update_congest_status(node, nw)
        if node.congest_status:
            congested_nodes_count += 1
            penalty += (node.load - LOAD_BALANCE_THRESHOLD)
        
        if congested_nodes_count > LOAD_BALANCE_THRESHOLD:
            penalty *= 2
    return (base + penalty, congested_nodes_count)

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
                return True, (current_path, new_path)
        else:
            print(f"⚠️ Node {node.id} could not find alternative path to {dest_id} that avoids {congested_nodes}")
                
    return False, None
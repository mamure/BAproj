from routing_alg import wcett

CONGESTION_THRESHOLD = 5
LOAD_BALANCE_THRESHOLD = 2

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
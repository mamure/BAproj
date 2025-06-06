from collections import deque

def shortest_path(graph, src_id, dest_id):
    """Finds the shortest path between source and destination nodes using breadth-first search

    Args:
        graph (NetworkGraph): The network graph object containing nodes and connectivity information
        src_id (str/int): ID of the source node
        dest_id (str/int): ID of the destination node

    Returns:
        list: Ordered list of node IDs representing the shortest path, or None if no path exists
    """
    src_node = graph.nodes[src_id]
    if dest_id not in graph.nodes:
        return []
    target_node = graph.nodes[dest_id]
    
    visited = set()
    queue = deque([(src_node, [src_node.id])])

    while queue:
        current_node, path = queue.popleft()
        if current_node.id in visited:
            continue
        
        visited.add(current_node.id)

        if current_node.id == target_node.id:
            return path
        
        for neighbor_id in current_node.neighbors:
            if neighbor_id not in visited:
                neighbor_node = graph.nodes[neighbor_id]
                if neighbor_node.type == "C" and neighbor_id != dest_id:
                    continue
                queue.append((graph.nodes[neighbor_id], path + [neighbor_id]))

    return None

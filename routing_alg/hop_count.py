from collections import deque

def shortest_path(graph, src_id, dest_id):
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
                queue.append((graph.nodes[neighbor_id], path + [neighbor_id]))

    return None

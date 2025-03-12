from collections import deque

def shortest_path(graph, start_id, target_id):
    if start_id == target_id:
        return []
    
    start_node = graph.nodes[start_id]
    if target_id not in graph.nodes:
        return []
    target_node = graph.nodes[target_id]
    
    visited = set()
    queue = deque([(start_node, [start_node.id])])

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

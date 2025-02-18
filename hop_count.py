def shortest_path(graph, start_id, target_id):
    if start_id == target_id: # source node is destination node 
        return None
    
    # id to node object
    start_node = graph.nodes[start_id] 
    target_node = graph.nodes[target_id]
    
    visited = set()
    queue = [(start_node, [start_node.id])]

    while queue:
        current_node, path = queue.pop(0)

        if current_node.id in visited:
            continue
        
        visited.add(current_node.id)

        if current_node == target_node:
            return path
        
        for neighbor_id in current_node.neighbors:
            if neighbor_id not in visited:
                queue.append((graph.nodes[neighbor_id], path + [neighbor_id]))

    return None
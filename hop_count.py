import network as nt

def shortest_path(start_node, target_node):
    if start_node.id == target_node.id:
        print("Error, source node is destination node.")
        return None
    
    visited = set()
    queue = [(start_node, [start_node])]
    
    while queue:
        current_node, path = queue.pop(0)
        
        if current_node.id in visited: # if node already has been visited skip it
            continue
        
        visited.add(current_node.id)
        
        if current_node == target_node:
            return path

        for edge in current_node.edges:
            print(edge)
            neighbor = edge.node_b if edge.node_a == current_node else edge.node_a
            if neighbor.id not in visited:
                queue.append((neighbor, path + [neighbor]))
        
    return None


if __name__ == "__main__":
    g = nt.Graph()
    node1 = g.create_node("Router")
    node2 = g.create_node("Router")
    node3 = g.create_node("Client")
    node4 = g.create_node("Gateway")
    
    g.add_edge(node1, node2, 1)
    g.add_edge(node2, node3, 1)
    g.add_edge(node3, node4, 1)
    g.add_edge(node1, node4, 1)
    
    # Find the shortest (hop count) path from node1 to node3.
    path = shortest_path(node1, node3)
    if path:
        # The hop count is the number of edges, which is one less than the number of nodes in the path.
        hop_count = len(path) - 1
        print("Shortest path:", " -> ".join(node.id for node in path))
        print("Hop count:", hop_count)
    else:
        print("No path found between", node1.id, "and", node3.id)
import random as rnd

# trans_rate = # between x and y
# avg_queue = 2
# congest_lvl = avg_queue / trans_rate

# congest_status = False

# congest_threshold = 5
# lb_threshold_switch = 2

# if congest_lvl >= congest_threshold:
#     congest_status = True # congested
# else:
#     congest_status = False # load-balanced

class Node:
    """
    A class representing a node in a graph.
    
    Args:
        node_id (int): The identifier for the node.
        type (str): The type of the node.
    """
    def __init__(self, node_id, type):
        self.id = node_id
        self.type = type
        self.edges = []
        
    def add_edge(self, node):
        """
        Add edge between two nodes
        
        Args:
            node (int): The identifier for the node to be added.
        """
        if node.id not in self.edges:
            edge = graph.create_edge()
            self.edges.append(node.id)
            node.edges.append(self.id)
            return edge
        
    def remove_edge(self, node):
        """
        Remove edge between two nodes
        
        Args:
            node (int): The identifier for the node to be added.
        """
        if node.id in self.edges:
            self.edges.remove(node.id)
            node.edges.remove(self.id)
        

class Edge:
    """
    A class representing an edge in a graph.
    
    Args:
        edge_id (int): The identifier for the node.
        trans_rate (float, optional): Transmission rate between nodes
    """
    def __init__(self, edge_id, node_a, node_b, trans_rate):
        self.id = edge_id
        self.node_a = node_a.id
        self.node_b = node_b.id
        self.trans_rate = trans_rate
        
class Graph:
    def __init__(self):
        self.node_id_counter = 0
        self.edge_id_counter = 0
        
    def create_node():
        node = Node(node_id_counter)
        node_id_counter += 1
        return node
    
    def create_edge(node_a, node_b, trans_rate):
        edge = Edge(node_a, node_b, trans_rate)
        node_a.edges.append(node_b.id)
        node_b.edges.append(node_a.id)
        edge_id_counter += 1
        return edge

    def remove_node():
        return
        
    def remove_edge():
        return
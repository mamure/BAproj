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
    def __init__(self, node_id, type):
        self.id = node_id
        self.type = type
        self.edges = []
        self.congest_status = False

class Edge:
    def __init__(self, edge_id, node_a, node_b, trans_rate):
        self.id = edge_id
        self.node_a = node_a.id
        self.node_b = node_b.id
        self.trans_rate = trans_rate
        
class Graph:
    def __init__(self):
        self.node_id_counter = 0
        self.edge_id_counter = 0
        self.nodes = {}
        self.edges = {}
        
    def create_node(self, type):
        node = Node(self.node_id_counter, type)
        self.nodes[self.node_id_counter] = node
        self.node_id_counter += 1
        return node
    
    def add_edge(self, node_a, node_b, trans_rate):
        if node_b.id not in node_a.edges:
            edge = Edge(self.edge_id_counter, node_a, node_b, trans_rate)
            node_a.edges.append((node_b.id,trans_rate))
            node_b.edges.append((node_a.id,trans_rate))
            self.edges[self.edge_id_counter] = edge
            self.edge_id_counter += 1
            return edge
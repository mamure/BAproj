class Node:
    def __init__(self, node_id, type):
        self.id = node_id
        self.type = type
        self.neighbors = []
        self.routing_table = {}
        self.traffic_load = 0
        self.congest_status = False

class Edge:
    def __init__(self, edge_id, node_a, node_b, weight):
        self.id = edge_id
        self.node_a = node_a
        self.node_b = node_b
        self.weight = weight
        # self.bandwidth = bandwidth
        # self.delay = delay
        # self.loss_rate = loss_rate
        # self.load = load
        
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
    
    def add_edge(self, node_a, node_b, weight):
        if node_b.id not in node_a.neighbors:
            edge = Edge(self.edge_id_counter, node_a, node_b, weight)
            self.edges[self.edge_id_counter] = edge
            self.edge_id_counter += 1
            node_a.neighbors.append(node_b.id)
            node_b.neighbors.append(node_a.id)
            return edge
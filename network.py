class Node:
    def __init__(self, node_id, type):
        self.id = node_id
        self.type = type
        self.neighbors = []
        self.routing_table = {}
        self.load = 0
        self.congest_status = False
        
    def __repr__(self):
        return f"Node(id={self.id}, type={self.device_type})"

class Edge:
    def __init__(self, edge_id, src, dst, bandwidth, loss_rate, channel = 1):
        self.id = edge_id
        self.src = src
        self.dst = dst
        self.bandwidth = bandwidth
        self.loss_rate = loss_rate
        self.channel = channel
        
    def __repr__(self):
        return f"Edge({self.node_a.id} <-> {self.node_b.id})"
    
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
    
    def add_edge(self, node_a, node_b, bandwidth, loss_rate):
        if node_b.id not in node_a.neighbors:
            edge = Edge(self.edge_id_counter, node_a, node_b, bandwidth, loss_rate)
            self.edges[self.edge_id_counter] = edge
            self.edge_id_counter += 1
            node_a.neighbors.append(node_b.id)
            node_b.neighbors.append(node_a.id)
            return edge
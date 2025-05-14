import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import routing_alg.routing as routing
from network import Graph


class TestPacket(unittest.TestCase):
    def setUp(self):
        self.graph = Graph()
        
    def test_hop_packet_route(self):
        # Create a simple network topology
        # a11 -- b12 --c13
        # |            |
        # d14 ------- e15
        
        # Create nodes
        node_a = self.graph.create_node("IGW")
        node_b = self.graph.create_node("AP")
        node_c = self.graph.create_node("AP")
        node_d = self.graph.create_node("AP")
        node_e = self.graph.create_node("C")
        
        # Connect nodes with edges
        self.graph.add_edge(node_a, node_b, 100, 0)
        self.graph.add_edge(node_b, node_c, 100, 0)
        self.graph.add_edge(node_a, node_d, 100, 0)
        self.graph.add_edge(node_c, node_e, 100, 0)
        self.graph.add_edge(node_d, node_e, 1, 0)
        
        for node_id, node in self.graph.nodes.items():
            next_hop = routing.HopCountRouting().compute_routing_tb(self.graph, node_id, node_a.id)
            if next_hop is not None:
                node.routing_table[node_a.id] = next_hop
        
        self.graph.start_network()
    
        self.graph.send_packet_graph(node_e.id, node_a.id)
    
        expected_path = [node_e.id, node_d.id, node_a.id]
        result = self.graph.send_packet_graph(node_e.id, node_a.id)
        packet = result["packet"]
        self.assertEqual(packet.route_taken, expected_path)
        
        self.graph.stop_network()
        
    def test_wcett_packet_route(self):
        # Create a simple network topology
        # a16 -- b17 --c18
        # |            |
        # d19 ------- e20
        
        # Create nodes
        node_a = self.graph.create_node("IGW")
        node_b = self.graph.create_node("AP")
        node_c = self.graph.create_node("AP")
        node_d = self.graph.create_node("AP")
        node_e = self.graph.create_node("C")
        
        # Connect nodes with edges
        self.graph.add_edge(node_a, node_b, 1000, 0)
        self.graph.add_edge(node_b, node_c, 1000, 0)
        self.graph.add_edge(node_a, node_d, 1000, 0)
        self.graph.add_edge(node_c, node_e, 1000, 0)
        self.graph.add_edge(node_d, node_e, 1, 0)
        
        for node_id, node in self.graph.nodes.items():
            next_hop = routing.WCETTRouting().compute_routing_tb(self.graph, node_id, node_a.id)
            if next_hop is not None:
                node.routing_table[node_a.id] = next_hop
        
        self.graph.start_network()
        
        self.graph.send_packet_graph(node_e.id, node_a.id)
        expected_path = [node_e.id, node_c.id, node_b.id, node_a.id]
        
        result = self.graph.send_packet_graph(node_e.id, node_a.id)
        packet = result["packet"]
        self.assertEqual(packet.route_taken, expected_path)
        
        self.graph.stop_network()
        
if __name__ == '__main__':
    unittest.main()
import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routing_alg.wcett import compute_ett, compute_wcett
from network import Graph

class TestWCETT(unittest.TestCase):
    def setUp(self):
        self.graph = Graph()
    
    def test_compute_ett(self):
        node_1 = self.graph.create_node("router")
        node_2 = self.graph.create_node("router")
        
        edge = self.graph.add_edge(node_1, node_2, 100, 0.01)
        
        packet_size = 1000
        ett = compute_ett(edge, packet_size)
        
        # Expected ETT calculation:
        expected_p = 1 - (1 - 0.01) * (1 - 0.01)
        expected_etx = 1 / (1 - expected_p)
        
        bandwidth_bps = 100 * 125000
        expected_ett = expected_etx * (packet_size / bandwidth_bps)
        
        # Allow for floating-point precision issues
        self.assertAlmostEqual(ett, expected_ett, places=10)
        
    def test_compute_wcett_single_edge(self):
        node_1 = self.graph.create_node("router")
        node_2 = self.graph.create_node("router")
        
        edge = self.graph.add_edge(node_1, node_2, 100, 0.01)
        edge.channel = 1
        
        packet_size = 1000
        edges = [edge]
        
        wcett_value = compute_wcett(edges, packet_size)
        ett_value = compute_ett(edge, packet_size)
        
        # For a single edge, WCETT should equal ETT
        self.assertAlmostEqual(wcett_value, ett_value, places=10)
        
    def test_compute_wcett_multi_channel(self):
        node_1 = self.graph.create_node("router")
        node_2 = self.graph.create_node("router")
        node_3 = self.graph.create_node("router")
        
        edge1 = self.graph.add_edge(node_1, node_2, 100, 0.01)
        edge1.channel = 1
        
        edge2 = self.graph.add_edge(node_2, node_3, 50, 0.02)
        edge2.channel = 2
        
        packet_size = 1000
        edges = [edge1, edge2]
        
        ett1 = compute_ett(edge1, packet_size)
        ett2 = compute_ett(edge2, packet_size)
        
        wcett_value = compute_wcett(edges, packet_size)
        
        # WCETT should be: β * (ett1 + ett2) + (1 - β) * max(ett1, ett2)
        expected_wcett = 0.5 * (ett1 + ett2) + (1 - 0.5) * max(ett1, ett2)
        
        self.assertAlmostEqual(wcett_value, expected_wcett, places=10)
        
    def test_compute_wcett_same_channel(self):
        node_1 = self.graph.create_node("router")
        node_2 = self.graph.create_node("router")
        node_3 = self.graph.create_node("router")
        
        edge1 = self.graph.add_edge(node_1, node_2, 100, 0.01)
        edge1.channel = 1
        
        edge2 = self.graph.add_edge(node_2, node_3, 50, 0.02)
        edge2.channel = 1
        
        packet_size = 1000
        edges = [edge1, edge2]
        
        ett1 = compute_ett(edge1, packet_size)
        ett2 = compute_ett(edge2, packet_size)
        
        wcett_value = compute_wcett(edges, packet_size)
        
        # WCETT should be: β * (ett1 + ett2) + (1 - β) * max(ett1, ett2)
        expected_wcett = 0.5 * (ett1 + ett2) + (1 - 0.5) * (ett1 + ett2)
        
        self.assertAlmostEqual(wcett_value, expected_wcett, places=10)
    
if __name__ == '__main__':
    unittest.main()
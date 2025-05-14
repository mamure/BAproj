import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routing_alg.hop_count import shortest_path
from network import Graph

class TestNetwork(unittest.TestCase):
    def setUp(self):
        self.graph = Graph()
    
    def test_shortest_path(self):
        node_a = self.graph.create_node("router")
        node_b = self.graph.create_node("router")
        node_c = self.graph.create_node("router")
        
        self.graph.add_edge(node_a, node_b, 100, 0.01)
        self.graph.add_edge(node_b, node_c, 100, 0.01)
        
        # direct
        path_a_b = shortest_path(self.graph, node_a.id, node_b.id)
        self.assertEqual(len(path_a_b), 2)
        self.assertEqual(path_a_b[0], node_a.id)
        self.assertEqual(path_a_b[1], node_b.id)
        
        # multi hop
        path_a_c = shortest_path(self.graph, node_a.id, node_c.id)
        self.assertEqual(len(path_a_c), 3)
        self.assertEqual(path_a_c[0], node_a.id)
        self.assertEqual(path_a_c[-1], node_c.id)
        
        # non-existing
        non_existing_id = 3
        path_a_non = shortest_path(self.graph, node_a.id, non_existing_id)
        self.assertEqual(path_a_non, [])
import unittest

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from network import Node, Edge, Graph, node_id_manager, edge_id_manager, packet_id_manager

class TestNetwork(unittest.TestCase):
    def setUp(self):
        self.graph = Graph()
    
    def test_create_node(self):
        node = self.graph.create_node("router")
        self.assertIsInstance(node, Node)
        self.assertEqual(node.type, "router")
        self.assertFalse(node.running)
    
    def test_add_edge(self):
        node_a = self.graph.create_node("router")
        node_b = self.graph.create_node("host")
        edge = self.graph.add_edge(node_a, node_b, 100, 0.01)
        
        self.assertIsInstance(edge, Edge)
        self.assertEqual(edge.src, node_a)
        self.assertEqual(edge.dest, node_b)
        self.assertEqual(edge.bandwidth, 100)
        self.assertEqual(edge.loss_rate, 0.01)
        self.assertTrue(node_b.id in node_a.neighbors)
        self.assertTrue(node_a.id in node_b.neighbors)
        
    def test_get_edge_between_nodes(self):
        node_a = self.graph.create_node("router")
        node_b = self.graph.create_node("host")
        edge = self.graph.add_edge(node_a, node_b, 100, 0.01)
        
        found_edge = self.graph.get_edge_between_nodes(node_a.id, node_b.id)
        self.assertEqual(found_edge, edge)
        
        node_c = self.graph.create_node("host")
        not_found = self.graph.get_edge_between_nodes(node_a.id, node_c.id)
        self.assertIsNone(not_found)
    
    def test_id_managers(self):
        node_id1 = node_id_manager()
        node_id2 = node_id_manager()
        self.assertEqual(node_id2, node_id1 + 1)
        
        edge_id1 = edge_id_manager()
        edge_id2 = edge_id_manager()
        self.assertEqual(edge_id2, edge_id1 + 1)
        
        packet_id1 = packet_id_manager() 
        packet_id2 = packet_id_manager()
        self.assertEqual(packet_id2, packet_id1 + 1)

if __name__ == '__main__':
    unittest.main()
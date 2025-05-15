import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routing_alg.wcett_lb_post import update_congest_status
from network import Graph, BUFFER_SIZE

class TestWcettLBPost(unittest.TestCase):
    def setUp(self):
        self.network = Graph()
        
        self.node1 = self.network.create_node('IGW')
        self.node2 = self.network.create_node('MR')
        self.node3 = self.network.create_node('C')
        
        self.network.add_edge(self.node1, self.node2, 10, 0)
        self.network.add_edge(self.node1, self.node3, 10, 0)
    
    def test_update_congest_status_no_congestion(self):
        # Fill queue with some small number of items
        for _ in range(2):
            self.node1.queue.put("packet")
        
        update_congest_status(self.node1, self.network)
        
        assert self.node1.congest_status is False
        assert self.node1.load == 2
    
    def test_update_congest_status_congestion(self):
        # Fill queue with items at threshold
        for _ in range(BUFFER_SIZE):
            self.node1.queue.put("packet")
        
        update_congest_status(self.node1, self.network)
        
        assert self.node1.congest_status is True
        assert self.node1.load == BUFFER_SIZE

if __name__ == '__main__':
    unittest.main()
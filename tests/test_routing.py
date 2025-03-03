import sys
import os

# Add the parent directory (project root) to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import Mock, patch
import routing.routing as routing

# file: routing.py

# Import the function to test

class TestFindAllPaths(unittest.TestCase):
    def setUp(self):
        # Create mock network for testing
        self.mock_network = Mock()
        self.mock_network.nodes = {}
        
        # Create mock nodes
        for i in range(1, 6):
            node = Mock()
            node.neighbors = []
            self.mock_network.nodes[i] = node

    def test_same_source_and_destination(self):
        """Test when source and destination are the same."""
        paths = routing.find_all_paths(self.mock_network, 1, 1)
        self.assertEqual(paths, [[1]])
    
    def test_direct_path(self):
        """Test a direct path between two nodes."""
        # Set up a direct path from 1 to 2
        self.mock_network.nodes[1].neighbors = [2]
        
        mock_edge = Mock()
        mock_edge.active = True
        self.mock_network.get_edge_between_nodes = Mock(return_value=mock_edge)
        
        # Mock the recursive call to return the expected result
        with patch('routing.routing.find_all_paths', 
                  side_effect=lambda nw, src, dst, path=None, visited=None, max_d=None: 
                      [[2]] if src == 2 and dst == 2 else []):
            
            paths = routing.find_all_paths(self.mock_network, 1, 2)
            self.assertEqual(paths, [[1, 2]])
            
    def test_multiple_paths(self):
        """Test multiple paths between two nodes."""
        # Set up a network with multiple paths
        # 1 -> 2 -> 4
        # 1 -> 3 -> 4
        self.mock_network.nodes[1].neighbors = [2, 3]
        self.mock_network.nodes[2].neighbors = [4]
        self.mock_network.nodes[3].neighbors = [4]
        
        # All edges are active
        mock_edge = Mock()
        mock_edge.active = True
        self.mock_network.get_edge_between_nodes = Mock(return_value=mock_edge)
        
        # Mock the recursive calls
        def mock_find_all_paths(nw, src, dst, path=None, visited=None, max_d=None):
            if src == 2 and dst == 4:
                return [[2, 4]]
            elif src == 3 and dst == 4:
                return [[3, 4]]
            elif src == 4 and dst == 4:
                return [[4]]
            return []
            
        with patch('routing.routing.find_all_paths', side_effect=mock_find_all_paths):
            paths = routing.find_all_paths(self.mock_network, 1, 4)
            # We should get two paths: [1,2,4] and [1,3,4]
            self.assertEqual(len(paths), 2)
            self.assertIn([1, 2, 4], paths)
            self.assertIn([1, 3, 4], paths)
    
    def test_no_path(self):
        """Test when there is no path between source and destination."""
        # No neighbors for node 1
        self.mock_network.nodes[1].neighbors = []
        
        paths = routing.find_all_paths(self.mock_network, 1, 5)
        self.assertEqual(paths, [])
    
    def test_inactive_edge(self):
        """Test when a potential path has an inactive edge."""
        self.mock_network.nodes[1].neighbors = [2]
        
        # Edge is inactive
        mock_edge = Mock()
        mock_edge.active = False
        self.mock_network.get_edge_between_nodes = Mock(return_value=mock_edge)
        
        paths = routing.find_all_paths(self.mock_network, 1, 2)
        self.assertEqual(paths, [])
    
    def test_max_depth_limit(self):
        """Test that max_depth prevents infinite loops in cyclic graphs."""
        # Create a cycle 1 -> 2 -> 3 -> 1
        self.mock_network.nodes[1].neighbors = [2]
        self.mock_network.nodes[2].neighbors = [3]
        self.mock_network.nodes[3].neighbors = [1]
        
        mock_edge = Mock()
        mock_edge.active = True
        self.mock_network.get_edge_between_nodes = Mock(return_value=mock_edge)
        
        # Set max_depth to 2 to prevent following the full cycle
        with patch('routing.routing.find_all_paths', 
                  side_effect=lambda nw, src, dst, path=None, visited=None, max_d=None: 
                      [] if len(path) > max_d else [[src]]):
            
            paths = routing.find_all_paths(self.mock_network, 1, 4, max_depth=2)
            self.assertEqual(paths, [])
    
    def test_visited_nodes_not_revisited(self):
        """Test that nodes are not revisited (prevents cycles)."""
        # Create a cycle 1 -> 2 -> 1
        self.mock_network.nodes[1].neighbors = [2]
        self.mock_network.nodes[2].neighbors = [1, 3]
        self.mock_network.nodes[3].neighbors = [4]
        
        mock_edge = Mock()
        mock_edge.active = True
        self.mock_network.get_edge_between_nodes = Mock(return_value=mock_edge)
        
        # Mock function to verify visited set works correctly
        def mock_find_all_paths(nw, src, dst, path=None, visited=None, max_d=None):
            if src == 2 and dst == 4:
                # Should only try path through 3, not back to 1
                return [[2, 3, 4]]
            elif src == 3 and dst == 4:
                return [[3, 4]]
            return []
            
        with patch('routing.routing.find_all_paths', side_effect=mock_find_all_paths):
            paths = routing.find_all_paths(self.mock_network, 1, 4)
            # We should get only one path [1,2,3,4] and not revisit 1
            self.assertEqual(len(paths), 1)
            self.assertEqual(paths[0], [1, 2, 3, 4])

if __name__ == '__main__':
    unittest.main()
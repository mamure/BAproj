import sys
import os
# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import routing.hop_count as hp
import routing.wcett as wcett
import network as nt

def find_all_paths(nw, src, dest, max_depth=10):
    path = [src]
    visited = set([src])
        
    if src == dest:
        return [path]
    if len(path) > max_depth:
        return []
    
    all_paths = []
    src_node = nw.nodes[src]
    
    for neighbor_id in src_node.neighbors:
        if neighbor_id not in visited:
            edge = nw.get_edge_between_nodes(src, neighbor_id)
            if edge and edge.active:
                
                new_visited = visited.copy()
                new_visited.add(neighbor_id)
                new_path = path + [neighbor_id]
                
                next_paths = find_all_paths(nw, neighbor_id, dest, new_path, new_visited, max_depth)
                all_paths.extend(next_paths)
                
    return all_paths

class RoutingProtocol:
    def compute_routing_tb(self, nw, src, dest):
        """
        Args:
            nw (Network): The network graph
            src (int): node_id for the source node
            dest (int): node_id for the destination node
        """
        raise NotImplementedError()

class HopCountRouting(RoutingProtocol):
    def compute_routing_tb(self, nw, src, dest):        
        routing_tb = hp.shortest_path(nw, src, dest)
        return routing_tb
    
class WCETTRouting(RoutingProtocol):
    def __init__(self, packet_sz=1024, beta=0.5):
        self.packet_sz = packet_sz
        self.beta = beta
        
    def compute_routing_tb(self, nw, src, dest):
        all_paths = find_all_paths(nw, src, dest)
        
        if not all_paths:
            return None
        
        weights = {}
        for path in all_paths:
            edges = []
            for i in range(len(path) - 1):
                edge = nw.get_edge_between_nodes(path[i], path[i+1])
                if edge:
                    edges.append(edge)
                    
            wcett_var = wcett.compute_wcett(edges, self.packet_sz, self.beta)
            weights[tuple(path)] = wcett_var
        
        best_path = min(weights, key=weights.get)
        return list(best_path)
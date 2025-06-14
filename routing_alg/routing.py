import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routing_alg import hop_count as hc
from routing_alg import wcett, wcett_lb_post, wcett_lb_pre
from routing_alg.routing_utils import find_all_paths, is_valid_path

class RoutingProtocol:
    def compute_routing_tb(self, nw, src_id, dest_id):
        """
        Args:
            nw (Network): The network graph
            src_id (int): node_id for the source node
            dest_id (int): node_id for the destination node
        """
        raise NotImplementedError()

class HopCountRouting(RoutingProtocol):
    def compute_routing_tb(self, nw, src_id, dest_id):
        if src_id == dest_id:
            return      
        routing_tb = hc.shortest_path(nw, src_id, dest_id)
        return routing_tb[1]
    
class WCETTRouting(RoutingProtocol):
    def __init__(self, packet_sz=1024, beta=0.5):
        self.packet_sz = packet_sz
        self.beta = beta
        
    def compute_routing_tb(self, nw, src_id, dest_id):
        all_paths = find_all_paths(nw, src_id, dest_id)
        # Filter out paths with client nodes as transit
        all_paths = [path for path in all_paths if is_valid_path(nw, path)]

        if not all_paths:
            return None
        
        weights = {}
        for path in all_paths:
            if len(path) < 2:
                continue

            edges = []
            for i in range(len(path) - 1):
                edge = nw.get_edge_between_nodes(path[i], path[i+1])
                if edge:
                    edges.append(edge)
                    
            if edges:
                wcett_temp = wcett.compute_wcett(edges, self.packet_sz, self.beta)
                weights[tuple(path)] = wcett_temp

        if not weights:
            return None

        best_path = min(weights, key=weights.get)
        if best_path and len(best_path) >= 2:
            return best_path[1]
        return None

class WCETT_LB_POSTRouting(RoutingProtocol):
    def __init__(self, packet_sz=1024, beta=0.5):
        self.packet_sz = packet_sz
        self.beta = beta
        self.path_cache = {}
        
    def compute_routing_tb(self, nw, src, dest):
        all_paths = find_all_paths(nw, src, dest)
        if not all_paths:
            return None
        
        path_metrics = []
        
        for path in all_paths:
            if len(path) < 2:
                continue

            edges = []
            for i in range(len(path) - 1):
                edge = nw.get_edge_between_nodes(path[i], path[i+1])
                if edge:
                    edges.append(edge)
                    
            if edges:
                metric = wcett_lb_post.compute_wcett_lb(edges, self.packet_sz, nw, path)
                path_metrics.append((path, metric))

        if not path_metrics:
            return None
        
        path_metrics.sort(key=lambda x: (x[1]))
        
        best_path = path_metrics[0][0]
        
        self.path_cache[(src, dest)] = best_path
        
        if best_path and len(best_path) >= 2:
            return best_path[1]
        return None

class WCETT_LB_PRERouting(RoutingProtocol):
    def __init__(self, packet_sz=1024, beta=0.5):
        self.packet_sz = packet_sz
        self.beta = beta
        self.path_cache = {}
        
    def compute_routing_tb(self, nw, src, dest):
        all_paths = find_all_paths(nw, src, dest)
        # Filter out paths with client nodes as transit
        all_paths = [path for path in all_paths if is_valid_path(nw, path)]
        if not all_paths:
            return None
        
        path_metrics = []
        
        for path in all_paths:
            if len(path) < 2:
                continue

            edges = []
            for i in range(len(path) - 1):
                edge = nw.get_edge_between_nodes(path[i], path[i+1])
                if edge:
                    edges.append(edge)
                    
            if edges:
                metric = wcett_lb_pre.compute_wcett_lb(edges, self.packet_sz, nw, path)
                path_metrics.append((path, metric))

        if not path_metrics:
            return None
        
        path_metrics.sort(key=lambda x: (x[1]))
        
        best_path = path_metrics[0][0]
        
        self.path_cache[(src, dest)] = best_path
        
        if best_path and len(best_path) >= 2:
            return best_path[1]
        return None
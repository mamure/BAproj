from routing_alg import hop_count as hc
from routing_alg import wcett
from routing_alg import wcett_lb_post
from routing_alg import wcett_lb_pre

def find_all_paths(nw, src, dest, path=None, visited=None, max_depth=10):
    if path is None:
        path = [src]
    if visited is None:
        visited = set([src])
        
    if src == dest:
        return [path]
    if len(path) > max_depth:
        return []
    
    all_paths = []
    src_node = nw.nodes[src]
    
    for neighbor_id in src_node.neighbors:
        if neighbor_id not in visited:
            neighbor_node = nw.nodes[neighbor_id]
            if neighbor_node.type == "C" and neighbor_id != dest:
                continue
            edge = nw.get_edge_between_nodes(src, neighbor_id)
            if edge and edge.active:
                
                new_visited = visited.copy()
                new_visited.add(neighbor_id)
                new_path = path + [neighbor_id]
                
                next_paths = find_all_paths(nw, neighbor_id, dest, new_path, new_visited, max_depth)
                all_paths.extend(next_paths)
                
    return all_paths

def is_valid_path(nw, path):
    if len(path) <= 2:
        return True
        
    for node_id in path[1:-1]:
        node = nw.nodes[node_id]
        if node.type == "C":  # Client nodes can't be transit nodes
            return False
            
    return True

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
    
    def alternative_path(self, nw, src, dest, non_nodes):
        all_paths = find_all_paths(nw, src, dest)
        # Filter out paths with client nodes as transit
        all_paths = [path for path in all_paths if is_valid_path(nw, path)]
        
        valid_paths = []
        
        for path in all_paths:
            if not any(node_id in non_nodes for node_id in path[1:-1]):
                valid_paths.append(path)
        
        if not valid_paths:
            return None
        
        path_metrics = []
        for path in valid_paths:
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
        
        path_metrics.sort(key=lambda x: x[1])
        return path_metrics[0][0]

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
    
    def alternative_path(self, nw, src, dest, non_nodes):
        all_paths = find_all_paths(nw, src, dest)
        # Filter out paths with client nodes as transit
        all_paths = [path for path in all_paths if is_valid_path(nw, path)]
        valid_paths = []
        
        for path in all_paths:
            if not any(node_id in non_nodes for node_id in path[1:-1]):
                valid_paths.append(path)
        
        if not valid_paths:
            return None
        
        path_metrics = []
        for path in valid_paths:
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
        
        path_metrics.sort(key=lambda x: x[1])
        return path_metrics[0][0]
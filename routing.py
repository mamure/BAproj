from routing_alg import hop_count as hc
from routing_alg import wcett
# from routing_alg import wcett_lb

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
    def compute_routing_tb(self, nw, src_id, dest_id):        
        routing_tb = hc.shortest_path(nw, src_id, dest_id)
        return routing_tb
    
class WCETTRouting(RoutingProtocol):
    def __init__(self, packet_sz=1024, beta=0.5):
        self.packet_sz = packet_sz
        self.beta = beta
        
    def compute_routing_tb(self, nw, src_id, dest_id):
        all_paths = find_all_paths(nw, src_id, dest_id)

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
        return best_path
    
# class WCETT_LBRouting(RoutingProtocol):
#     def __init__(self):
#         super().__init__()
    
#     def compute_routing_tb(self, nw, src, dest):
#         return super().compute_routing_tb(nw, src, dest)
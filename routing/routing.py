import hop_count as hp

class RoutingProtocol:
    def compute_routing_tb(self, nw, src, dst):
        """
        Args:
            nw (Network): The network graph
            src (int): node_id for the source node
            dst (int): node_id for the destination node
        """
        raise NotImplementedError()

class HopCountRouting(RoutingProtocol):
    def compute_routing_tb(self, nw, src, dst):        
        routing_tb = hp.shortest_path(nw, src, dst)
        return routing_tb
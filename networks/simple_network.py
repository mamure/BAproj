import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import network as nt
import visualiser as vis

def initialize_simple_network():
    """
    Creates a simple line network.
    The routers are connected in a line-like manner, and clients are attached to the "last" router.
    
    Returns:
        Network: A Network object containing all nodes and edges.
    """
    network = nt.Graph()
    igw = network.create_node("IGW")
    ap1 = network.create_node("AP")
    ap2 = network.create_node("AP")
    c = network.create_node("C")
    
    network.add_edge(igw, ap1, 1, 0.5)
    network.add_edge(ap1, ap2, 1, 0.5)
    network.add_edge(ap2, c, 1, 0.5)
    
    return network
    
if __name__ == "__main__":
    network = initialize_simple_network()
    vis.visualize_network(network, "simple")
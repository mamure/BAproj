import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import network as nt
import visualiser as vis

def initialize_network():
    """
    Creates a network with strategic bottlenecks and diverse link characteristics
    to better demonstrate load balancing algorithms.
    
    Returns:
        Network: A Network object containing all nodes and edges.
    """
    network = nt.Graph()

    igw = network.create_node("IGW")
    mr1 = network.create_node("MR")
    mr2 = network.create_node("MR")
    mr3 = network.create_node("MR")
    mr4 = network.create_node("MR")
    mr5 = network.create_node("MR")
    mr6 = network.create_node("MR")
    c7 = network.create_node("C")
    c8 = network.create_node("C")
    c9 = network.create_node("C")
    c10 = network.create_node("C")
    c11 = network.create_node("C")
    c12 = network.create_node("C")
    

    network.add_edge(igw, mr1, 200, 0.01)
    network.add_edge(igw, mr2, 180, 0.015)
    network.add_edge(igw, mr3, 120, 0.02)

    network.add_edge(mr1, mr4, 90, 0.04)
    network.add_edge(mr4, mr5, 80, 0.05)
    network.add_edge(mr5, mr6, 120, 0.03)
    network.add_edge(mr1, mr2, 75, 0.05)
    network.add_edge(mr2, mr5, 25, 0.25)
    network.add_edge(mr2, mr3, 65, 0.08)
    network.add_edge(mr3, mr6, 30, 0.15)

    network.add_edge(c7, mr1, 40, 0.15)
    network.add_edge(c7, mr4, 45, 0.18)
    network.add_edge(c8, mr1, 38, 0.12)
    network.add_edge(c8, mr5, 60, 0.20)
    network.add_edge(c9, mr4, 50, 0.15)
    network.add_edge(c10, mr6, 30, 0.12)
    network.add_edge(c10, mr5, 35, 0.20)
    network.add_edge(c11, mr3, 40, 0.15)
    network.add_edge(c11, mr6, 60, 0.18)
    network.add_edge(c12, mr3, 42, 0.15)

    return network
    
if __name__ == "__main__":
    network = initialize_network()
    vis.visualize_network(network, "complex")

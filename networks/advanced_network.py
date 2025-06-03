import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import network as nt
import visualiser as vis

def initialize_network():
    """
    Creates a larger network with strategic bottlenecks and diverse link
    characteristics to showcase load balancing benefits.
    
    Returns:
        Network: A Network object containing all nodes and edges.
    """
    network = nt.Graph()

    igw0 = network.create_node("IGW")
    igw1 = network.create_node("IGW")
    mr2 = network.create_node("MR")
    mr3 = network.create_node("MR")
    mr4 = network.create_node("MR")
    mr5 = network.create_node("MR")
    mr6 = network.create_node("MR")
    mr7 = network.create_node("MR")
    mr8 = network.create_node("MR")
    mr9 = network.create_node("MR")
    mr10 = network.create_node("MR")
    mr11 = network.create_node("MR")
    c12 = network.create_node("C")
    c13 = network.create_node("C")
    c14 = network.create_node("C")
    c15 = network.create_node("C")
    c16 = network.create_node("C")
    c17 = network.create_node("C")

    network.add_edge(igw0, igw1, 350, 0.01)
    
    network.add_edge(igw0, mr2, 180, 0.02)
    network.add_edge(igw0, mr3, 220, 0.02)
    network.add_edge(igw1, mr3, 200, 0.02)
    network.add_edge(igw1, mr4, 40, 0.12)
    network.add_edge(igw1, mr5, 190, 0.03)
    
    network.add_edge(mr2, mr3, 180, 0.03)
    network.add_edge(mr2, mr6, 120, 0.05)
    network.add_edge(mr3, mr4, 100, 0.05)
    network.add_edge(mr3, mr6, 160, 0.15)
    network.add_edge(mr4, mr5, 130, 0.04)
    network.add_edge(mr4, mr7, 60, 0.06)
    network.add_edge(mr4, mr8, 50, 0.08)
    network.add_edge(mr4, mr9, 35, 0.10)
    network.add_edge(mr6, mr7, 25, 0.08)
    network.add_edge(mr6, mr10, 180, 0.06)
    network.add_edge(mr7, mr8, 140, 0.05)
    network.add_edge(mr8, mr10, 160, 0.04)
    network.add_edge(mr8, mr11, 140, 0.06)
    network.add_edge(mr9, mr11, 150, 0.05)

    network.add_edge(c12, mr2, 80, 0.15)
    network.add_edge(c12, mr6, 85, 0.18)
    network.add_edge(c13, mr6, 75, 0.15)
    network.add_edge(c13, mr10, 90, 0.20)
    network.add_edge(c14, mr10, 85, 0.15)
    network.add_edge(c14, mr7, 70, 0.18)
    network.add_edge(c14, mr8, 80, 0.15)
    network.add_edge(c15, mr10, 80, 0.16)
    network.add_edge(c15, mr8, 75, 0.14)
    network.add_edge(c15, mr11, 85, 0.17)
    network.add_edge(c16, mr11, 80, 0.15)
    network.add_edge(c16, mr9, 75, 0.16)
    network.add_edge(c17, mr9, 80, 0.15)
    network.add_edge(c17, mr5, 90, 0.18)

    return network
    
if __name__ == "__main__":
    network = initialize_network()
    vis.visualize_network(network, "advanced")

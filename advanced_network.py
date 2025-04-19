import network as nt
import visualiser as vis
import random as rnd

def initialize_network():
    """
    Creates a network with:
    - x Internet Gateway nodes (IGWs)
    - y Mesh Routers (MRs)
    - z Clients
    The routers are interconnected in a mesh-like manner, and clients are attached to routers.
    
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
    
    network.add_edge(igw0, igw1, 100, rnd.uniform(0.3,0.6))
    
    network.add_edge(igw0, mr2, 50, rnd.uniform(0.3,0.6))
    network.add_edge(igw0, mr3, 30, rnd.uniform(0.3,0.6))
    network.add_edge(igw1, mr3, 20, rnd.uniform(0.3,0.6))
    network.add_edge(igw1, mr4, 10, rnd.uniform(0.3,0.6))
    network.add_edge(igw1, mr5, 50, rnd.uniform(0.3,0.6))
    
    network.add_edge(mr2, mr3, 20, rnd.uniform(0.3,0.6))
    network.add_edge(mr2, mr6, 30, rnd.uniform(0.3,0.6))
    network.add_edge(mr3, mr4, 30, rnd.uniform(0.3,0.6))
    network.add_edge(mr3, mr6, 40, rnd.uniform(0.3,0.6))
    network.add_edge(mr4, mr5, 20, rnd.uniform(0.3,0.6))
    network.add_edge(mr4, mr7, 20, rnd.uniform(0.3,0.6))
    network.add_edge(mr4, mr8, 20, rnd.uniform(0.3,0.6))
    network.add_edge(mr5, mr9, 10, rnd.uniform(0.3,0.6))
    network.add_edge(mr6, mr7, 40, rnd.uniform(0.3,0.6))
    network.add_edge(mr6, mr10, 10, rnd.uniform(0.3,0.6))
    network.add_edge(mr7, mr8, 40, rnd.uniform(0.3,0.6))
    network.add_edge(mr8, mr10, 10, rnd.uniform(0.3,0.6))
    network.add_edge(mr8, mr11, 20, rnd.uniform(0.3,0.6))
    network.add_edge(mr9, mr11, 40, rnd.uniform(0.3,0.6))
    
    network.add_edge(c12, mr2, 10, rnd.uniform(0.3,0.6))
    network.add_edge(c12, mr6, 30, rnd.uniform(0.3,0.6))
    network.add_edge(c13, mr6, 20, rnd.uniform(0.3,0.6))
    network.add_edge(c13, mr10, 30, rnd.uniform(0.3,0.6))
    network.add_edge(c14, mr10, 30, rnd.uniform(0.3,0.6))
    network.add_edge(c14, mr7, 10, rnd.uniform(0.3,0.6))
    network.add_edge(c14, mr8, 20, rnd.uniform(0.3,0.6))
    network.add_edge(c15, mr10, 20, rnd.uniform(0.3,0.6))
    network.add_edge(c15, mr8, 40, rnd.uniform(0.3,0.6))
    network.add_edge(c15, mr11, 30, rnd.uniform(0.3,0.6))
    network.add_edge(c16, mr11, 20, rnd.uniform(0.3,0.6))
    network.add_edge(c16, mr9, 30, rnd.uniform(0.3,0.6))
    network.add_edge(c17, mr9, 40, rnd.uniform(0.3,0.6))
    network.add_edge(c17, mr5, 20, rnd.uniform(0.3,0.6))

    return network
    
if __name__ == "__main__":
    network = initialize_network()
    vis.visualize_network(network)

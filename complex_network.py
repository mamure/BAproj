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
    
    Args:
        x (int): Number of IGWs.
        y (int): Number of MRs.
        z (int): Number of Clients.
    
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
    
    network.add_edge(igw, mr1, 40, rnd.uniform(0.1,0.4))
    network.add_edge(igw, mr3, 50, rnd.uniform(0.1,0.4))
    network.add_edge(igw, mr4, 30, rnd.uniform(0.1,0.4))
    
    network.add_edge(mr1, mr5, 30, rnd.uniform(0.1,0.4))
    network.add_edge(mr2, mr5, 50, rnd.uniform(0.1,0.4))
    network.add_edge(mr2, mr3, 40, rnd.uniform(0.1,0.4))
    network.add_edge(mr2, mr6, 60, rnd.uniform(0.1,0.4))
    
    network.add_edge(c7, mr3, 25, rnd.uniform(0.1,0.4))
    network.add_edge(c7, mr2, 55, rnd.uniform(0.1,0.4))
    network.add_edge(c8, mr1, 35, rnd.uniform(0.1,0.4))
    network.add_edge(c8, mr2, 55, rnd.uniform(0.1,0.4))
    network.add_edge(c9, mr5, 45, rnd.uniform(0.1,0.4))
    network.add_edge(c10, mr1, 35, rnd.uniform(0.1,0.4))
    network.add_edge(c10, mr5, 45, rnd.uniform(0.1,0.4))
    network.add_edge(c11, mr1, 35, rnd.uniform(0.1,0.4))
    network.add_edge(c11, mr4, 35, rnd.uniform(0.1,0.4))
    network.add_edge(c12, mr6, 65, rnd.uniform(0.1,0.4))
    network.add_edge(c12, mr4, 35, rnd.uniform(0.1,0.4))

    return network
    
if __name__ == "__main__":
    network = initialize_network()
    vis.visualize_network(network)

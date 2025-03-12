import network as nt
import visualiser as vis

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
    c13 = network.create_node("C")
    c14 = network.create_node("C")
    c15 = network.create_node("C")
    
    network.add_edge(igw, mr1, 1, 0)
    network.add_edge(igw, mr2, 1, 0)
    network.add_edge(igw, mr3, 1, 0)
    
    network.add_edge(mr1, mr4, 1, 0)
    network.add_edge(mr1, mr6, 1, 0)
    network.add_edge(mr2, mr4, 1, 0)
    network.add_edge(mr2, mr5, 1, 0)
    network.add_edge(mr3, mr5, 1, 0)
    
    network.add_edge(c7, mr5, 1, 0)
    network.add_edge(c7, mr6, 1, 0)
    network.add_edge(c8, mr3, 1, 0)
    network.add_edge(c8, mr5, 1, 0)
    network.add_edge(c9, mr3, 1, 0)
    network.add_edge(c10, mr2, 1, 0)
    network.add_edge(c10, mr3, 1, 0)
    network.add_edge(c10, mr5, 1, 0)
    network.add_edge(c11, mr4, 1, 0)
    network.add_edge(c11, mr6, 1, 0)
    network.add_edge(c12, mr1, 1, 0)
    network.add_edge(c12, mr2, 1, 0)
    network.add_edge(c13, mr6, 1, 0)
    network.add_edge(c14, mr2, 1, 0)
    network.add_edge(c14, mr4, 1, 0)
    network.add_edge(c14, mr5, 1, 0)
    network.add_edge(c15, mr4, 1, 0)
    network.add_edge(c15, mr5, 1, 0)

    return network
    
if __name__ == "__main__":
    network = initialize_network()
    vis.visualize_network(network)

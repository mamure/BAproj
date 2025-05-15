import network as nt
import visualiser as vis

def initialize_network():
    """
    Creates a network with:
    - Internet Gateway nodes (IGWs)
    - Mesh Routers (MRs)
    - Clients (C)
    The routers are interconnected in a mesh-like manner, and clients are attached to routers.
    
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
    
    network.add_edge(igw, mr1, 20, 0.1)
    network.add_edge(igw, mr3, 60, 0.1)
    network.add_edge(igw, mr4, 40, 0.1)

    network.add_edge(mr1, mr5, 20, 0.1)
    network.add_edge(mr2, mr5, 150, 0.1)
    network.add_edge(mr2, mr3, 150, 0.1)
    network.add_edge(mr2, mr6, 70, 0.1)
    network.add_edge(mr4, mr6, 5, 0.1)

    network.add_edge(c7, mr6, 35, 0.1)
    network.add_edge(c7, mr2, 180, 0.1)
    network.add_edge(c8, mr1, 45, 0.1)
    network.add_edge(c8, mr2, 180, 0.1)
    network.add_edge(c9, mr5, 55, 0.1)
    network.add_edge(c10, mr1, 45, 0.1)
    network.add_edge(c10, mr5, 55, 0.1)
    network.add_edge(c11, mr4, 45, 0.1)
    network.add_edge(c12, mr6, 75, 0.1)
    network.add_edge(c12, mr4, 45, 0.1)

    return network
    
if __name__ == "__main__":
    network = initialize_network()
    vis.visualize_network(network)

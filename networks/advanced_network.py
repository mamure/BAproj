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
    
    network.add_edge(igw0, igw1, 300, 0.1)
    
    network.add_edge(igw0, mr2, 10, 0.1)
    network.add_edge(igw0, mr3, 200, 0.1)
    network.add_edge(igw1, mr3, 180, 0.1)
    network.add_edge(igw1, mr4, 50, 0.1)
    network.add_edge(igw1, mr5, 180, 0.1)
    
    network.add_edge(mr2, mr3, 10, 0.1)
    network.add_edge(mr2, mr6, 50, 0.1)
    network.add_edge(mr3, mr4, 50, 0.1)
    network.add_edge(mr3, mr6, 180, 0.1)
    network.add_edge(mr4, mr5, 40, 0.1)
    network.add_edge(mr4, mr7, 40, 0.1)
    network.add_edge(mr4, mr8, 40, 0.1)
    network.add_edge(mr4, mr9, 40, 0.1)
    network.add_edge(mr6, mr7, 180, 0.1)
    network.add_edge(mr6, mr10, 200, 0.1)
    network.add_edge(mr7, mr8, 200, 0.1)
    network.add_edge(mr8, mr10, 180, 0.1)
    network.add_edge(mr8, mr11, 200, 0.1)
    network.add_edge(mr9, mr11, 180, 0.1)

    network.add_edge(c12, mr2, 100, 0.1)
    network.add_edge(c12, mr6, 100, 0.1)
    network.add_edge(c13, mr6, 100, 0.1)
    network.add_edge(c13, mr10, 140, 0.1)
    network.add_edge(c14, mr10, 100, 0.1)
    network.add_edge(c14, mr7, 110, 0.1)
    network.add_edge(c14, mr8, 100, 0.1)
    network.add_edge(c15, mr10, 100, 0.1)
    network.add_edge(c15, mr8, 100, 0.1)
    network.add_edge(c15, mr11, 100, 0.1)
    network.add_edge(c16, mr11, 100, 0.1)
    network.add_edge(c16, mr9, 100, 0.1)
    network.add_edge(c17, mr9, 100, 0.1)
    network.add_edge(c17, mr5, 130, 0.1)

    return network
    
if __name__ == "__main__":
    network = initialize_network()
    vis.visualize_network(network)

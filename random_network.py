import random as rnd
import network as nt
import visualiser as vis

def initialize_network(x, y, z):
    """
    Creates a network with:
    - x Internet Gateway nodes (IGWs)
    - y Routers (APs)
    - z Clients
    The routers are interconnected in a mesh-like manner, and clients are attached to routers.
    
    Args:
        x (int): Number of IGWs.
        y (int): Number of APs.
        z (int): Number of Clients.
    
    Returns:
        Network: A Network object containing all nodes and edges.
    """
    network = nt.Graph()

    igws = [network.create_node("IGW") for _ in range(x)]

    routers = [network.create_node("AP") for _ in range(y)]

    clients = [network.create_node("C") for _ in range(z)]

    for igw in igws:
        num_connections = 3
        connected_routers = rnd.sample(routers, num_connections)
        for router in connected_routers:
            network.add_edge(igw, router, rnd.uniform(30,100), rnd.uniform(0.1,0.9))

    for i in range(len(routers)):
        for j in range(i + 1, len(routers)):
            if rnd.random() < 0.5:
                network.add_edge(routers[i], routers[j], rnd.uniform(20, 100), rnd.uniform(0.1,0.9))

    for client in clients:
        num_connections = rnd.randint(1, min(3, len(routers)))  # Each client connects to 1-3 routers
        connected_routers = rnd.sample(routers, num_connections)
        for router in connected_routers:
            network.add_edge(client, router, rnd.uniform(10, 80), rnd.uniform(0.1,0.9))

    return network
    
if __name__ == "__main__":
    x = 1  # Number of IGWs
    y = 6  # Number of Routers
    z = 20 # Number of Clients

    network = initialize_network(x, y, z)
    vis.visualize_network(network)

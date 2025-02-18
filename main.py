import random as rnd
import network as nt
import hop_count as hc

def initialize_network(x, y, z):
    """
    Creates a network with:
    - x Internet Gateway nodes (IGWs)
    - y Routers
    - z Clients
    The routers are interconnected in a mesh-like manner, and clients are attached to routers.
    
    Args:
        x (int): Number of IGWs (Internet Gateways).
        y (int): Number of Routers.
        z (int): Number of Clients.
    
    Returns:
        Network: A Network object containing all nodes and edges.
    """
    network = nt.Graph()

    # Create IGW nodes
    igws = [network.create_node("IGW") for _ in range(x)]

    # Create Router nodes
    routers = [network.create_node("Router") for _ in range(y)]

    # Create Client nodes
    clients = [network.create_node("Client") for _ in range(z)]

    # Connect IGWs to Routers (Each IGW connects to multiple routers)
    for igw in igws:
        num_connections = max(1, y // x)  # Distribute routers evenly across IGWs
        connected_routers = rnd.sample(routers, num_connections)
        for router in connected_routers:
            network.add_edge(igw, router, rnd.uniform(50, 100))

    # Connect Routers in a Mesh-like Topology
    for i in range(len(routers)):
        for j in range(i + 1, len(routers)):
            if rnd.random() < 0.5:  # Randomly decide connections to avoid full mesh
                network.add_edge(routers[i], routers[j], rnd.uniform(20, 80))

    # Assign Clients to Routers
    for client in clients:
        assigned_router = rnd.choice(routers)  # Each client connects to a random router
        network.add_edge(client, assigned_router, rnd.uniform(10, 50))

    return network

if __name__ == "__main__":
    x = 2  # Number of IGWs
    y = 10  # Number of Routers
    z = 50 # Number of Clients

    network = initialize_network(x, y, z)
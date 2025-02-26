import random as rnd
import network as nt
from pyvis.network import Network as pyNT
import os

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
        num_connections = max(1, y // x)
        connected_routers = rnd.sample(routers, num_connections)
        for router in connected_routers:
            network.add_edge(igw, router, rnd.uniform(20,100), rnd.uniform(0.1,0.9))

    for i in range(len(routers)):
        for j in range(i + 1, len(routers)):
            if rnd.random() < 0.5:
                network.add_edge(routers[i], routers[j], rnd.uniform(20, 100), rnd.uniform(0.1,0.9))

    for client in clients:
        num_connections = rnd.randint(1, min(4, len(routers)))  # Each client connects to 1-4 routers
        connected_routers = rnd.sample(routers, num_connections)
        for router in connected_routers:
            network.add_edge(client, router, rnd.uniform(10, 80), rnd.uniform(0.1,0.9))

    return network

def visualize_network(network):
    net = pyNT(height='750px', width='100%', bgcolor='#272A32', font_color='white')

    # Define colors for node types
    node_colors = {
        "IGW": "red",
        "AP": "blue",
        "C": "green"
    }
    
    for node_id, node in network.nodes.items():
        color = node_colors.get(node.type)
        net.add_node(node_id, label=f"Node {node_id}", title=f"Type: {node.type}", color=color)

    # Add edges
    for edge_id, edge in network.edges.items():
        net.add_edge(edge.src.id, edge.dst.id, title=f"Bandwidth: {edge.bandwidth:.2f} Mbps, Loss Rate: {edge.loss_rate:.2f}")
    
    # Ensure output directory exists
    output_dir = "html_vis"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save the visualization
    output_path = os.path.join(output_dir, "complex_graph.html")
    net.write_html(output_path)
    print(f"Network graph saved at '{output_path}'. Open it in your browser to view.")
    
if __name__ == "__main__":
    x = 2  # Number of IGWs
    y = 10  # Number of Routers
    z = 50 # Number of Clients

    network = initialize_network(x, y, z)
    visualize_network(network)

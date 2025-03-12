import network as nt
from pyvis.network import Network as pyNT
import os
import routing

def initialize_simple_network():
    """
    Creates a simple line network.
    The routers are connected in a line-like manner, and clients are attached to the "last" router.
    
    Args:
        x (int): Number of IGWs.
        y (int): Number of APs.
        z (int): Number of Clients.
    
    Returns:
        Network: A Network object containing all nodes and edges.
    """
    network = nt.Graph()
    igw = network.create_node("IGW")
    ap1 = network.create_node("AP")
    ap2 = network.create_node("AP")
    c = network.create_node("C")
    
    network.add_edge(igw, ap1, 1, 0.5)
    network.add_edge(ap1, ap2, 1, 0.5)
    network.add_edge(ap2, c, 1, 0.5)
    
    return network, igw, c

def visualize_network(network):
    net = pyNT(height='750px', width='100%', bgcolor='#272A32', font_color='white')

    node_colors = {
        "IGW": "red",
        "AP": "blue",
        "C": "green"
    }
    
    for node_id, node in network.nodes.items():
        color = node_colors.get(node.type)
        net.add_node(node_id, label=f"Node {node_id}", title=f"Type: {node.type}", color=color)

    for edge_id, edge in network.edges.items():
        net.add_edge(edge.src.id, edge.dst.id, title=f"Bandwidth: {edge.bandwidth:.2f} Mbps, Loss Rate: {edge.loss_rate:.2f}")
    
    output_dir = "html_vis"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save the visualization
    output_path = os.path.join(output_dir, "simple_graph.html")
    net.write_html(output_path)
    print(f"Network graph saved at '{output_path}'. Open it in your browser to view.")
    
if __name__ == "__main__":
    network, igw, c = initialize_simple_network()
    test = routing.WCETTRouting()
    visualize_network(network)
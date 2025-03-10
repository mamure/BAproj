from pyvis.network import Network as pyNT
import os

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
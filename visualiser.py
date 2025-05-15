from pyvis.network import Network as pyNT
import os

def visualize_network(network):
    """
    Create an interactive visualization of a network topology.
    
    This function takes a network object, extracts its nodes and edges, and generates
    an interactive HTML visualization using the pyvis library. The visualization uses
    color coding to distinguish between different node types (IGW, AP, C) and displays
    relevant information about nodes and edges when hovering over them.
    
    Args:
        network (Graph): A network graph object containing nodes and edges.
    """
    net = pyNT(height='750px', width='100%', bgcolor='#272A32', font_color='white')

    node_colors = {
        "IGW": "red",
        "AP": "blue",
        "C": "green"
    }
    
    # Add nodes to the visualization
    for node_id, node in network.nodes.items():
        color = node_colors.get(node.type)
        net.add_node(
            node_id, 
            label=f"Node {node_id}", 
            title=f"Type: {node.type}", 
            color=color
        )

    # Add edges to the visualization with bandwidth and loss rate information
    for edge_id, edge in network.edges.items():
        net.add_edge(
            edge.src.id, 
            edge.dest.id, 
            title=f"Bandwidth: {edge.bandwidth:.2f} Mbps, Loss Rate: {edge.loss_rate:.2f}"
        )
    
    output_dir = "html_vis"
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "graph.html")
    net.write_html(output_path)
    print(f"Network graph saved at '{output_path}'. Open it in your browser to view.")
def compute_ett(edge, packet_sz):
    """Calculates Expected Transmission Time (ETT) for a given edge and packet size

    Args:
        edge (Edge): Network edge object containing loss_rate and bandwidth attributes
        packet_sz (int): Size of the packet in bytes

    Returns:
        float: The Expected Transmission Time value
    """
    loss_rate = edge.loss_rate
    p = 1 - (1 - loss_rate) * (1 - loss_rate)
    etx = 1 / (1 - p)
    
    # Convert bandwidth from Mbps to bytes/sec
    bandwidth_bps = edge.bandwidth * 125000
    
    ett = etx * (packet_sz / bandwidth_bps)
    return ett

def compute_wcett(edges, packet_sz, beta = 0.5):
    """Calculates the Weighted Cumulative ETT (WCETT) metric for a path

    Args:
        edges (list): List of Edge objects representing a path
        packet_sz (int): Size of the packet in bytes
        beta (float, optional): Weighting parameter balancing channel diversity. Defaults to 0.5.

    Returns:
        float: The WCETT metric value for the path
    """
    ett_sum = 0
    max_ett_channel = {}
    for edge in edges:
        ett_var = compute_ett(edge, packet_sz)
        ett_sum += ett_var
        
        channel = edge.channel
        max_ett_channel[channel] = max_ett_channel.get(channel, 0) + ett_var
    max_channel_ett = max(max_ett_channel.values())
    
    wcett = (1 - beta) * ett_sum + beta * max_channel_ett
    
    return wcett
def compute_ett(edge, packet_sz):
    loss_rate = edge.loss_rate
    etx = 1 / ((1 - loss_rate) * (1 - loss_rate))
    ett = etx * (packet_sz / edge.bandwidth)
    return ett

def compute_wcett(edges, packet_sz, beta = 0.5):
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
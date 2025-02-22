import time

def ett(edge, packet_sz):
    loss_rate = edge.loss_rate
    etx = 1 / ((1 - loss_rate) * (1 - loss_rate))
    ett = (etx * packet_sz) / edge.bandwidth
    return ett

# def compute_wcett(edges, packet_sz, beta = 0.5):
#     for edge in edges:
#         ett = ett(edge, packet_sz)
#         ett_sum += ett
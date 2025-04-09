import random as rnd
import time

class Packet:
    def __init__(self, packet_id, src_id, dest_id, size, packet_type="DATA", priority=1):
        """
        Args:
            src (int)
            dest (int)
            size (int)
            packet_type (str, optional): Defaults to "DATA".
        """
        self.id = packet_id
        self.src_id = src_id
        self.dest_id = dest_id
        self.size = size
        self.type = packet_type
        self.time = time.time()
        self.route_taken = []
        self.priority = priority # 1=low, 3=high
        
    def add_hop(self, node_id):
        self.route_taken.append(node_id)
    
    def create_ack(self):
        return Packet(self.dest,self.src, None, "ACK")
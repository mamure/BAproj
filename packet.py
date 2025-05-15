import time

class Packet:
    def __init__(self, packet_id, src_id, dest_id, size, packet_type="DATA"):
        """
        Args:
            src (int)
            dest (int)
            size (int): In bytes
            packet_type (str, optional): Defaults to "DATA".
        """
        self.id = packet_id
        self.src_id = src_id
        self.dest_id = dest_id
        self.size = size
        self.type = packet_type
        self.time = time.time()
        self.route_taken = []
        self.created_time = time.time()
        self.delivered_time = None
        
    def add_hop(self, node_id):
        self.route_taken.append(node_id)
    
    def create_ack(self):
        return Packet(self.dest,self.src, None, "ACK")
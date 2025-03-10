import random as rnd
import time

class Packet:
    def __init__(self, packet_id, src, dest, size, packet_type="DATA"):
        """
        Args:
            src (int)
            dest (int)
            size (int)
            packet_type (str, optional): Defaults to "DATA".
        """
        self.id = packet_id
        self.src = src
        self.dest = dest
        self.size = size
        self.type = packet_type
        self.time = time.time()
    
    def create_ack(self):
        return Packet(self.dest,self.src, None, "ACK")
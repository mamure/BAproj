import random as rnd
import time

class Packet:
    def __init__(self, src, dest, payload, size, packet_type="DATA"):
        """_summary_

        Args:
            src (int): _description_
            dest (int): _description_
            payload (_type_): _description_
            packet_type (str, optional): _description_. Defaults to "DATA".
        """
        self.src = src
        self.dest = dest
        self.payload = payload
        self.size = size
        self.type = packet_type
        self.time = time.time()
    
    def create_ack(self):
        return Packet(self.dest,self.src, None, "ACK")
    
    def send_packet(self):
        if rnd.random() >= 1: # 1 is placeholder for loss ratio for edge
            print(f"Packet sent from {self.src} to {self.dest} with payload: {self.payload}")
            self.send_ack()
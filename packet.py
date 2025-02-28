import random as rnd

class Packet:
    def __init__(self, src, dest, payload):
        """_summary_

        Args:
            src (node_id): _description_
            dest (node_id): _description_
            payload (_type_): _description_
        """
        self.src = src
        self.dest = dest
        self.payload = payload
        
    def send_packet(self):
        if rnd.random() >= 1: # 1 is placeholder for loss ratio for edge
            print(f"Packet sent from {self.src} to {self.dest} with payload: {self.payload}")
            self.send_ack()
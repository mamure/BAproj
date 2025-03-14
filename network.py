import socket
import threading
import random as rnd
import time
from packet import Packet
import pickle as pkl

NODE_ID_COUNTER = 0
EDGE_ID_COUNTER = 0
PACKET_ID_COUNTER = 0

def node_id_manager():
    global NODE_ID_COUNTER
    current = NODE_ID_COUNTER
    NODE_ID_COUNTER += 1
    return current

def edge_id_manager():
    global EDGE_ID_COUNTER
    current = EDGE_ID_COUNTER
    EDGE_ID_COUNTER += 1
    return current

def packet_id_manager():
    global PACKET_ID_COUNTER
    current = PACKET_ID_COUNTER
    PACKET_ID_COUNTER += 1
    return current

class Node:
    def __init__(self, node_id, type, ip="127.0.0.1", port=None):
        """
        Args:
            node_id (int)
            type (str)
            ip (str, optional): Defaults to "127.0.0.1".
            port (int, optional)
        """
        self.id = node_id
        self.type = type
        self.neighbors = []
        self.routing_table = {}
        self.load = 0
        self.congest_status = False
        
        self.ip = ip
        self.port = 5000 + node_id
        self.socket = None
        self.listening = False
        self.received_packets = []
        
    def __repr__(self):
        return f"Node(id={self.id}, type={self.type})"

    def start_listening(self):
        if self.listening:
            return
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.ip, self.port))
        self.listening = True
        
        self.listener_thread = threading.Thread(target=self.listen_for_packets)
        self.listener_thread.daemon = True
        self.listener_thread.start()
    
    def stop_listening(self):
        self.listening = False
        self.socket.close()
        self.socket = None
        
    def listen_for_packets(self):
        while self.listening:
            try:
                data, addr = self.socket.recvfrom(4096)
                packet = pkl.loads(data)
                
                self.received_packets.append(packet)
                
                if packet.type == 'DATA':
                    self.send_ack(packet, addr)
            except Exception as e:
                if self.listening:
                    print(f'Error on node {self.id}: {e}')
                    
    def send_ack(self, packet, addr):
        packet_id = packet_id_manager()
        ack_packet = Packet(
            packet_id,
            src_id=packet.dest_id,
            dest_id=packet.src_id,
            size=64,
            packet_type="ACK"
        )
        try:
            ack_data = pkl.dumps(ack_packet)
            self.socket.sendto(ack_data, addr)
        except Exception as e:
            print(f'Error sending ACK from node {self.id}: {e}')
            
    def send_packet(self, dest, edge):
        if not self.socket:
            self.start_listening()
            time.sleep(0.1)
        
        packet_id = packet_id_manager()
        packet = Packet(
            packet_id,
            src_id=self.id,
            dest_id=dest.id,
            size=1024
        )
        
        loss_rate = edge.loss_rate
        if rnd.random() < loss_rate:
            return {'success': False, 'reason': 'packet_loss'}
        
        max_tries = 3
        retry = 0
        while retry < max_tries:
            try:
                packet_data = pkl.dumps(packet)
                self.socket.sendto(packet_data, (dest.ip, dest.port))
                self.socket.settimeout(0.5) # half a second timeout
                try:
                    ack_data, addr = self.socket.recvfrom(4096)
                    ack = pkl.loads(ack_data)
                    if ack.type == 'ACK':
                        return {'success': True, 'ack': ack_data}
                    else:
                        return {'success': False, 'reason': 'invalid_ack'}

                except socket.timeout:
                    print(f'ACK timeout for packet {packet_id}')
                    retry += 1
                    continue
            except Exception as e:
                return {'success': False, 'reason': str(e)}
        return {'success': False, 'reason': 'timeout'}
class Edge:
    def __init__(self, edge_id, src, dst, bandwidth, loss_rate):
        self.id = edge_id
        self.src = src
        self.dst = dst
        self.bandwidth = bandwidth
        self.loss_rate = loss_rate
        self.channel = rnd.randint(1,3)
        self.active = True
        
    def __repr__(self):
        return f"Edge({self.src.id} <-> {self.dst.id})"
    
    def transmit_pck(self, packet_sz=1024):
        if not self.active:
            return None
        
        trans_time = (packet_sz * 8) / (self.bandwidth * 1_000_000)
        
        time.sleep(trans_time)
        return trans_time
    
    def send_pck(self, src, dst):
        if src.id != self.src.id and src.id != self.dst.id:
            raise ValueError(f"Node {src.id} is not connected to this edge")
        
        if dst.id != self.src.id and dst.id != self.dst.id:
            raise ValueError(f"Node {dst.id} is not connected to this edge")
        
        self.transmit_pck()
        
        result = src.send_packet(dst, edge=self)
        return result
    
class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}
        
    def create_node(self, type, ip="127.0.0.1", port=None):
        node = Node(node_id_manager(), type, ip, port)
        self.nodes[node.id] = node
        return node
    
    def add_edge(self, node_a, node_b, bandwidth, loss_rate):
        if node_b.id not in node_a.neighbors:
            edge = Edge(edge_id_manager(), node_a, node_b, bandwidth, loss_rate)
            self.edges[edge.id] = edge
            node_a.neighbors.append(node_b.id)
            node_b.neighbors.append(node_a.id)
            return edge
        
    def start_network(self):
        for node in self.nodes.values():
            node.start_listening()
    
    def stop_network(self):
        for node in self.nodes.values():
            node.stop_listening()
            
    def get_edge_between_nodes(self, node_a_id, node_b_id):
        for edge in self.edges.values():
            if (edge.src.id == node_a_id and edge.dst.id == node_b_id) or (edge.src.id == node_b_id and edge.dst.id == node_a_id):
                return edge
        return None
    
    def send_packet(self, src_id, dst_id):
        if src_id not in self.nodes or dst_id not in self.nodes:
            return {'success': False, 'reason': 'invalid_node_id'}
        
        src = self.nodes[src_id]
        dst = self.nodes[dst_id]
        
        if not src.listening:
            src.start_listening()
            time.sleep(0.1)
    
        if not dst.listening:
            dst.start_listening()
            time.sleep(0.1)
        
        edge = self.get_edge_between_nodes(src.id, dst.id)
        if not edge:
            return {'success': False, 'reason': 'nodes_not_connected'}
        return edge.send_pck(src, dst)
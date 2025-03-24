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

def reset_id_managers():
    global NODE_ID_COUNTER, EDGE_ID_COUNTER, PACKET_ID_COUNTER
    NODE_ID_COUNTER = 0
    EDGE_ID_COUNTER = 0
    PACKET_ID_COUNTER = 0

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
            return {'success': False, 'reason': 'timed out'}
        
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
                    return
                    
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
            return {'success': False, 'reason': 'error'}
            
    def send_packet_node(self, dest, edge, send_packet=None):
        if not self.socket:
            self.start_listening()
            time.sleep(0.1)
            
        if send_packet is not None:
            packet = send_packet
        else:
            packet_id = packet_id_manager()
            packet = Packet(
                packet_id,
                src_id=self.id,
                dest_id=dest.id,
                size=1024
            )
        
        loss_rate = edge.loss_rate
        if rnd.random() < loss_rate:
            self.socket.settimeout(1)
            return {'success': False, 'reason': 'packet_loss'}
        
        max_tries = 3
        retry = 0
        while retry < max_tries:
            try:
                self.socket.setblocking(1)
                self.socket.settimeout(3)
                
                packet_data = pkl.dumps(packet)
                self.socket.sendto(packet_data, (dest.ip, dest.port))
                try:
                    ack_data, addr = self.socket.recvfrom(4096)
                    ack = pkl.loads(ack_data)
                    if ack.type == 'ACK':
                        if not send_packet:
                            packet.add_hop(dest.id)
                        return {'success': True}
                    else:
                        return {'success': False, 'reason': 'invalid_ack'}
                except socket.timeout:
                    retry += 1
                    print(f"Timeout retry {retry}/{max_tries}")
                    continue
            except Exception as e:
                print(f"Error: {str(e)}")
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
    
    def send_packet_edge(self, src, dst, packet=None):
        if src.id != self.src.id and src.id != self.dst.id:
            raise ValueError(f"Node {src.id} is not connected to this edge")
        
        if dst.id != self.src.id and dst.id != self.dst.id:
            raise ValueError(f"Node {dst.id} is not connected to this edge")
        
        result = src.send_packet_node(dst, edge=self, send_packet=packet)
        
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
    
    def send_packet_graph(self, src_id, dest_id, packet=None):
        if src_id not in self.nodes or dest_id not in self.nodes:
            return {'success': False, 'reason': 'invalid_node_id'}

        src = self.nodes[src_id]
        dest = self.nodes[dest_id]

        if packet is None:
            packet_id = packet_id_manager()
            packet = Packet(packet_id, src_id, dest_id, 1024)

        if not packet.route_taken or packet.route_taken[-1] != src_id:
            packet.add_hop(src_id)

        if not src.listening:
            src.start_listening()
        if not dest.listening:
            dest.start_listening()

        current_node = src
        print(f'current node id: {current_node.id}')
        print(f'src node id: {dest_id}')

        while current_node.id != dest_id:
            # Get the routing table entry for the destination
            route = current_node.routing_table.get(dest_id)
            if route is None:
                return {'success': False, 'reason': 'no_route_found'}

            # If the routing table holds a full route (a list), pick the next hop.
            if isinstance(route, list):
                try:
                    idx = route.index(current_node.id)
                except ValueError:
                    return {'success': False, 'reason': 'no_route_found'}

                if idx + 1 >= len(route):
                    return {'success': False, 'reason': 'no_route_found'}
                next_hop_id = route[idx + 1]
            else:
                # Otherwise assume it's the next hop id
                next_hop_id = route

            # Get the edge between the current node and the next hop
            edge = self.get_edge_between_nodes(current_node.id, next_hop_id)
            if not edge:
                return {'success': False, 'reason': 'nodes_not_connected'}

            # Send the packet along the edge
            result = edge.send_packet_edge(current_node, self.nodes[next_hop_id], packet)
            if not result.get('success', False):
                return result

            packet.add_hop(next_hop_id)
            current_node = self.nodes[next_hop_id]
            print(f'current node id: {current_node.id}')

        return {'success': True}

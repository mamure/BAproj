import socket
import threading
import json
import time
import random as rnd

class Node:
    def __init__(self, node_id, type, ip="127.0.0.1", port=None):
        self.id = node_id
        self.type = type
        self.neighbors = []
        self.routing_table = {}
        self.load = 0
        self.congest_status = False
        
        # Network communication properties
        self.ip = ip
        self.port = 5000 + node_id  # port based on node_id
        self.socket = None
        self.listening = False
        self.received_packets = []
        self.packet_handlers = []
        
    def __repr__(self):
        return f"Node(id={self.id}, type={self.type}, port={self.port})"
    
    def start_listening(self):
        """Start the socket server to listen for incoming packets"""
        if self.listening:
            return
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.ip, self.port))
        self.listening = True
        
        # Start listener thread
        self.listener_thread = threading.Thread(target=self._listen_for_packets)
        self.listener_thread.daemon = True
        self.listener_thread.start()
        print(f"Node {self.id} listening on {self.ip}:{self.port}")
        
    def stop_listening(self):
        """Stop the socket server"""
        self.listening = False
        if self.socket:
            self.socket.close()
            self.socket = None
    
    def _listen_for_packets(self):
        """Listen for incoming packets"""
        while self.listening:
            try:
                data, addr = self.socket.recvfrom(4096)
                packet = json.loads(data.decode('utf-8'))
                
                # Store the packet
                self.received_packets.append(packet)
                
                # Process with registered handlers
                for handler in self.packet_handlers:
                    handler(packet, addr)
                
                # Handle ACKs
                if packet.get('type') == 'DATA':
                    self._send_ack(packet, addr)
                
                print(f"Node {self.id} received: {packet}")
            except Exception as e:
                if self.listening:  # Only show error if we're supposed to be listening
                    print(f"Node {self.id} listening error: {e}")
    
    def _send_ack(self, packet, addr):
        """Send ACK for a received packet"""
        ack_packet = {
            'type': 'ACK',
            'for_packet': packet.get('id'),
            'src': self.id,
            'dest': packet.get('src')
        }
        try:
            self.socket.sendto(json.dumps(ack_packet).encode('utf-8'), addr)
        except Exception as e:
            print(f"Error sending ACK from node {self.id}: {e}")
    
    def register_packet_handler(self, handler_function):
        """Register a function to handle incoming packets"""
        self.packet_handlers.append(handler_function)
    
    def send_packet(self, dest_node, payload, edge=None):
        """Send a packet to another node
        
        Args:
            dest_node: The destination Node object
            payload: Data to send
            edge: Optional Edge to use (for loss rate)
            
        Returns:
            dict: Result with success status and details
        """
        if not self.socket:
            self.start_listening()
        
        # Create packet
        packet_id = rnd.randint(10000, 99999)
        packet = {
            'id': packet_id,
            'src': self.id,
            'dest': dest_node.id,
            'payload': payload,
            'type': 'DATA',
            'timestamp': time.time()
        }
        
        # Check for simulated packet loss
        loss_rate = edge.loss_rate if edge else 0.1
        if rnd.random() < loss_rate:
            print(f"Simulated packet loss: Node {self.id} -> Node {dest_node.id}")
            return {'success': False, 'reason': 'packet_loss'}
        
        try:
            # Send the packet
            self.socket.sendto(json.dumps(packet).encode('utf-8'), 
                              (dest_node.ip, dest_node.port))
            
            # Wait for ACK with timeout
            self.socket.settimeout(2.0)  # 2 second timeout
            try:
                ack_data, _ = self.socket.recvfrom(4096)
                ack = json.loads(ack_data.decode('utf-8'))
                
                if ack.get('type') == 'ACK' and ack.get('for_packet') == packet_id:
                    print(f"ACK received for packet {packet_id}")
                    return {'success': True, 'ack': ack}
                else:
                    return {'success': False, 'reason': 'invalid_ack'}
                    
            except socket.timeout:
                print(f"ACK timeout for packet {packet_id}")
                return {'success': False, 'reason': 'timeout'}
            
        except Exception as e:
            print(f"Error sending from Node {self.id}: {e}")
            return {'success': False, 'reason': str(e)}
        finally:
            # Reset timeout
            self.socket.settimeout(None)
            
class Edge:
    def __init__(self, edge_id, src, dst, bandwidth, loss_rate, channel=1):
        self.id = edge_id
        self.src = src
        self.dst = dst
        self.bandwidth = bandwidth  # in Mbps
        self.loss_rate = loss_rate  # 0.0 to 1.0
        self.channel = channel
        self.active = True
        self.packets_sent = 0
        self.packets_lost = 0
        self.bytes_transferred = 0
        
    def __repr__(self):
        return f"Edge({self.src.id} <-> {self.dst.id})"
    
    def transmit_packet(self, packet_size=1024):
        """
        Simulate packet transmission over this edge
        Returns transmission time in seconds
        """
        if not self.active:
            return None
        
        # Calculate transmission time based on bandwidth
        # bandwidth in Mbps, packet_size in bytes
        transmission_time = (packet_size * 8) / (self.bandwidth * 1_000_000)
        
        # Simulate network delay
        time.sleep(transmission_time)
        
        return transmission_time
    
    def send_packet(self, from_node, to_node, payload):
        """Send a packet over this edge from one node to another"""
        if from_node.id != self.src.id and from_node.id != self.dst.id:
            raise ValueError(f"Node {from_node.id} is not connected to this edge")
        
        if to_node.id != self.src.id and to_node.id != self.dst.id:
            raise ValueError(f"Node {to_node.id} is not connected to this edge")
        
        # Simulate transmission delay
        self.transmit_packet()
        
        # Send the actual packet
        result = from_node.send_packet(to_node, payload, edge=self)
        
        # Update statistics
        self.packets_sent += 1
        if not result['success']:
            self.packets_lost += 1
        else:
            # Estimate bytes based on payload size + overhead
            estimated_bytes = len(json.dumps(payload)) + 100  # 100 bytes overhead
            self.bytes_transferred += estimated_bytes
            
        return result

class Graph:
    def __init__(self):
        self.node_id_counter = 0
        self.edge_id_counter = 0
        self.nodes = {}
        self.edges = {}
        
    def create_node(self, type, ip="127.0.0.1", port=None):
        """Create a new node with networking capability"""
        node = Node(self.node_id_counter, type, ip, port)
        self.nodes[self.node_id_counter] = node
        self.node_id_counter += 1
        return node
    
    def add_edge(self, node_a, node_b, bandwidth, loss_rate):
        """Connect two nodes with a communication edge"""
        if node_b.id not in node_a.neighbors:
            edge = Edge(self.edge_id_counter, node_a, node_b, bandwidth, loss_rate)
            self.edges[self.edge_id_counter] = edge
            self.edge_id_counter += 1
            node_a.neighbors.append(node_b.id)
            node_b.neighbors.append(node_a.id)
            return edge
    
    def start_network(self):
        """Start all nodes listening for packets"""
        for node in self.nodes.values():
            node.start_listening()
    
    def stop_network(self):
        """Stop all nodes from listening"""
        for node in self.nodes.values():
            node.stop_listening()
    
    def get_edge_between_nodes(self, node_a_id, node_b_id):
        """Find the edge connecting two nodes"""
        for edge in self.edges.values():
            if (edge.src.id == node_a_id and edge.dst.id == node_b_id) or (edge.src.id == node_b_id and edge.dst.id == node_a_id):
                return edge
        return None
    
    def send_packet_between_nodes(self, from_node_id, to_node_id, payload):
        """Send a packet between two nodes in the network"""
        if from_node_id not in self.nodes or to_node_id not in self.nodes:
            return {'success': False, 'reason': 'invalid_node_id'}
        
        from_node = self.nodes[from_node_id]
        to_node = self.nodes[to_node_id]
        
        # Find the edge connecting these nodes
        edge = self.get_edge_between_nodes(from_node_id, to_node_id)
        if not edge:
            return {'success': False, 'reason': 'nodes_not_connected'}
        
        # Send the packet over the edge
        return edge.send_packet(from_node, to_node, payload)
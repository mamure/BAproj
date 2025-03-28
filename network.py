import threading
import random as rnd
import time
import queue
from packet import Packet

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
    def __init__(self, node_id, type):
        """
        Args:
            node_id (int)
            type (str)
        """
        self.id = node_id
        self.type = type
        self.neighbors = []
        self.routing_table = {}
        self.load = 0
        self.congest_status = False
        self.queue = queue.Queue()
        self.received_packets = []
        self.sent_packets = {}
        self.running = False
        
    def __repr__(self):
        return f"Node(id={self.id}, type={self.type})"

    def start_running(self):
        """Starts processing thread
        """
        if self.running:
            return {'success': False, 'reason': 'already_running'}
        
        self.running = True
        self.thread = threading.Thread(target=self.process_packets)
        self.thread.daemon = True
        self.thread.start()
        return {'success': True}
    
    def stop_running(self):
        self.running = False
        self.thread.join()
        
    def process_packets(self):
        while self.running:
            try:
                message = self.queue.get(timeout=1)
                packet = message['packet']
                src = message['sender']

                self.received_packets.append(packet)
                
                if packet.type == 'DATA':
                    self.send_ack(packet, src)
                self.queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                if self.running:
                    print(f'Error processing packet at Node {self.id}: {e}')
    
    def send_ack(self, packet, src):
        packet_id = packet_id_manager()
        ack = Packet(packet_id, self.id, packet.src_id, 64,"ACK")
        
        src.queue.put({'packet': ack, 'sender': self})
        
    def receive_message(self, packet, src):
        self.queue.put({'packet': packet, 'sender': src})
    
class Edge:
    def __init__(self, edge_id, src, dest, bandwidth, loss_rate):
        self.id = edge_id
        self.src = src
        self.dest = dest
        self.bandwidth = bandwidth
        self.loss_rate = loss_rate
        self.channel = rnd.randint(1,3)
        self.active = True
        
    def __repr__(self):
        return f"Edge({self.src.id} <-> {self.dst.id})"
    
    def send_packet_edge(self, src, dest, packet):
        if not self.active:
            print(f"Edge {self.id}: Inactive, cannot send packet {packet.id}")
            return {'success': False, 'reason': 'edge_inactive'}
        if src.id != self.src.id and src.id != self.dest.id:
            return {'success': False, 'reason': 'invalid_src'}
        if dest.id != self.src.id and dest.id != self.dest.id:
            return {'success': False, 'reason': 'invalid_dest'}
        if rnd.random() < self.loss_rate:
            return {'success': False, 'reason': 'packet_loss'}
        
        delay = packet.size / self.bandwidth * 0.001
        time.sleep(delay)
        
        dest.receive_message(packet, src)
        return {'success': True}
    
class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}
        
    def create_node(self, type):
        node = Node(node_id_manager(), type)
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
            node.start_running()
    
    def stop_network(self):
        for node in self.nodes.values():
            node.stop_running()
            
    def get_edge_between_nodes(self, node_a_id, node_b_id):
        for edge in self.edges.values():
            if (edge.src.id == node_a_id and edge.dest.id == node_b_id) or (edge.src.id == node_b_id and edge.dest.id == node_a_id):
                return edge
        return None
    
    def send_packet_graph(self, src_id, dest_id):
        if src_id not in self.nodes or dest_id not in self.nodes:
            return {'success': False, 'reason': 'invalid_node_id'}
        
        src = self.nodes[src_id]
        dest = self.nodes[dest_id]
        
        packet_id = packet_id_manager()
        packet = Packet(packet_id, src_id, dest_id, 1024)
        packet.route_taken.append(src_id)
        
        if not src.running:
            src.start_running()
        if not dest.running:
            dest.start_running()
            
        current_node = src
        next_node = None
        
        while current_node.id != dest_id:
            if dest_id not in src.routing_table:
                return {'success': False, 'reason': 'no_route_found'}
            next_hop_id = current_node.routing_table[dest_id]
            next_node = self.nodes[next_hop_id]
            
            edge = self.get_edge_between_nodes(current_node.id, next_hop_id)
            if not edge:
                return {'success': False, 'reason': 'nodes_not_connected'}
            
            max_tries = 3
            for retry in range(max_tries):
                send_result = edge.send_packet_edge(current_node, next_node, packet)
                if send_result['success']:
                    time.sleep(0.1)
                    packet.route_taken.append(next_hop_id)
                    current_node.sent_packets[packet.id] = time.time()
                    current_node = next_node
                    break
                elif send_result['reason'] == 'packet_loss':
                    continue
                else:
                    return send_result
            else:
                return {'success': False, 'reason': 'max_tries'}
        print(f"packet {packet.id} route: {packet.route_taken}")
        return {'success': True, 'packet': packet}
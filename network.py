import threading
import time
import queue
import random as rnd

from packet import Packet
import routing_alg.wcett_lb_post as wcett_lb_post
import routing_alg.wcett_lb_pre as wcett_lb_pre
import routing_alg.routing as routing
from log_config import get_logger

logger = get_logger("network")

NODE_ID_COUNTER = 0
EDGE_ID_COUNTER = 0
PACKET_ID_COUNTER = 0

BUFFER_SIZE = { # message queue maximum length
    "IGW": 150,
    "MR": 75
} 
QUEUE_PROCESS_TIME = 0.05  # time for node to process packet. Adjust to fill up queue. ≈ 20 pkt/s to fill up

def node_id_manager():
    """Generate and return a unique ID for a new node.

    Returns:
        int: A unique node identifier
    """
    global NODE_ID_COUNTER
    current = NODE_ID_COUNTER
    NODE_ID_COUNTER += 1
    return current

def edge_id_manager():
    """Generate and return a unique ID for a new edge.

    Returns:
        int: A unique edge identifier
    """
    global EDGE_ID_COUNTER
    current = EDGE_ID_COUNTER
    EDGE_ID_COUNTER += 1
    return current

def packet_id_manager():
    """Generate and return a unique ID for a new packet.

    Returns:
        int: A unique edge identifier
    """
    global PACKET_ID_COUNTER
    current = PACKET_ID_COUNTER
    PACKET_ID_COUNTER += 1
    return current

def reset_id_managers():
    """Reset all ID counters to zero.
    """
    global NODE_ID_COUNTER, EDGE_ID_COUNTER, PACKET_ID_COUNTER
    NODE_ID_COUNTER = 0
    EDGE_ID_COUNTER = 0
    PACKET_ID_COUNTER = 0

class Node:
    def __init__(self, node_id, type, network):
        """
        Args:
            node_id (int)
            type (str)
            network (network)
        """
        self.id = node_id
        self.type = type
        self.neighbors = []
        self.routing_table = {}
        self.load = 0
        self.congest_status = False
        buffer_size = BUFFER_SIZE.get(type, 75)  # Default to 75 if type not found
        self.queue = queue.Queue(maxsize=buffer_size)
        self.received_packets = []
        self.sent_packets = {}
        self.dropped_packets = []
        self.running = False
        self.network = network
        
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
        
        self.congest_thread = threading.Thread(target=self.monitor_congestion)
        self.congest_thread.daemon = True
        self.congest_thread.start()
        
        return {'success': True}
    
    def stop_running(self):
        """Stops processing thread
        """
        self.running = False
        if hasattr(self, 'thread') and self.thread.is_alive():
            self.thread.join(timeout=2.0)
        if hasattr(self, 'congest_thread') and self.congest_thread.is_alive():
            self.congest_thread.join(timeout=2.0)
    
    def monitor_congestion(self):
        """Monitor and manage node congestion status.
        """
        while self.running:
            try:
                routing_algorithm = self.network.routing_algorithm
                
                if routing_algorithm and isinstance(routing_algorithm, routing.WCETT_LB_PRERouting):
                    wcett_lb_pre.predict_congestion(self, self.network, routing_algorithm)
                elif routing_algorithm and isinstance(routing_algorithm, routing.WCETT_LB_POSTRouting):
                    wcett_lb_post.update_congest_status(self, self.network, routing_algorithm)
                
                self.load = self.queue.qsize()

                for dest_id in self.routing_table.keys():
                    if routing_algorithm and isinstance(routing_algorithm, routing.WCETT_LB_POSTRouting):
                        wcett_lb_post.update_path(self, self.network, dest_id, routing_algorithm)
                    elif routing_algorithm and isinstance(routing_algorithm, routing.WCETT_LB_PRERouting):
                        wcett_lb_pre.update_path(self, self.network, dest_id, routing_algorithm)
                time.sleep(1)
            except Exception as e:
                if self.running:
                    logger.error(f"Error monitoring congestion at Node {self.id}: {e}")
        
    def process_packets(self):
        """Process packets from the node's queue.
        """
        while self.running:
            try:
                message = self.queue.get(timeout=1)
                packet = message['packet']
                src = message['sender']
                self.received_packets.append(packet)
                
                if packet.type == 'ACK':
                    logger.debug(f"Node {self.id} received ACK from {packet.src_id} for packet to {packet.dest_id}")
                
                if self.type == "IGW":
                    time.sleep(QUEUE_PROCESS_TIME * 0.01)  # IGWs are alot faster but not instant
                else:
                    time.sleep(QUEUE_PROCESS_TIME)
                if packet.type == 'DATA':
                    self.send_ack(packet, src)
                self.queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                if self.running:
                    logger.error(f'Error processing packet at Node {self.id}: {e}')
    
    def send_ack(self, packet, src):
        """Send an acknowledgment packet in response to a data packet.

        Args:
            packet (Packet): The original data packet to acknowledge
            src (Node): The source node that sent the original packet
        """
        packet_id = packet_id_manager()
        ack = Packet(packet_id, self.id, packet.src_id, 64,"ACK")
        src.queue.put({'packet': ack, 'sender': self})
        
    def receive_message(self, packet, src):
        """Receive and process an incoming packet.

        Args:
            packet (Packet): The packet being received
            src (Node): The node sending the packet

        Returns:
            bool: True if packet was accepted, False if dropped
        """
        try:
             # Prioritize ACKs, should always go through
            if packet.type == 'ACK':
                self.received_packets.append(packet)
                return True
            try:
                self.queue.put_nowait({'packet': packet, 'sender': src})
                return True
            except queue.Full:
                print(f"Node {self.id}: dropping {packet.id} (buffer full)")
                self.dropped_packets.append({
                    'packet_id': packet.id,
                    'src': packet.src_id,
                    'dest': packet.dest_id,
                    'time': time.time(),
                    'reason': 'buffer_full'
                })
                return False
        except Exception as e:
            logger.error(f"Error receiving message at Node {self.id}: {e}")
            return False
    
    def receive_wcett_lb_update(self, sender_id, paths, state_changed=False):
        """
        Receive WCETT-LB metric updates from a neighbor node.
        
        Args:
            sender_id: ID of the node sending the update
            paths: List of (dest_id, path, metric) tuples with updated path metrics
        """
        if not hasattr(self, 'wcett_lb_updates'):
            self.wcett_lb_updates = {}
        
        self.wcett_lb_updates[sender_id] = {
            'paths': paths,
            'timestamp': time.time(),
            'state_changed': state_changed
        }
        
        # Log the update
        logger.debug(f"Node {self.id} received WCETT-LB update from node {sender_id} with {len(paths)} paths")
    
class Edge:
    def __init__(self, edge_id, src, dest, bandwidth, loss_rate):
        """Initialize a new edge between two nodes.

        Args:
            edge_id (int): Unique identifier for this edge
            src (Node): Source node object
            dest (Node): Destination node object
            bandwidth (float): Maximum data transfer rate
            loss_rate (float): Probability (0-1) of packet loss on this edge
        """
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
        """Send a packet across this edge.

        Args:
            src (Node): Source node sending the packet
            dest (Node): Destination node receiving the packet
            packet (Packet): The packet to be sent

        Returns:
            dict: Result with 'success' boolean and 'reason' string if failed
        """
        if not self.active:
            logger.error(f"Edge {self.id}: Inactive, cannot send packet {packet.id}")
            return {'success': False, 'reason': 'edge_inactive'}
        if src.id != self.src.id and src.id != self.dest.id:
            return {'success': False, 'reason': 'invalid_src'}
        if dest.id != self.src.id and dest.id != self.dest.id:
            return {'success': False, 'reason': 'invalid_dest'}
        if rnd.random() < self.loss_rate:
            return {'success': False, 'reason': 'packet_loss'}
        
        tx = packet.size / self.bandwidth * 0.01
        time.sleep(tx)
        
        receive_result = dest.receive_message(packet, src)
        if not receive_result:
            return {'success': False, 'reason': 'buffer_full'}
        return {'success': True}
    
class Graph:
    def __init__(self, routing_algorithm=None):
        """Initialize a new network graph.

        Args:
            routing_algorithm (object, optional): The routing algorithm to use.
                Defaults to None.
        """
        self.nodes = {}
        self.edges = {}
        self.routing_algorithm = routing_algorithm
        
    def create_node(self, type):
        """Create a new node and add it to the network.

        Args:
            type (str): The type of node to create (e.g., 'router', 'client')

        Returns:
            Node: The newly created node
        """
        node = Node(node_id_manager(), type, network=self)
        self.nodes[node.id] = node
        return node
    
    def add_edge(self, node_a, node_b, bandwidth, loss_rate):
        """Create an edge connecting two nodes.

        Args:
            node_a (Node): First node to connect
            node_b (Node): Second node to connect
            bandwidth (float): Maximum data transfer rate in Mbps (megabits per second)
            loss_rate (float): Probability (0-1) of packet loss on the edge

        Returns:
            Edge: The newly created edge, or None if the nodes were already connected
        """
        if node_b.id not in node_a.neighbors:
            edge = Edge(edge_id_manager(), node_a, node_b, bandwidth, loss_rate)
            self.edges[edge.id] = edge
            node_a.neighbors.append(node_b.id)
            node_b.neighbors.append(node_a.id)
            return edge
        
    def start_network(self):
        """Start the operation of all nodes in the network.
        """
        for node in self.nodes.values():
            node.start_running()
    
    def stop_network(self):
        """Stop the operation of all nodes in the network.
        """
        for node in self.nodes.values():
            node.stop_running()
            
    def get_edge_between_nodes(self, node_a_id, node_b_id):
        """Return the edge connecting two nodes if it exists.

        Args:
            node_a_id (int): ID of the first node
            node_b_id (int): ID of the second node

        Returns:
            Edge: The edge object connecting the two nodes, or None if no such edge exists
        """
        for edge in self.edges.values():
            if (edge.src.id == node_a_id and edge.dest.id == node_b_id) or (edge.src.id == node_b_id and edge.dest.id == node_a_id):
                return edge
        return None
    
    def send_packet_graph(self, src_id, dest_id):
        if src_id not in self.nodes or dest_id not in self.nodes:
            logger.error(f"Invalid node ID: {src_id} or {dest_id}")
            return {'success': False, 'reason': 'invalid_node_id'}
        
        src = self.nodes[src_id]
        dest = self.nodes[dest_id]
        
        packet_id = packet_id_manager()
        packet = Packet(packet_id, src_id, dest_id, 1024, "DATA")
        packet.route_taken.append(src_id)
        
        if not src.running:
            src.start_running()
        if not dest.running:
            dest.start_running()
            
        current_node = src
        next_node = None
        
        while current_node.id != dest_id:
            if dest_id not in current_node.routing_table:
                return {'success': False, 'reason': 'no_route_found'}
            next_hop_id = current_node.routing_table[dest_id]
            next_node = self.nodes[next_hop_id]
            
            edge = self.get_edge_between_nodes(current_node.id, next_hop_id)
            if not edge:
                return {'success': False, 'reason': 'nodes_not_connected'}
            
            # Clear any old ACKs before sending
            current_node.received_packets = [p for p in current_node.received_packets if p.type != 'ACK']
            
            max_tries = 3
            for retry in range(max_tries):
                send_result = edge.send_packet_edge(current_node, next_node, packet)
                if send_result['success']:
                    packet.route_taken.append(next_hop_id)
                    current_node.sent_packets[packet.id] = time.time()
                    current_node = next_node
                    
                    # Wait for ACK
                    ack_received = False
                    start_time = time.time()
                    while time.time() - start_time < 0.5: 
                        if any(pkt.type == 'ACK' and 
                              pkt.src_id == next_hop_id and
                              pkt.dest_id == current_node.id
                              for pkt in src.received_packets):
                            ack_received = True
                            break
                        time.sleep(0.05)
                    break
            else:
                # If we couldn't send the packet at all, try again or fail
                if retry == max_tries - 1:
                    return send_result
    
        # If we reached here, the packet made it to the destination
        packet.delivered_time = time.time()
        return {'success': True, 'packet': packet}
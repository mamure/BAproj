import threading
import random as rnd
import time
import queue
from packet import Packet
import routing_alg.wcett_lb_post as wcett_lb_post
import routing_alg.wcett_lb_pre as wcett_lb_pre
import routing_alg.routing as routing
from log_config import get_logger

logger = get_logger("network")

NODE_ID_COUNTER = 0
EDGE_ID_COUNTER = 0
PACKET_ID_COUNTER = 0

BUFFER_SIZE = 75
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
        self.queue = queue.Queue(maxsize=BUFFER_SIZE)
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
                wcett_lb_post.update_congest_status(self, self.network)
                self.load = self.queue.qsize()

                for dest_id in self.routing_table.keys():
                    routing_algorithm = self.network.routing_algorithm
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
                if self.type == "IGW":
                    time.sleep(QUEUE_PROCESS_TIME * 0.1)  # IGWs are faster but not instant
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
            if self.type == "IGW" or not self.congest_status:
                self.queue.put({'packet': packet, 'sender': src})
                return True
            else:
                print(f"Node {self.id}: dropping {packet.id} (congested)")
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
        
        delay = packet.size / self.bandwidth * 0.01
        time.sleep(delay)
        
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
            
            max_tries = 3
            for retry in range(max_tries):
                send_result = edge.send_packet_edge(current_node, next_node, packet)
                if send_result['success']:
                    time.sleep(0.01)
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
        if packet.id in dest.dropped_packets:
            return {'success': False, 'reason': 'dropped_at_destination', 'packet': packet.id}
        packet.delivered_time = time.time()
        return {'success': True, 'packet': packet}
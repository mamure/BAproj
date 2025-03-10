import random
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
from complex import initialize_network
from packet import Packet
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MeshNetworkSimulator:
    def __init__(self, num_c=15, num_ap=6, num_igw=1, packet_size=512, timeout=1.0):
        """Initialize the mesh network simulator."""
        self.num_c = num_c
        self.num_ap = num_ap
        self.num_igw = num_igw
        self.packet_size = packet_size
        self.timeout = timeout
        
        # Performance metrics
        self.packets_sent = 0
        self.packets_delivered = 0
        self.packets_lost = 0
        self.retransmissions = 0
        
        # Time-series data for visualization
        self.time_points = []
        self.throughput_data = []
        self.error_rate_data = []
        self.current_time = 0
        
        self.network = self._setup_network()
        self.pending_packets = {}  # {packet_id: (source, destination, send_time, retry_count)}
        
    def _setup_network(self):
        """Set up the network using the complex network generator."""
        network = initialize_network(self.num_igw, self.num_ap, self.num_c)
        
        return network

    def generate_packet(self, source, destination):
        """Generate a packet from source to destination."""
        packet_id = f"pkt_{source}_{destination}_{self.packets_sent}"
        packet = Packet(
            packet_id=packet_id, 
            source=source, 
            destination=destination, 
            size=self.packet_size,
            timestamp=self.current_time
        )
        self.packets_sent += 1
        return packet
    
    def send_packet(self, source, packet):
        """Send a packet from a source node."""
        # Record the packet as pending
        self.pending_packets[packet.packet_id] = (
            source, 
            packet.destination, 
            self.current_time, 
            0  # retry count
        )
        
        # Find next hop (simple shortest path routing)
        try:
            path = nx.shortest_path(self.network, source=source, target=packet.destination)
            if len(path) > 1:
                next_hop = path[1]
                # Check if transmission succeeds
                if self._simulate_transmission(source, next_hop, packet):
                    logger.debug(f"Packet {packet.packet_id} sent from {source} to next hop {next_hop}")
                    self.network.nodes[next_hop]['buffer'].append((packet, path[2:] if len(path) > 2 else []))
                else:
                    logger.debug(f"Packet {packet.packet_id} failed during transmission from {source} to {next_hop}")
                    self.packets_lost += 1
            else:
                logger.warning(f"No valid path from {source} to {packet.destination}")
                self.packets_lost += 1
        except nx.NetworkXNoPath:
            logger.warning(f"No path from {source} to {packet.destination}")
            self.packets_lost += 1
            
    def _simulate_transmission(self, source, target, packet):
        """Simulate packet transmission over a link."""
        if (source, target) in self.network.edges():
            edge = self.network.edges[source, target]
            # Check for transmission error based on error probability
            if random.random() < edge['error_prob']:
                return False
                
            # Calculate transmission delay based on packet size and bandwidth
            # (not actually delaying, just simulating)
            delay = (packet.size * 8) / (edge['bandwidth'] * 1000)  # seconds
            return True
        return False
    
    def process_network(self):
        """Process packets in the network for one time step."""
        # Check for packet timeouts
        current_packets = list(self.pending_packets.items())
        for packet_id, (source, destination, send_time, retry_count) in current_packets:
            if self.current_time - send_time > self.timeout:
                # Handle timeout - retransmit if under max retries
                if retry_count < 3:  # Max 3 retries
                    logger.debug(f"Retransmitting packet {packet_id}, retry {retry_count+1}")
                    new_packet = Packet(
                        packet_id=packet_id,
                        source=source,
                        destination=destination,
                        size=self.packet_size,
                        timestamp=self.current_time
                    )
                    self.send_packet(source, new_packet)
                    self.retransmissions += 1
                    # Update retry count
                    self.pending_packets[packet_id] = (source, destination, self.current_time, retry_count + 1)
                else:
                    logger.debug(f"Packet {packet_id} abandoned after max retries")
                    self.packets_lost += 1
                    del self.pending_packets[packet_id]
        
        # Process nodes (forward packets)
        for node in self.network.nodes():
            if self.network.nodes[node]['buffer'] and not self.network.nodes[node]['processing']:
                self.network.nodes[node]['processing'] = True
                packet, next_hops = self.network.nodes[node]['buffer'].pop(0)
                
                # If this node is the destination
                if node == packet.destination:
                    logger.debug(f"Packet {packet.packet_id} delivered to destination {node}")
                    self.packets_delivered += 1
                    
                    # Send ACK if it was addressed to an IGW (simulate internet response)
                    if node in self.igw_nodes and packet.packet_id in self.pending_packets:
                        source, _, _, _ = self.pending_packets[packet.packet_id]
                        del self.pending_packets[packet.packet_id]
                        
                        # Create and send ACK packet back to source
                        ack_packet = Packet(
                            packet_id=f"ack_{packet.packet_id}",
                            source=node,
                            destination=source,
                            size=64,  # Smaller ACK packet
                            timestamp=self.current_time,
                            is_ack=True
                        )
                        self.send_packet(node, ack_packet)
                
                # Forward to next hop if needed
                elif next_hops:
                    next_hop = next_hops[0]
                    remaining_hops = next_hops[1:] if len(next_hops) > 1 else []
                    
                    if self._simulate_transmission(node, next_hop, packet):
                        logger.debug(f"Packet {packet.packet_id} forwarded from {node} to {next_hop}")
                        self.network.nodes[next_hop]['buffer'].append((packet, remaining_hops))
                    else:
                        logger.debug(f"Packet {packet.packet_id} lost during forwarding from {node} to {next_hop}")
                        self.packets_lost += 1
                
                self.network.nodes[node]['processing'] = False

    def generate_traffic(self, packets_per_step=5):
        """Generate new traffic in the network."""
        for _ in range(packets_per_step):
            if self.client_nodes and self.igw_nodes:
                source = random.choice(self.client_nodes)
                destination = random.choice(self.igw_nodes)
                packet = self.generate_packet(source, destination)
                self.send_packet(source, packet)
    
    def calculate_metrics(self):
        """Calculate network performance metrics."""
        # Calculate throughput: delivered packets * size / time in seconds
        if self.current_time > 0:
            throughput = (self.packets_delivered * self.packet_size * 8) / (self.current_time * 1000)  # kbps
        else:
            throughput = 0
            
        # Calculate error rate: (lost packets) / (sent packets)
        if self.packets_sent > 0:
            error_rate = self.packets_lost / self.packets_sent
        else:
            error_rate = 0
            
        # Store time-series data
        self.time_points.append(self.current_time)
        self.throughput_data.append(throughput)
        self.error_rate_data.append(error_rate * 100)  # as percentage
        
        return throughput, error_rate
    
    def visualize_network(self):
        """Visualize the current network state."""
        plt.figure(figsize=(15, 10))
        
        # Plot the network topology
        plt.subplot(2, 2, 1)
        node_colors = ['red' if self.network.nodes[n]['type'] == 'igw' else 'blue' for n in self.network.nodes()]
        nx.draw(self.network, pos=self.pos, node_color=node_colors, with_labels=True, 
                node_size=100, font_size=8)
        plt.title('Network Topology')
        
        # Plot throughput over time
        plt.subplot(2, 2, 2)
        plt.plot(self.time_points, self.throughput_data)
        plt.xlabel('Simulation Time')
        plt.ylabel('Throughput (kbps)')
        plt.title('Network Throughput')
        
        # Plot error rate over time
        plt.subplot(2, 2, 3)
        plt.plot(self.time_points, self.error_rate_data)
        plt.xlabel('Simulation Time')
        plt.ylabel('Error Rate (%)')
        plt.title('Packet Error Rate')
        
        # Display summary statistics
        plt.subplot(2, 2, 4)
        plt.axis('off')
        stats = f"""
        Simulation Statistics:
        - Packets Sent: {self.packets_sent}
        - Packets Delivered: {self.packets_delivered}
        - Packets Lost: {self.packets_lost}
        - Retransmissions: {self.retransmissions}
        - Current Throughput: {self.throughput_data[-1]:.2f} kbps
        - Current Error Rate: {self.error_rate_data[-1]:.2f}%
        """
        plt.text(0.1, 0.5, stats, fontsize=12)
        
        plt.tight_layout()
        plt.savefig(f"network_simulation_{self.current_time}.png")
        plt.close()
    
    def run_simulation(self, duration=100, update_interval=1):
        """Run the simulation for a specified duration."""
        for t in range(0, duration, update_interval):
            self.current_time = t
            
            # Generate new traffic
            self.generate_traffic()
            
            # Process network
            self.process_network()
            
            # Calculate metrics
            throughput, error_rate = self.calculate_metrics()
            
            if t % 10 == 0:  # Visualize every 10 steps
                logger.info(f"Simulation time: {t}, Throughput: {throughput:.2f} kbps, Error Rate: {error_rate*100:.2f}%")
                self.visualize_network()
        
        # Final visualization
        self.visualize_network()
        
        # Summary
        logger.info(f"""
        Simulation Complete!
        Total Packets Sent: {self.packets_sent}
        Successfully Delivered: {self.packets_delivered}
        Packets Lost: {self.packets_lost}
        Retransmissions: {self.retransmissions}
        Average Throughput: {np.mean(self.throughput_data):.2f} kbps
        Average Error Rate: {np.mean(self.error_rate_data):.2f}%
        """)


def main():
    # Create and run the simulator
    simulator = MeshNetworkSimulator()
    simulator.run_simulation(duration=100)


if __name__ == "__main__":
    main()
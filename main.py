from networks import complex_network
from networks import advanced_network
import routing_alg.routing as routing
import logging
import time
import random as rnd
import threading
import argparse
from network import reset_id_managers
from log_config import get_logger, setup_logging

logger = get_logger("main")

class MeshNetworkSimulator:
    """
    Mesh Network Simulator for evaluating routing algorithms in wireless mesh networks.
    
    This class provides functionality to simulate network traffic using different routing
    algorithms and network topologies.
    """
    def __init__(self, topology_type=0):
        """
        Initialize the simulator with a specified network topology.

        Args:
            topology_type (int, optional): The network topology to use. 
                0 = complex network, 1 = advanced network. Defaults to 0.
        """
        reset_id_managers()
        
        if topology_type == 0:
            self.network = complex_network.initialize_network()
            self.topology_name = "small"
        elif topology_type == 1:
            self.topology_name = "big"
            self.network = advanced_network.initialize_network()
        else:
            raise ValueError("Invalid topology type. Must be 0 (small) or 1 (big)")
        
    def simulate_traffic(self, duration, load):
        """
        Args:
            duration (int, optional): Duration of simulation in seconds.
            load (int, optional): packets per second.
        
        Returns:
            tuple: Tuple containing (error_rate, throughput, avg_delay)
        """
        self.network.start_network()
        
        total_packets = 0
        packets_sent = 0
        total_bytes = 0
        total_delay = 0.0
        packet_results = {}
        
        start_time = time.time()
        
        c_nodes = [node_id for node_id, node in self.network.nodes.items() 
            if node.type == "C"]
        igw_nodes = [node_id for node_id, node in self.network.nodes.items() 
            if node.type == "IGW"]
        
        def send_packet_thread(packet_id, src_id, dest_id):
            """
            Thread function to send a packet through the network.

            Args:
                packet_id (_type_): _description_
                src_id (_type_): _description_
                dest_id (_type_): _description_
            """
            result = self.network.send_packet_graph(src_id, dest_id)
            packet_results[packet_id] = result
        
        threads = []
        active_threads = []
        max_concurrent_threads = 50
        cleanup = 5
        
        packet_interval = 1.0 / load
        next_packet_time = start_time
        
        try:
            while time.time() - start_time < duration:
                current_time = time.time()
                if total_packets % cleanup == 0:
                    active_threads = [t for t in active_threads if t.is_alive()]
            
                if len(active_threads) >= max_concurrent_threads:
                    time.sleep(0.01)
                    active_threads = [t for t in active_threads if t.is_alive()]
                    continue
                
                if current_time < next_packet_time:
                    sleep_time = min(next_packet_time - current_time, 0.01)
                    time.sleep(sleep_time)
                    continue
            
                src_id = rnd.choice(c_nodes)
                dest_id = rnd.choice(igw_nodes)
                total_packets += 1
                
                t = threading.Thread(
                    target=send_packet_thread,
                    args=(total_packets, src_id, dest_id)
                )
                t.daemon = True
                t.start()
                active_threads.append(t)
                threads.append(t)
                
                next_packet_time += packet_interval
                
                if total_packets % 200 == 0:
                    elapsed = time.time() - start_time
                    logger.info(f"Progress: {total_packets} packets, {elapsed:.1f}s elapsed")

        except KeyboardInterrupt:
            logger.info("Simulation interrupted")
        finally:
            logger.info("Waiting for threads to complete...")
            for t in threads:
                t.join(timeout=0.5)
            
            for result in packet_results.values():
                if result.get('success'):
                    packets_sent += 1
                    packet = result.get('packet')
                    
                    total_bytes += packet.size
                    
                    if packet.delivered_time and packet.created_time:
                        delay = packet.delivered_time - packet.created_time
                        total_delay += delay
            
            elapsed = time.time() - start_time
            error_rate = ((total_packets - packets_sent) / total_packets)*100
            
            # Throughput in Kbps (kilobits per second)
            throughput = (total_bytes * 8 / 1000) / elapsed if elapsed > 0 else 0
            avg_delay = (total_delay / packets_sent) if packets_sent > 0 else 0
            
            logging.info('=== Simulation Results ===')
            logging.info(f'Duration: {elapsed:.1f} seconds')
            logging.info(f'Total packets: {total_packets}')
            logging.info(f'Successful packets: {packets_sent}')
            logging.info(f'Error rate: {error_rate:.1f}%')
            logging.info(f'Throughput: {throughput:.1f} Kbps')
            logging.info(f'Average delay: {avg_delay:.2f} seconds')
            
            return error_rate, throughput, avg_delay
    
    def hop_count_sim(self):
        """
        Define all routing tables using hop count metric algorithm. 
        The destination should be the IGW nodes' id.
        
        Returns:
            bool: True if routing tables were successfully created, False otherwise.
        """
        igw_nodes = [node_id for node_id, node in self.network.nodes.items() 
                if node.type == "IGW"]
        if not igw_nodes: 
            logging.error("NO IGW in network")
            return False
        
        self.network.routing_algorithm = None
        hop_count_alg = routing.HopCountRouting()

        logger.info("Hop count initial next hop:")
        for node_id, node in self.network.nodes.items():
            for igw_id in igw_nodes:
                next_hop = hop_count_alg.compute_routing_tb(self.network, node_id, igw_id)
                if next_hop is not None:
                    node.routing_table[igw_id] = next_hop
                    logger.info(f"{node.id} → {igw_id}: {node.routing_table[igw_id]}")
        
        logging.info(f"Hop count routing tables created for {len(self.network.nodes)} nodes")
                    
        return True
    
    def wcett_sim(self):
        """
        Define all routing tables using WCETT metric algorithm. 
        The destination should be the IGW nodes' id.
        
        Returns:
            bool: True if routing tables were successfully created, False otherwise.
        """
        igw_nodes = [node_id for node_id, node in self.network.nodes.items() 
                if node.type == "IGW"]
        if not igw_nodes: 
            logging.error("NO IGW in network")
            return False
        
        self.network.routing_algorithm = None
        wcett_alg = routing.WCETTRouting()
        
        logger.info("WCETT initial next hop:")
        for node_id, node in self.network.nodes.items():
            for igw_id in igw_nodes:
                next_hop = wcett_alg.compute_routing_tb(self.network, node_id, igw_id)
                if next_hop is not None:
                    node.routing_table[igw_id] = next_hop
                    logger.info(f"{node.id} → {igw_id}: {node.routing_table[igw_id]}")
        
        logging.info(f"WCETT routing tables created for {len(self.network.nodes)} nodes")
        
        return True
    
    def wcett_lb_post_sim(self):
        """
        Define all routing tables using WCETT-LB Post metric algorithm. 
        The destination should be the IGW nodes' id.
        
        Returns:
            bool: True if routing tables were successfully created, False otherwise.
        """
        igw_nodes = [node_id for node_id, node in self.network.nodes.items() 
                if node.type == "IGW"]
        if not igw_nodes: 
            logging.error("NO IGW in network")
            return False
        
        wcett_lb_post_algorithm = routing.WCETT_LB_POSTRouting()
        self.network.routing_algorithm = wcett_lb_post_algorithm
        
        for node_id, node in self.network.nodes.items():
            node.routing_table = {}  # Clear existing routing table
            for igw_id in igw_nodes:
                next_hop = wcett_lb_post_algorithm.compute_routing_tb(self.network, node_id, igw_id)
                if next_hop is not None:
                    node.routing_table[igw_id] = next_hop
        
        logging.info(f"WCETT-LB Post routing tables created for {len(self.network.nodes)} nodes")
        
        if hasattr(wcett_lb_post_algorithm, 'path_cache'):
            logger.info("WCETT-LB Post initial paths:")
            for (src, dest), path in wcett_lb_post_algorithm.path_cache.items():
                if len(path) > 0:
                    logger.info(f"{src} → {dest}: {path}")

        return True
    
    def wcett_lb_pre_sim(self):
        """
        Define all routing tables using WCETT-LB Pre metric algorithm. 
        The destination should be the IGW nodes' id.
        
        Returns:
            bool: True if routing tables were successfully created, False otherwise.
        """
        igw_nodes = [node_id for node_id, node in self.network.nodes.items() 
                if node.type == "IGW"]
        if not igw_nodes: 
            logging.error("NO IGW in network")
            return False
        
        wcett_lb_pre_algorithm = routing.WCETT_LB_PRERouting()
        self.network.routing_algorithm = wcett_lb_pre_algorithm
        
        for node_id, node in self.network.nodes.items():
            node.routing_table = {}  # Clear existing routing table
            for igw_id in igw_nodes:
                next_hop = wcett_lb_pre_algorithm.compute_routing_tb(self.network, node_id, igw_id)
                if next_hop is not None:
                    node.routing_table[igw_id] = next_hop
                    
        logging.info(f"WCETT-LB Pre routing tables created for {len(self.network.nodes)} nodes")
        
        if hasattr(wcett_lb_pre_algorithm, 'path_cache'):
            logger.info("WCETT-LB Pre initial paths:")
            for (src, dest), path in wcett_lb_pre_algorithm.path_cache.items():
                if len(path) > 0:
                    logger.info(f"{src} → {dest}: {path}")
        return True

def main():
    """
    Main entry point of the program.
    Parses command line arguments and runs the simulation with specified parameters.
    """
    parser = argparse.ArgumentParser(description='Wireless Mesh Network Simulator')
    
    parser.add_argument('-t', '--topology', type=int, choices=[0, 1], default=0,
                        help='Network topology: 0=small, 1=big (default: 0)')
    parser.add_argument('-d', '--duration', type=int, default=120,
                        help='Simulation duration in seconds (default: 120)')
    parser.add_argument('-l', '--load', type=float, default=20,
                        help='Network load in packets per second (default: 20)')
    
    args = parser.parse_args()
    
    sim = MeshNetworkSimulator(args.topology)
    
    while True:
        print("\nSelect an option:")
        print("1. Run Hop Count")
        print("2. Run WCETT")
        print("3. Run WCETT-LB Post")
        print("4. Run WCETT-LB Pre")
        print("5. Exit")
        
        choice = input("Enter: ")
        
        if choice == "1":
            # Run simulation with Hop Count from routing
            if sim.hop_count_sim():
                sim.simulate_traffic(duration=args.duration, load=args.load)
            else:
                logger.error("Failed")
            break
        elif choice == "2":
            # Run simulation with WCETT from routing
            if sim.wcett_sim():
                sim.simulate_traffic(duration=args.duration, load=args.load)
            else:
                logger.error("Failed")
            break
        elif choice == "3":
            # Run simulation with WCETT-LB Post from routing
            if sim.wcett_lb_post_sim():
                sim.simulate_traffic(duration=args.duration, load=args.load)
            else:
                logger.error("Failed")
            break
        elif choice == "4":
            # Run simulation with WCETT-LB Pre from routing
            if sim.wcett_lb_pre_sim():
                sim.simulate_traffic(duration=args.duration, load=args.load)
            else:
                logger.error("Failed")
            break
        elif choice == "5":
            logger.info("Exiting...")
            break
        else:
            logger.error("Invalid choice.")

if __name__ == "__main__":
    setup_logging()
    main()
import complex_network
import advanced_network
import routing
import logging
import time
import random as rnd
import threading

class MeshNetworkSimulator:
    def __init__(self, type):
        if type == 0:
            self.network = complex_network.initialize_network()
        elif type == 1:
            self.network = advanced_network.initialize_network()
        
    def simulate_traffic(self, duration=30, load=50):
        """
        Args:
            duration (int, optional): Duration of simulation in seconds. Defaults to 30.
            load (int, optional): packets per second. Defaults to 50.
        """
        self.network.start_network()
        
        total_packets = 0
        packets_sent = 0
        packet_results = {}
        
        start_time = time.time()
        
        c_nodes = [node_id for node_id, node in self.network.nodes.items() 
            if node.type == "C"]
        igw_nodes = [node_id for node_id, node in self.network.nodes.items() 
            if node.type == "IGW"]
        
        def send_packet_thread(packet_id, src_id, dest_id):
            priority = 3 if rnd.random() < 0.1 else 1
            result = self.network.send_packet_graph(src_id, dest_id, priority)
            packet_results[packet_id] = result
        
        threads = []
        active_threads = []
        max_concurrent_threads = 16
        cleanup = 10
        
        try:
            while time.time() - start_time < duration:
                if total_packets % cleanup == 0:
                    active_threads = [t for t in active_threads if t.is_alive()]
            
                if len(active_threads) >= max_concurrent_threads:
                    time.sleep(0.01)
                    active_threads = [t for t in active_threads if t.is_alive()]
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
                
                if total_packets % 200 == 0:
                    elapsed = time.time() - start_time
                    print(f"Progress: {total_packets} packets, {elapsed:.1f}s elapsed")
                    
                time.sleep(1 / load)

        except KeyboardInterrupt:
            print("Simulation interrupted")
        finally:
            print("Waiting for threads to complete...")
            for t in threads:
                t.join(timeout=0.5)
            
            for result in packet_results.values():
                if result.get('success'):
                    packets_sent += 1
            
            elapsed = time.time() - start_time
            error_rate = ((total_packets - packets_sent) / total_packets)*100
            
            print("\n=== Simulation Results ===")
            print(f'Duration: {elapsed:.1f} seconds')
            print(f'Total packets: {total_packets}')
            print(f'Successful packets: {packets_sent}')
            print(f'Error rate: {error_rate:.1f}%')
            
            return error_rate
    
    def hop_count_sim(self):
        """
        Define all routing tables using hop count metric algorithm. 
        The destination should be the IGW nodes' id.
        """
        igw_nodes = [node_id for node_id, node in self.network.nodes.items() 
                if node.type == "IGW"]
        if not igw_nodes: 
            logging.error("NO IGW in network")
            return False
        
        self.network.routing_algorithm = None
        hop_count_alg = routing.HopCountRouting()
        
        for node_id, node in self.network.nodes.items():
            for igw_id in igw_nodes:
                next_hop = hop_count_alg.compute_routing_tb(self.network, node_id, igw_id)
                if next_hop is not None:
                    node.routing_table[igw_id] = next_hop
        
        logging.info(f"Hop count routing tables created for {len(self.network.nodes)} nodes")
        return True
    
    def wcett_sim(self):
        """
        Define all routing tables using WCETT metric algorithm. 
        The destination should be the IGW nodes' id.
        """
        igw_nodes = [node_id for node_id, node in self.network.nodes.items() 
                if node.type == "IGW"]
        if not igw_nodes: 
            logging.error("NO IGW in network")
            return False
        
        self.network.routing_algorithm = None
        wcett_alg = routing.WCETTRouting()
        
        for node_id, node in self.network.nodes.items():
            for igw_id in igw_nodes:
                next_hop = wcett_alg.compute_routing_tb(self.network, node_id, igw_id)
                if next_hop is not None:
                    node.routing_table[igw_id] = next_hop
        
        logging.info(f"WCETT routing tables created for {len(self.network.nodes)} nodes")
        return True
    
    def wcett_lb_sim(self):
        """
        Define all routing tables using WCETT-LB metric algorithm. 
        The destination should be the IGW nodes' id.
        """
        igw_nodes = [node_id for node_id, node in self.network.nodes.items() 
                if node.type == "IGW"]
        if not igw_nodes: 
            logging.error("NO IGW in network")
            return False
        
        wcett_lb_algorithm = routing.WCETT_LBRouting()
        self.network.routing_algorithm = wcett_lb_algorithm
        
        for node_id, node in self.network.nodes.items():
            node.routing_table = {}  # Clear existing routing table
            for igw_id in igw_nodes:
                next_hop = wcett_lb_algorithm.compute_routing_tb(self.network, node_id, igw_id)
                if next_hop is not None:
                    node.routing_table[igw_id] = next_hop
        
        print(f"Is WCETT-LB Routing Algorithm: {isinstance(self.network.routing_algorithm, routing.WCETT_LBRouting)}")
        
        # # Print path cache for debugging
        # if hasattr(wcett_lb_algorithm, 'path_cache'):
        #     print("WCETT-LB initial paths:")
        #     for (src, dest), path in wcett_lb_algorithm.path_cache.items():
        #         if len(path) > 0:
        #             print(f"  {src} → {dest}: {path}")
        
        logging.info(f"WCETT-LB routing tables created for {len(self.network.nodes)} nodes")
        return True
    
    def wcett_lb_adv_sim(self):
        """
        Define all routing tables using WCETT-LB Advanced metric algorithm. 
        The destination should be the IGW nodes' id.
        """
        igw_nodes = [node_id for node_id, node in self.network.nodes.items() 
                if node.type == "IGW"]
        if not igw_nodes: 
            logging.error("NO IGW in network")
            return False
        
        wcett_lb_adv_algorithm = routing.WCETT_LB_ADVRouting()
        self.network.routing_algorithm = wcett_lb_adv_algorithm
        
        for node_id, node in self.network.nodes.items():
            node.routing_table = {}  # Clear existing routing table
            for igw_id in igw_nodes:
                next_hop = wcett_lb_adv_algorithm.compute_routing_tb(self.network, node_id, igw_id)
                if next_hop is not None:
                    node.routing_table[igw_id] = next_hop
        
        print(f"Is WCETT-LB Advanced Routing Algorithm: {isinstance(self.network.routing_algorithm, routing.WCETT_LB_ADVRouting)}")
        
        # Print path cache for debugging
        if hasattr(wcett_lb_adv_algorithm, 'path_cache'):
            print("WCETT-LB Advanced initial paths:")
            for (src, dest), path in wcett_lb_adv_algorithm.path_cache.items():
                if len(path) > 0:
                    print(f"  {src} → {dest}: {path}")
        
        logging.info(f"WCETT-LB Advanced routing tables created for {len(self.network.nodes)} nodes")
        return True

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    sim = MeshNetworkSimulator(1)
    
    while True:
        print("\nSelect an option:")
        print("1. Run Hop Count")
        print("2. Run WCETT")
        print("3. Run WCETT-LB")
        print("4. Run WCETT-LB Advanced")
        print("5. Exit")
        
        choice = input("Enter: ")
        
        if choice == "1":
            # Run simulation with Hop Count from routing
            if sim.hop_count_sim():
                sim.simulate_traffic()
            else:
                print("Failed")
            break
        elif choice == "2":
            # Run simulation with WCETT from routing
            if sim.wcett_sim():
                sim.simulate_traffic()
            else:
                print("Failed")
            break
        elif choice == "3":
            # Run simulation with WCETT-LB from routing
            if sim.wcett_lb_sim():
                sim.simulate_traffic()
            else:
                print("Failed")
            break
        elif choice == "4":
            # Run simulation with WCETT-LB Advanced from routing
            if sim.wcett_lb_adv_sim():
                sim.simulate_traffic()
            else:
                print("Failed")
            break
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
from complex import initialize_network
import routing
import logging
import time

class MeshNetworkSimulator:
    def __init__(self):
        self.network = initialize_network(x,y,z)
        
    def simulate_traffic(self, duration=10):
        self.network.start_network()
        
        total_packets = 0
        packets_send = 0
        
        start_time = time.time()
    
        try:
            while time.time() - start_time < duration:
                self.network.send_packet(1,1)
        except KeyboardInterrupt:
            print("Simulation interrupted")
        finally:
            self.network.stop_network()
            elapsed = time.time() - start_time
            print("\n=== Simulation Results ===")
            print(f'Duration: {elapsed:.1f} seconds')
            print(f'Total packets: {total_packets}')
            print(f'Successful packets: {packets_send}')
            print(f'Error rate: {(total_packets - packets_send / total_packets)*100:.1f}%')
    
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
        
        for node_id, node in self.network.nodes.items():
            for igw_id in igw_nodes:
                next_hop = routing.HopCountRouting().compute_routing_tb(self.network, node_id, igw_id)
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
        
        for node_id, node in self.network.nodes.items():
            for igw_id in igw_nodes:
                next_hop = routing.WCETTRouting().compute_routing_tb(self.network, node_id, igw_id)
                if next_hop is not None:
                    node.routing_table[igw_id] = next_hop
        
        logging.info(f"WCETT routing tables created for {len(self.network.nodes)} nodes")
        return True

def main(x, y, z):
    """
    Args:
        x (int): Number of IGWs.
        y (int): Number of APs.
        z (int): Number of Clients.
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    sim = MeshNetworkSimulator()
    
    while True:
        print("\nSelect an option:")
        print("1. Run Hop Count")
        print("2. Run WCETT")
        print("3. Run WCETT-LB")
        print("4. Exit")
        
        choice = input("Enter 1, 2, 3 or 4: ")
        
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
            # Run simulation with WCETT-LB from routing (not implemented yet)
            break
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    x = 1  # Number of IGWs
    y = 6  # Number of Routers
    z = 20 # Number of Clients
    main(x, y, z)
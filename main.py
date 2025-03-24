from complex_network import initialize_network
import routing
import logging
import time
import random as rnd

class MeshNetworkSimulator:
    def __init__(self):
        self.network = initialize_network()
        
    def simulate_traffic(self, duration=60):
        self.network.start_network()
        time.sleep(5)
        
        total_packets = 0
        packets_sent = 0
        
        start_time = time.time()
        
        c_nodes = [node_id for node_id, node in self.network.nodes.items() 
            if node.type == "C"]
        igw_nodes = [node_id for node_id, node in self.network.nodes.items() 
            if node.type == "IGW"]
    
        try:
            while time.time() - start_time < duration:
                src_id = rnd.choice(c_nodes)
                dst_id = rnd.choice(igw_nodes)
                total_packets += 1
                
                src_node = self.network.nodes[src_id]
                route = src_node.routing_table.get(dst_id)
                if not route:
                    logging.error(f"No route found from node {src_id} to IGW {dst_id}")
                    continue
                
                route_success = True
                
                for i in range(len(route) - 1):
                    result = self.network.send_packet_graph(route[i], route[i+1])
                    if not result.get("success"):
                        logging.error(f"Packet transmission failed between node {route[i]} and node {route[i+1]}: Reason - {result.get('reason', 'unknown')}")
                        route_success = False
                        break
                    
                if route_success:
                    packets_sent += 1
                    logging.info(f"Packet from {src_id} to {dst_id} result: {result}")
                # progess every 100 packets
                if total_packets % 100 == 0:
                    elapsed = time.time() - start_time
                    print(f"Progress: {total_packets} packets, {elapsed:.1f}s elapsed")
        except KeyboardInterrupt:
            print("Simulation interrupted")
        finally:
            self.network.stop_network()
            elapsed = time.time() - start_time
            print("\n=== Simulation Results ===")
            print(f'Duration: {elapsed:.1f} seconds')
            print(f'Total packets: {total_packets}')
            print(f'Successful packets: {packets_sent}')
            print(f'Error rate: {((total_packets - packets_sent) / total_packets)*100:.1f}%')
    
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

def main():
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
    main()
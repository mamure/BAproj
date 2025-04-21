import time
import matplotlib.pyplot as plt
from main import MeshNetworkSimulator
import numpy as np

def run_stress_sim(routing_type, network_type, start_load=5, max_load=30, step=5, duration=60):
    """
    Run network stress test and generate graphs similar to the reference examples.
    
    Args:
        routing_type: 'hop_count', 'wcett', 'wcett_lb', or 'wcett_lb_adv'
        network_type: 0 for complex_network, 1 for advanced_network
        start_load: Starting packet rate
        max_load: Maximum packet rate
        step: Load increment step
        duration: Test duration per step in seconds
    """
    sim = MeshNetworkSimulator()
    
    if routing_type == 'hop_count':
        sim.hop_count_sim()
        algo_name = "Hop count"
    elif routing_type == 'wcett':
        sim.wcett_sim()
        algo_name = "WCETT"
    elif routing_type == 'wcett_lb':
        sim.wcett_lb_sim()
        algo_name = "WCETT-LB"
    elif routing_type == 'wcett_lb_adv':
        sim.wcett_lb_adv_sim()
        algo_name = "WCETT-LB Advanced"
        
    loads = np.arange(start_load, max_load + step, step)
    throughputs = []
    delays = []
    
    for load in loads:
        print(f"\n--- Testing {algo_name} with load: {load} pkts/sec ---")
        
        start_time = time.time()
        packet_times = {}
        packet_sizes = {}
        total_packets = 0
        delivered_packets = 0
        
        def send_packet_thread(packet_id, src_id, dest_id):
            nonlocal delivered_packets, packet_times, packet_sizes
            
            send_time = time.time()
            packet_times[packet_id] = {'send': send_time}
            packet_sizes[packet_id] = 1024
            
            priority = 3 if np.random.random() < 0.1 else 1
            result = sim.network.send_packet_graph(src_id, dest_id, priority)
            
            if result.get('success'):
                delivered_packets += 1
                packet_times[packet_id]['receive'] = time.time()
        
        # Run simulation
        sim.simulate_traffic(duration=duration, load=load)
        
        # Calculate metrics
        elapsed = time.time() - start_time
        
        # Calculate throughput (packets per second)
        throughput = delivered_packets / elapsed if elapsed > 0 else 0
        throughputs.append(throughput)
        
        # Calculate average end-to-end delay
        total_delay = 0
        count = 0
        for pid, times in packet_times.items():
            if 'receive' in times:
                delay = times['receive'] - times['send']
                total_delay += delay
                count += 1
        
        avg_delay = total_delay / count if count > 0 else 0
        delays.append(avg_delay)
        
        print(f"Load: {load} pkts/sec, Throughput: {throughput:.2f} pkts/sec, Delay: {avg_delay:.4f} sec")
    
    # Create throughput graph
    plt.figure(figsize=(10, 6))
    plt.plot(loads, throughputs, 'o-', linewidth=2, markersize=8)
    plt.xlabel("Load (pkts/sec)")
    plt.ylabel("Throughput (pkts)")
    plt.title(f"{algo_name} Throughput vs Load")
    plt.grid(True)
    plt.savefig(f"{routing_type}_throughput.png")
    plt.close()
    
    # Create delay graph
    plt.figure(figsize=(10, 6))
    plt.plot(loads, delays, 'o-', linewidth=2, markersize=8)
    plt.xlabel("Load (pkts/sec)")
    plt.ylabel("End-to-end delay (second)")
    plt.title(f"{algo_name} End-to-End Delay vs Load")
    plt.grid(True)
    plt.savefig(f"{routing_type}_delay.png")
    plt.close()
    
    return loads, throughputs, delays

def compare_routing_algorithms(network_type):
    """Compare multiple routing algorithms on the same graphs"""
    
    algorithms = [
        ('hop_count', 'Hop count'),
        ('wcett_lb', 'WCETT-LB')
    ]
    
    # Storage for results
    all_results = {}
    
    # Run tests for each algorithm
    for routing_type, name in algorithms:
        print(f"\n=== Testing {name} ===")
        loads, throughputs, delays = run_stress_sim(
            routing_type=routing_type, 
            network_type=network_type
        )
        all_results[name] = {
            'loads': loads,
            'throughputs': throughputs,
            'delays': delays
        }
    
    # Create comparison throughput graph
    plt.figure(figsize=(10, 6))
    for name, results in all_results.items():
        plt.plot(results['loads'], results['throughputs'], 'o-', linewidth=2, label=name)
    plt.xlabel("Load (pkts/sec)")
    plt.ylabel("Throughput (pkts)")
    plt.title("Routing Algorithm Throughput Comparison")
    plt.legend()
    plt.grid(True)
    plt.savefig("routing_throughput_comparison.png")
    plt.show()
    
    # Create comparison delay graph
    plt.figure(figsize=(10, 6))
    for name, results in all_results.items():
        plt.plot(results['loads'], results['delays'], 'o-', linewidth=2, label=name)
    plt.xlabel("Load (pkts/sec)")
    plt.ylabel("End-to-end delay (second)")
    plt.title("Routing Algorithm End-to-End Delay Comparison")
    plt.legend()
    plt.grid(True)
    plt.savefig("routing_delay_comparison.png")
    plt.show()

if __name__ == "__main__":
    # Run comparison for both simple and advanced networks
    print("Testing on advanced network (type 1)")
    compare_routing_algorithms(1)
    
    print("\nTesting on complex network (type 0)")
    compare_routing_algorithms(0)
import matplotlib.pyplot as plt
from main import MeshNetworkSimulator
from network import reset_id_managers

def run_all_experiments():
    loads = [5, 10, 20, 25, 40, 50]
    
    hop_count_results = {'er': [], 'throughput': [], 'delay': []}
    wcett_results = {'er': [], 'throughput': [], 'delay': []}
    wcett_lb_results = {'er': [], 'throughput': [], 'delay': []}
    
    # Hop Count
    sim = MeshNetworkSimulator(0)
    sim.hop_count_sim()
    for load in loads:
        print(f'\nHop Count Sim with load {load} pkt/s')
        er, throughput, delay = sim.simulate_traffic(duration=180, load=load)
        hop_count_results['er'].append(er)
        hop_count_results['throughput'].append(throughput)
        hop_count_results['delay'].append(delay)
    
    # WCETT
    sim = MeshNetworkSimulator(0)
    sim.wcett_sim()
    for load in loads:
        print(f'\nWCETT Sim with load {load} pkt/s')
        er, throughput, delay = sim.simulate_traffic(duration=180, load=load)
        wcett_results['er'].append(er)
        wcett_results['throughput'].append(throughput)
        wcett_results['delay'].append(delay)
    
    # WCETT-LB
    sim = MeshNetworkSimulator(0)
    sim.wcett_lb_sim()
    for load in loads:
        print(f'\nWCETT-LB Sim with load {load} pkt/s')
        er, throughput, delay = sim.simulate_traffic(duration=180, load=load)
        wcett_lb_results['er'].append(er)
        wcett_lb_results['throughput'].append(throughput)
        wcett_lb_results['delay'].append(delay)
        
    
    # Create a figure with 3 subplots
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 15))
    
    # Plot Error Rate
    ax1.plot(loads, hop_count_results['er'], marker='o', label='Hop Count')
    ax1.plot(loads, wcett_results['er'], marker='s', label='WCETT')
    ax1.plot(loads, wcett_lb_results['er'], marker='^', label='WCETT-LB')
    ax1.set_xlabel("Load (pkts/sec)")
    ax1.set_ylabel("Error rate (%)")
    ax1.set_title("Error Rate Comparison")
    ax1.legend()
    ax1.grid(True)
    
    # Plot Throughput
    ax2.plot(loads, hop_count_results['throughput'], marker='o', label='Hop Count')
    ax2.plot(loads, wcett_results['throughput'], marker='s', label='WCETT')
    ax2.plot(loads, wcett_lb_results['throughput'], marker='^', label='WCETT-LB')
    ax2.set_xlabel("Load (pkts/sec)")
    ax2.set_ylabel("Throughput (Kbps)")
    ax2.set_title("Throughput Comparison")
    ax2.legend()
    ax2.grid(True)
    
    # Plot End-to-End Delay
    ax3.plot(loads, hop_count_results['delay'], marker='o', label='Hop Count')
    ax3.plot(loads, wcett_results['delay'], marker='s', label='WCETT')
    ax3.plot(loads, wcett_lb_results['delay'], marker='^', label='WCETT-LB')
    ax3.set_xlabel("Load (pkts/sec)")
    ax3.set_ylabel("End-to-End Delay (s)")
    ax3.set_title("End-to-End Delay Comparison")
    ax3.legend()
    ax3.grid(True)
    
    plt.tight_layout()
    plt.savefig("routing_performance_comparison.png")
    plt.show()
    
    print(f'Hop count results: {hop_count_results}')
    print(f'WCETT results: {wcett_results}')
    print(f'WCETT-LB results: {wcett_lb_results}')

if __name__ == "__main__":
    run_all_sims()
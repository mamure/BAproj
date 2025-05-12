import matplotlib.pyplot as plt
from main import MeshNetworkSimulator
from network import reset_id_managers

def run_all_sims():
    loads = [5, 10, 20, 30, 35]
    
    hop_count_results = {'er': [], 'throughput': [], 'delay': []}
    wcett_results = {'er': [], 'throughput': [], 'delay': []}
    wcett_lb_post_results = {'er': [], 'throughput': [], 'delay': []}
    wcett_lb_pre_results = {'er': [], 'throughput': [], 'delay': []}
    
    reset_id_managers()
    
    # Hop Count
    sim = MeshNetworkSimulator(0)
    sim.hop_count_sim()
    for load in loads:
        print(f'\nHop Count Sim with load {load} pkt/s')
        er, throughput, delay = sim.simulate_traffic(duration=180, load=load)
        hop_count_results['er'].append(er)
        hop_count_results['throughput'].append(throughput)
        hop_count_results['delay'].append(delay)
        
    reset_id_managers()
    
    # WCETT
    sim = MeshNetworkSimulator(0)
    sim.wcett_sim()
    for load in loads:
        print(f'\nWCETT Sim with load {load} pkt/s')
        er, throughput, delay = sim.simulate_traffic(duration=180, load=load)
        wcett_results['er'].append(er)
        wcett_results['throughput'].append(throughput)
        wcett_results['delay'].append(delay)
        
    reset_id_managers()
    
    # WCETT-LB Post
    sim = MeshNetworkSimulator(0)
    sim.wcett_lb_post_sim()
    for load in loads:
        print(f'\nWCETT-LB Post Sim with load {load} pkt/s')
        er, throughput, delay = sim.simulate_traffic(duration=180, load=load)
        wcett_lb_post_results['er'].append(er)
        wcett_lb_post_results['throughput'].append(throughput)
        wcett_lb_post_results['delay'].append(delay)
    
    reset_id_managers()
    
    # WCETT-LB Pre
    sim = MeshNetworkSimulator(0)
    sim.wcett_lb_pre_sim()
    for load in loads:
        print(f'\nWCETT-LB Pre Sim with load {load} pkt/s')
        er, throughput, delay = sim.simulate_traffic(duration=180, load=load)
        wcett_lb_pre_results['er'].append(er)
        wcett_lb_pre_results['throughput'].append(throughput)
        wcett_lb_pre_results['delay'].append(delay)
    
    # Plot Error Rate
    plt.figure(figsize=(10, 6))
    plt.plot(loads, hop_count_results['er'], marker='o', label='Hop Count')
    plt.plot(loads, wcett_results['er'], marker='s', label='WCETT')
    plt.plot(loads, wcett_lb_post_results['er'], marker='^', label='WCETT-LB Post')
    plt.plot(loads, wcett_lb_pre_results['er'], marker='P', label='WCETT-LB Pre')
    plt.xlabel("Load (pkts/sec)")
    plt.ylabel("Error rate (%)")
    plt.title("Error Rate Comparison")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("error_rate_comparison.png")
    
    # Plot Throughput
    plt.figure(figsize=(10, 6))
    plt.plot(loads, hop_count_results['throughput'], marker='o', label='Hop Count')
    plt.plot(loads, wcett_results['throughput'], marker='s', label='WCETT')
    plt.plot(loads, wcett_lb_post_results['throughput'], marker='^', label='WCETT-LB Post')
    plt.plot(loads, wcett_lb_pre_results['throughput'], marker='P', label='WCETT-LB Pre')
    plt.xlabel("Load (pkts/sec)")
    plt.ylabel("Throughput (Kbps)")
    plt.title("Throughput Comparison")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("throughput_comparison.png")
    
    # Plot End-to-End Delay
    plt.figure(figsize=(10, 6))
    plt.plot(loads, hop_count_results['delay'], marker='o', label='Hop Count')
    plt.plot(loads, wcett_results['delay'], marker='s', label='WCETT')
    plt.plot(loads, wcett_lb_post_results['delay'], marker='^', label='WCETT-LB Post')
    plt.plot(loads, wcett_lb_pre_results['delay'], marker='P', label='WCETT-LB Pre')
    plt.xlabel("Load (pkts/sec)")
    plt.ylabel("End-to-End Delay (s)")
    plt.title("End-to-End Delay Comparison")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("delay_comparison.png")
    
    plt.show()
    
    print(f'Hop count results: {hop_count_results}')
    print(f'WCETT results: {wcett_results}')
    print(f'WCETT-LB Post results: {wcett_lb_post_results}')
    print(f'WCETT-LB Pre results: {wcett_lb_pre_results}')

if __name__ == "__main__":
    run_all_sims()
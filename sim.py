import matplotlib.pyplot as plt
from main import MeshNetworkSimulator

def run_all_experiments():
    loads = [25, 50, 100, 150, 200]
    
    hop_count_er = []
    wcett_er = []
    wcett_lb_er = []
    
    # Hop Count
    sim = MeshNetworkSimulator()
    sim.hop_count_sim()
    for load in loads:
        print(f'\nHop Count Sim with load {load} pkt/s')
        er = sim.simulate_traffic(duration=60, load=load)
        hop_count_er.append(er)
    
    # WCETT
    sim = MeshNetworkSimulator()
    sim.wcett_sim()
    for load in loads:
        print(f'\nWCETT Sim with load {load} pkt/s')
        er = sim.simulate_traffic(duration=60, load=load)
        wcett_er.append(er)
    
    # WCETT-LB
    sim = MeshNetworkSimulator()
    sim.wcett_lb_sim()
    for load in loads:
        print(f'\nWCETT-LB Sim with load {load} pkt/s')
        er = sim.simulate_traffic(duration=60, load=load)
        wcett_lb_er.append(er)
    
    # Now plot the results
    plt.plot(loads, hop_count_er, marker='o', label='Hop Count')
    plt.plot(loads, wcett_er, marker='s', label='WCETT')
    plt.plot(loads, wcett_lb_er, marker='^', label='WCETT-LB')
    
    plt.xlabel("Load (pkts/sec)")
    plt.ylabel("Error rate")
    plt.title("Routing Algorithm Comparison")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    run_all_experiments()
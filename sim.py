import matplotlib.pyplot as plt
from main import MeshNetworkSimulator
from network import reset_id_managers

def run_all_experiments():
    loads = [5, 10, 20, 25, 40, 50]
    
    hop_count_er = []
    wcett_er = []
    wcett_lb_er = []
    wcett_lb_adv_er = []
    
    reset_id_managers()
    
    # Hop Count
    sim = MeshNetworkSimulator(0)
    sim.hop_count_sim()
    for load in loads:
        print(f'\nHop Count Sim with load {load} pkt/s')
        er = sim.simulate_traffic(duration=120, load=load)
        hop_count_er.append(er)
        
    reset_id_managers()
    
    # WCETT
    sim = MeshNetworkSimulator(0)
    sim.wcett_sim()
    for load in loads:
        print(f'\nWCETT Sim with load {load} pkt/s')
        er = sim.simulate_traffic(duration=120, load=load)
        wcett_er.append(er)
        
    reset_id_managers()
    
    # WCETT-LB
    sim = MeshNetworkSimulator(0)
    sim.wcett_lb_sim()
    for load in loads:
        print(f'\nWCETT-LB Sim with load {load} pkt/s')
        er = sim.simulate_traffic(duration=120, load=load)
        wcett_lb_er.append(er)
    
    reset_id_managers()
    
    # WCETT-LB Advandced
    sim = MeshNetworkSimulator(0)
    sim.wcett_lb_adv_sim()
    for load in loads:
        print(f'\nWCETT-LB Advanced Sim with load {load} pkt/s')
        er = sim.simulate_traffic(duration=120, load=load)
        wcett_lb_adv_er.append(er)
        
    print(f"Hop count results: {hop_count_er}")
    print(f"WCETT results: {wcett_er}")
    print(f"WCETT-LB results: {wcett_lb_er}")
    print(f"WCETT-LB Advanced results: {wcett_lb_adv_er}")
    
    # Now plot the results
    plt.plot(loads, hop_count_er, marker='o', label='Hop Count')
    plt.plot(loads, wcett_er, marker='s', label='WCETT')
    plt.plot(loads, wcett_lb_er, marker='^', label='WCETT-LB')
    plt.plot(loads, wcett_lb_adv_er, marker='h', label='WCETT-LB Advanced')
    
    plt.xlabel("Load (pkts/sec)")
    plt.ylabel("Error rate")
    plt.title("Routing Algorithm Comparison")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    run_all_experiments()
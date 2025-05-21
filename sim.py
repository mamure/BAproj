import matplotlib.pyplot as plt
import argparse
import os
import json
import time
from main import MeshNetworkSimulator
from network import reset_id_managers
from log_config import setup_logging, get_logger

logger = get_logger("sim")

def generate_load_series(base_load=5):
    """
    Generate a series of loads following the specified increment pattern.
    
    Args:
        base_load (float, optional): Starting load value. Defaults to 5.
    
    Returns:
        list: List of loads [base_load, base_load+5, base_load+15, base_load+25, base_load+30]
    """
    return [
        base_load,
        base_load + 5,
        base_load + 15,
        base_load + 25,
        base_load + 30
    ]

def run_all_sims(base_load=5, duration=180, topology=0, save_dir=None, show_plots=True):
    """
    Run simulations for all routing algorithms with configurable parameters.
    
    Args:
        base_load (float, optional): Starting load in packets/second. Defaults to 5. Other loads will follow the pattern:
                                    [base_load, base_load+5, base_load+15, base_load+25, base_load+30]
        duration (int, optional): Duration for each simulation in seconds. Defaults to 180.
        topology (int, optional): Network topology to use (0=small, 1=big). Defaults to 0.
        save_dir (str, optional): Directory to save results and plots. Defaults to None (current directory).
        show_plots (bool, optional): Whether to display plots. Defaults to True.
    
    Returns:
        dict: Dictionary containing the simulation results for all algorithms
    """
    loads = generate_load_series(base_load)
    topology_name = "small" if topology == 0 else "big"
    
    # Generate timestamp in MMDDHHMM format
    timestamp = time.strftime("%m%d%H%M")
    
    if save_dir:
        base_results_dir = os.path.join(save_dir, "simulation_results")
    else:
        base_results_dir = "simulation_results"
    
    os.makedirs(base_results_dir, exist_ok=True)
    results_dir = os.path.join(base_results_dir, f'results_{timestamp}')
    os.makedirs(results_dir, exist_ok=True)
    
    # Initialize results dictionaries
    hop_count_results = {'er': [], 'throughput': [], 'delay': []}
    wcett_results = {'er': [], 'throughput': [], 'delay': []}
    wcett_lb_post_results = {'er': [], 'throughput': [], 'delay': []}
    wcett_lb_pre_results = {'er': [], 'throughput': [], 'delay': []}
    
    # Run all simulations
    logger.info(f"=== Running simulations with {topology_name} topology, duration={duration}s ===")
    logger.info(f"Load series: {loads} packets/second")
    
    # Hop Count simulations
    reset_id_managers()
    sim = MeshNetworkSimulator(topology)
    sim.hop_count_sim()
    for load in loads:
        logger.info(f'Hop Count Sim with load {load} pkt/s')
        er, throughput, delay = sim.simulate_traffic(duration=duration, load=load)
        hop_count_results['er'].append(er)
        hop_count_results['throughput'].append(throughput)
        hop_count_results['delay'].append(delay)
    
    logger.debug("Cleaning up Hop-count simulator")
    del sim # forcing python arbage collection
        
    # WCETT simulations
    reset_id_managers()
    sim = MeshNetworkSimulator(topology)
    sim.wcett_sim()
    for load in loads:
        logger.info(f'WCETT Sim with load {load} pkt/s')
        er, throughput, delay = sim.simulate_traffic(duration=duration, load=load)
        wcett_results['er'].append(er)
        wcett_results['throughput'].append(throughput)
        wcett_results['delay'].append(delay)
    
    logger.debug("Cleaning up WCETT simulator")
    del sim
        
    # WCETT-LB Post simulations
    reset_id_managers()
    sim = MeshNetworkSimulator(topology)
    sim.wcett_lb_post_sim()
    for load in loads:
        logger.info(f'WCETT-LB Post Sim with load {load} pkt/s')
        er, throughput, delay = sim.simulate_traffic(duration=duration, load=load)
        wcett_lb_post_results['er'].append(er)
        wcett_lb_post_results['throughput'].append(throughput)
        wcett_lb_post_results['delay'].append(delay)
    
    logger.debug("Cleaning up WCETT-LB Post simulator")
    del sim
    
    # WCETT-LB Pre simulations
    reset_id_managers()
    sim = MeshNetworkSimulator(topology)
    sim.wcett_lb_pre_sim()
    for load in loads:
        logger.info(f'WCETT-LB Pre Sim with load {load} pkt/s')
        er, throughput, delay = sim.simulate_traffic(duration=duration, load=load)
        wcett_lb_pre_results['er'].append(er)
        wcett_lb_pre_results['throughput'].append(throughput)
        wcett_lb_pre_results['delay'].append(delay)

    logger.debug("Cleaning up WCETT-LB Pre simulator")
    del sim
    
    # Create plots
    # Plot Error Rate
    plt.figure(figsize=(10, 6))
    plt.plot(loads, hop_count_results['er'], marker='o', label='Hop Count')
    plt.plot(loads, wcett_results['er'], marker='s', label='WCETT')
    plt.plot(loads, wcett_lb_post_results['er'], marker='^', label='WCETT-LB Post')
    plt.plot(loads, wcett_lb_pre_results['er'], marker='P', label='WCETT-LB Pre')
    plt.xlabel("Load (pkts/sec)")
    plt.ylabel("Error rate (%)")
    plt.title(f"Error Rate Comparison ({topology_name} topology, {duration}s)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, "error_rate_comparison.png"))
    
    # Plot Throughput
    plt.figure(figsize=(10, 6))
    plt.plot(loads, hop_count_results['throughput'], marker='o', label='Hop Count')
    plt.plot(loads, wcett_results['throughput'], marker='s', label='WCETT')
    plt.plot(loads, wcett_lb_post_results['throughput'], marker='^', label='WCETT-LB Post')
    plt.plot(loads, wcett_lb_pre_results['throughput'], marker='P', label='WCETT-LB Pre')
    plt.xlabel("Load (pkts/sec)")
    plt.ylabel("Throughput (Kbps)")
    plt.title(f"Throughput Comparison ({topology_name} topology, {duration}s)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, "throughput_comparison.png"))
    
    # Plot End-to-End Delay
    plt.figure(figsize=(10, 6))
    plt.plot(loads, hop_count_results['delay'], marker='o', label='Hop Count')
    plt.plot(loads, wcett_results['delay'], marker='s', label='WCETT')
    plt.plot(loads, wcett_lb_post_results['delay'], marker='^', label='WCETT-LB Post')
    plt.plot(loads, wcett_lb_pre_results['delay'], marker='P', label='WCETT-LB Pre')
    plt.xlabel("Load (pkts/sec)")
    plt.ylabel("End-to-End Delay (s)")
    plt.title(f"End-to-End Delay Comparison ({topology_name} topology, {duration}s)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, "delay_comparison.png"))
    
    if show_plots:
        plt.show()
    
    # Gather all results
    all_results = {
        'parameters': {
            'timestamp': timestamp,
            'topology': topology_name,
            'duration': duration,
            'loads': loads
        },
        'hop_count': hop_count_results,
        'wcett': wcett_results,
        'wcett_lb_post': wcett_lb_post_results,
        'wcett_lb_pre': wcett_lb_pre_results
    }
    
    # Save results to JSON file
    with open(os.path.join(results_dir, "simulation_results.json"), 'w') as f:
        json.dump(all_results, f, indent=2)
    
    # logger.info summary
    logger.info("=== Simulation Complete ===")
    logger.info(f"Results saved to: {results_dir}")
    logger.info(f"Timestamp: {timestamp}")
    logger.info(f"Topology: {topology_name}")
    logger.info(f"Duration: {duration} seconds per simulation")
    logger.info(f"Loads tested: {loads}")
    
    return all_results

def run_single_algorithm_sim(algorithm, base_load=5, duration=180, topology=0, save_dir=None, show_plots=True):
    """
    Run simulations for a single routing algorithm.
    
    Args:
        algorithm (str): Routing algorithm to use ('hop', 'wcett', 'wcett_lb_post', or 'wcett_lb_pre')
        base_load (float, optional): Starting load in packets/second. Defaults to 5. Other loads will follow the pattern:
                                    [base_load, base_load+5, base_load+15, base_load+25, base_load+30]
        duration (int, optional): Duration for each simulation in seconds. Defaults to 180.
        topology (int, optional): Network topology to use (0=small, 1=big). Defaults to 0.
        save_dir (str, optional): Directory to save results and plots. Defaults to None.
        show_plots (bool, optional): Whether to display plots. Defaults to True.
        
    Returns:
        dict: Dictionary containing the results for the algorithm
    """
    # Generate loads based on the base_load parameter
    loads = generate_load_series(base_load)
    topology_name = "small" if topology == 0 else "big"
    
    # Generate timestamp in MMDDHHMM format
    timestamp = time.strftime("%m%d%H%M")
    
    if save_dir:
        base_results_dir = os.path.join(save_dir, "simulation_results")
    else:
        base_results_dir = "simulation_results"
    
    os.makedirs(base_results_dir, exist_ok=True)
    results_dir = os.path.join(base_results_dir, f'results_{timestamp}')
    os.makedirs(results_dir, exist_ok=True)
    
    # Initialize results
    results = {'er': [], 'throughput': [], 'delay': []}
    
    # Map algorithm name to method
    algorithm_methods = {
        'hop': lambda sim: sim.hop_count_sim(),
        'wcett': lambda sim: sim.wcett_sim(),
        'wcett_lb_post': lambda sim: sim.wcett_lb_post_sim(),
        'wcett_lb_pre': lambda sim: sim.wcett_lb_pre_sim()
    }
    
    algorithm_names = {
        'hop': 'Hop Count',
        'wcett': 'WCETT',
        'wcett_lb_post': 'WCETT-LB Post',
        'wcett_lb_pre': 'WCETT-LB Pre'
    }
    
    if algorithm not in algorithm_methods:
        logger.debug(f"Unknown algorithm: {algorithm}")
        logger.debug(f"Valid options are: {', '.join(algorithm_methods.keys())}")
        return None
    
    logger.info(f"=== Running {algorithm_names[algorithm]} simulation with {topology_name} topology ===")
    logger.info(f"Load series: {loads} packets/second")
    
    reset_id_managers()
    sim = MeshNetworkSimulator(topology)
    algorithm_methods[algorithm](sim)
    
    for load in loads:
        logger.info(f"{algorithm_names[algorithm]} Sim with load {load} pkt/s")
        er, throughput, delay = sim.simulate_traffic(duration=duration, load=load)
        results['er'].append(er)
        results['throughput'].append(throughput)
        results['delay'].append(delay)
    
    # Create plots
    plt.figure(figsize=(10, 6))
    plt.plot(loads, results['er'], marker='o')
    plt.xlabel("Load (pkts/sec)")
    plt.ylabel("Error rate (%)")
    plt.title(f"{algorithm_names[algorithm]} Error Rate ({topology_name} topology, {duration}s)")
    plt.grid(True)
    plt.savefig(os.path.join(results_dir, f"{algorithm}_error_rate.png"))
    
    plt.figure(figsize=(10, 6))
    plt.plot(loads, results['throughput'], marker='s')
    plt.xlabel("Load (pkts/sec)")
    plt.ylabel("Throughput (Kbps)")
    plt.title(f"{algorithm_names[algorithm]} Throughput ({topology_name} topology, {duration}s)")
    plt.grid(True)
    plt.savefig(os.path.join(results_dir, f"{algorithm}_throughput.png"))
    
    plt.figure(figsize=(10, 6))
    plt.plot(loads, results['delay'], marker='^')
    plt.xlabel("Load (pkts/sec)")
    plt.ylabel("End-to-End Delay (s)")
    plt.title(f"{algorithm_names[algorithm]} End-to-End Delay ({topology_name} topology, {duration}s)")
    plt.grid(True)
    plt.savefig(os.path.join(results_dir, f"{algorithm}_delay.png"))
    
    if show_plots:
        plt.show()
    
    # Save results
    all_results = {
        'parameters': {
            'timestamp': timestamp,
            'algorithm': algorithm,
            'topology': topology_name,
            'duration': duration,
            'loads': loads
        },
        'results': results
    }
    
    with open(os.path.join(results_dir, f"{algorithm}_results.json"), 'w') as f:
        json.dump(all_results, f, indent=2)
    
    logger.info(f"=== {algorithm_names[algorithm]} Simulation Complete ===")
    logger.info(f"Results saved to: {results_dir}")
    logger.info(f"Timestamp: {timestamp}")
    
    return results

def main():
    """
    Main entry point for the simulation script.
    Parses command-line arguments and runs the specified simulation.
    """
    parser = argparse.ArgumentParser(description='Wireless Mesh Network Performance Comparison')
    
    parser.add_argument('-a', '--algorithm', type=str,
                        choices=['hop', 'wcett', 'wcett_lb_post', 'wcett_lb_pre', 'all'],
                        default='all', help='Routing algorithm to simulate (default: all)')
    parser.add_argument('-b', '--base_load', type=float, default=5,
                        help='Base load in packets/second (default: 5). The simulation will test: '
                             'base_load, base_load+5, base_load+15, base_load+25, base_load+30')
    parser.add_argument('-d', '--duration', type=int, default=180,
                        help='Simulation duration in seconds (default: 180)')
    parser.add_argument('-t', '--topology', type=int, choices=[0, 1], default=0,
                        help='Network topology: 0=small, 1=big (default: 0)')
    parser.add_argument('-o', '--output', type=str, help='Directory to save results')
    parser.add_argument('--no-show', action='store_true',
                        help='Do not display plots (just save them)')
    
    args = parser.parse_args()
    
    if args.algorithm == 'all':
        run_all_sims(base_load=args.base_load, duration=args.duration, topology=args.topology,
                     save_dir=args.output, show_plots=not args.no_show)
    else:
        run_single_algorithm_sim(args.algorithm, base_load=args.base_load, duration=args.duration,
                                 topology=args.topology, save_dir=args.output, 
                                 show_plots=not args.no_show)

if __name__ == "__main__":
    # If run directly without arguments, use the default settings
    import sys
    if len(sys.argv) == 1:
        setup_logging()
        run_all_sims()
    else:
        setup_logging()
        main()
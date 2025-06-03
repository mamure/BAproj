import argparse
import json
import os
import time

import matplotlib.pyplot as plt

from log_config import setup_logging, get_logger
from main import MeshNetworkSimulator
from network import reset_id_managers
from routing_alg.routing_utils import (
    CONGESTION_THRESHOLD,
    LOAD_BALANCE_THRESHOLD
)

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
    hop_count_results = {'er': [], 'throughput': [], 'tx': []}
    wcett_results = {'er': [], 'throughput': [], 'tx': []}
    wcett_lb_post_results = {'er': [], 'throughput': [], 'tx': []}
    wcett_lb_pre_results = {'er': [], 'throughput': [], 'tx': []}
    
    # Track highest tx runs for each algorithm
    highest_tx_runs = {
        'hop_count': {'load': 0, 'tx': 0, 'all_tx': []},
        'wcett': {'load': 0, 'tx': 0, 'all_tx': []},
        'wcett_lb_post': {'load': 0, 'tx': 0, 'all_tx': []},
        'wcett_lb_pre': {'load': 0, 'tx': 0, 'all_tx': []}
    }
    
    # Run all simulations
    logger.info(f"=== Running simulations with {topology_name} topology, duration={duration}s ===")
    logger.info(f"Load series: {loads} packets/second")
    
    # Hop Count simulations
    for load in loads:
        logger.info(f'Hop Count Sim with load {load} pkt/s')
        reset_id_managers()
        sim = MeshNetworkSimulator(topology)
        sim.hop_count_sim()
        er, throughput, tx, all_tx = sim.simulate_traffic(duration=duration, load=load)
        hop_count_results['er'].append(er)
        hop_count_results['throughput'].append(throughput)
        hop_count_results['tx'].append(tx)
        
        # Check if this run has higher average transmission time
        if tx > highest_tx_runs['hop_count']['tx']:
            highest_tx_runs['hop_count']['load'] = load
            highest_tx_runs['hop_count']['tx'] = tx
            highest_tx_runs['hop_count']['all_tx'] = all_tx
        
        del sim # forcing python garbage collection
        time.sleep(2)
    
    # WCETT simulations
    for load in loads:
        logger.info(f'WCETT Sim with load {load} pkt/s')
        reset_id_managers()
        sim = MeshNetworkSimulator(topology)
        sim.wcett_sim()
        er, throughput, tx, all_tx = sim.simulate_traffic(duration=duration, load=load)
        wcett_results['er'].append(er)
        wcett_results['throughput'].append(throughput)
        wcett_results['tx'].append(tx)
        
        # Check if this run has higher average transmission time
        if tx > highest_tx_runs['wcett']['tx']:
            highest_tx_runs['wcett']['load'] = load
            highest_tx_runs['wcett']['tx'] = tx
            highest_tx_runs['wcett']['all_tx'] = all_tx
        
        del sim
        time.sleep(2)
    
    # WCETT-LB Post simulations
    for load in loads:
        logger.info(f'WCETT-LB Post Sim with load {load} pkt/s')
        reset_id_managers()
        sim = MeshNetworkSimulator(topology)
        sim.wcett_lb_post_sim()
        er, throughput, tx, all_tx = sim.simulate_traffic(duration=duration, load=load)
        wcett_lb_post_results['er'].append(er)
        wcett_lb_post_results['throughput'].append(throughput)
        wcett_lb_post_results['tx'].append(tx)
        
        # Check if this run has higher average transmission time
        if tx > highest_tx_runs['wcett_lb_post']['tx']:
            highest_tx_runs['wcett_lb_post']['load'] = load
            highest_tx_runs['wcett_lb_post']['tx'] = tx
            highest_tx_runs['wcett_lb_post']['all_tx'] = all_tx
        
        del sim
        time.sleep(2)
    
    # WCETT-LB Pre simulations
    for load in loads:
        logger.info(f'WCETT-LB Pre Sim with load {load} pkt/s')
        reset_id_managers()
        sim = MeshNetworkSimulator(topology)
        sim.wcett_lb_pre_sim()
        er, throughput, tx, all_tx = sim.simulate_traffic(duration=duration, load=load)
        wcett_lb_pre_results['er'].append(er)
        wcett_lb_pre_results['throughput'].append(throughput)
        wcett_lb_pre_results['tx'].append(tx)
        
        # Check if this run has higher average transmission time
        if tx > highest_tx_runs['wcett_lb_pre']['tx']:
            highest_tx_runs['wcett_lb_pre']['load'] = load
            highest_tx_runs['wcett_lb_pre']['tx'] = tx
            highest_tx_runs['wcett_lb_pre']['all_tx'] = all_tx
        
        del sim
        time.sleep(2)
    
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
    
    # Plot End-to-End Transmission time
    plt.figure(figsize=(10, 6))
    plt.plot(loads, hop_count_results['tx'], marker='o', label='Hop Count')
    plt.plot(loads, wcett_results['tx'], marker='s', label='WCETT')
    plt.plot(loads, wcett_lb_post_results['tx'], marker='^', label='WCETT-LB Post')
    plt.plot(loads, wcett_lb_pre_results['tx'], marker='P', label='WCETT-LB Pre')
    plt.xlabel("Load (pkts/sec)")
    plt.ylabel("Transmission Time (s)")
    plt.title(f"Transmission Time Comparison ({topology_name} topology, {duration}s)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, "tx_comparison.png"))
    
    if show_plots:
        plt.show()
    
    # Gather all results
    all_results = {
        'parameters': {
            'timestamp': timestamp,
            'topology': topology_name,
            'duration': duration,
            'Congestion threshold': CONGESTION_THRESHOLD,
            'Load-balancing threshold': LOAD_BALANCE_THRESHOLD,
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
    
    # Generate histograms for the runs with highest average transmission time
    for alg, data in highest_tx_runs.items():
        if alg in ['hop_count', 'wcett']:
            continue
        if data['all_tx']:
            alg_name = {
                'hop_count': 'Hop Count',
                'wcett': 'WCETT',
                'wcett_lb_post': 'WCETT-LB Post',
                'wcett_lb_pre': 'WCETT-LB Pre'
            }[alg]
            
            logger.info(f"Generating transmission time histogram for {alg_name} with load {data['load']} pkt/s")
            generate_trans_histogram(
                data['all_tx'],
                alg_name,
                data['load'],
                topology_name,
                duration,
                results_dir
            )

    return all_results

def run_single_algorithm_sim(algorithm, base_load=5, duration=180, topology=0, save_dir=None, show_plots=True, hist_path=None):
    """
    Run simulations for a single routing algorithm.
    
    Args:
        algorithm (str): Routing algorithm to use ('hop', 'wcett', 'wcett_lb_post', or 'wcett_lb_pre')
        base_load (float, optional): Starting load in packets/second. Defaults to 5.
        duration (int, optional): Duration for each simulation in seconds. Defaults to 180.
        topology (int, optional): Network topology to use (0=small, 1=big). Defaults to 0.
        save_dir (str, optional): Directory to save results and plots. Defaults to None.
        show_plots (bool, optional): Whether to display plots. Defaults to True.
        hist_path (str, optional): Path to save the transmission time histogram. Defaults to None.
        
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
    results = {'er': [], 'throughput': [], 'tx': []}
    
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
    
    # Track the run with highest average transmission time
    highest_tx_run = {
        'load': 0,
        'tx': 0,
        'all_tx': []
    }
    
    for load in loads:
        logger.info(f"{algorithm_names[algorithm]} Sim with load {load} pkt/s")
        reset_id_managers()
        sim = MeshNetworkSimulator(topology)
        algorithm_methods[algorithm](sim)
        er, throughput, tx, all_tx = sim.simulate_traffic(duration=duration, load=load)
        results['er'].append(er)
        results['throughput'].append(throughput)
        results['tx'].append(tx)
        
        # Check if this run has higher average transmission time
        if tx > highest_tx_run['tx']:
            highest_tx_run['load'] = load
            highest_tx_run['tx'] = tx
            highest_tx_run['all_tx'] = all_tx
        
        del sim
        time.sleep(1)
    
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
    plt.plot(loads, results['tx'], marker='^')
    plt.xlabel("Load (pkts/sec)")
    plt.ylabel("Transmission time (s)")
    plt.title(f"{algorithm_names[algorithm]} Transmission time ({topology_name} topology, {duration}s)")
    plt.grid(True)
    plt.savefig(os.path.join(results_dir, f"{algorithm}_tx.png"))
    
    if show_plots:
        plt.show()
    
    # Generate histogram for the run with highest average transmission time
    if highest_tx_run['all_tx'] and algorithm in ['wcett_lb_post', 'wcett_lb_pre']:
        logger.info(f"Generating Transmission Time histogram for {algorithm_names[algorithm]} with load {highest_tx_run['load']} pkt/s")
        generate_trans_histogram(
            highest_tx_run['all_tx'],
            algorithm_names[algorithm],
            highest_tx_run['load'],
            topology_name,
            duration,
            results_dir
        )
    
    # Save results
    all_results = {
        'parameters': {
            'timestamp': timestamp,
            'algorithm': algorithm,
            'topology': topology_name,
            'duration': duration,
            'Congestion threshold': CONGESTION_THRESHOLD,
            'Load-balancing threshold': LOAD_BALANCE_THRESHOLD,
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

def generate_trans_histogram(all_tx, algorithm, load, topology_name, duration, output_path):
    """
    Generate a histogram of end-to-end packet transmission time.
    
    Args:
        all_tx (list): List of packet transmission times in seconds
        algorithm (str): Name of the routing algorithm
        load (float): Network load in packets per second
        topology_name (str): Name of the network topology
        duration (int): Simulation duration in seconds
        output_path (str): Directory to save the histogram
    
    Returns:
        str: Path to the saved histogram file
    """
    if not all_tx:
        logger.warning("No transmission time data available to generate histogram")
        return None
    
    # Convert algorithm name to consistent filename format (lowercase with underscores)
    alg_filename = algorithm.lower().replace(' ', '_').replace('-', '_')
    
    # Save raw data to CSV file
    os.makedirs(output_path, exist_ok=True)
    csv_filename = f"{alg_filename}_tx_data_{int(load)}pps.csv"
    csv_filepath = os.path.join(output_path, csv_filename)
    
    # Write raw transmission time data
    with open(csv_filepath, 'w') as f:
        f.write("packet_id,transmission_time_seconds\n")
        for i, tx_time in enumerate(all_tx):
            f.write(f"{i},{tx_time}\n")
    
    logger.info(f"Raw transmission time data saved to: {csv_filepath}")
        
    plt.figure(figsize=(10, 6))
    plt.hist(all_tx, bins=50, alpha=0.75, edgecolor='black')
    
    # Add mean and median lines
    mean_tx = sum(all_tx) / len(all_tx)
    
    plt.axvline(mean_tx, color='r', linestyle='dashed', linewidth=1, label=f'Mean: {mean_tx:.3f}s')
    
    plt.xlabel("Transmission Time (seconds)")
    plt.ylabel("Number of Packets")
    plt.title(f"{algorithm} Transmission Distribution\n(Load: {load} pkt/s, {topology_name} topology, {duration}s)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Make sure the directory exists
    histogram_filename = f"{alg_filename}_tx_histogram_{int(load)}pps.png"
    histogram_filepath = os.path.join(output_path, histogram_filename)
    plt.savefig(histogram_filepath)
    logger.info(f"Transmission Time histogram saved to: {histogram_filepath}")
    return histogram_filepath
        

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
# Wireless Mesh Network Simulator

This project implements a simulator for evaluating routing algorithms in wireless mesh networks. It was developed as a bachelor's project in Computer Science at the University of Copenhagen (UCPH) in the spring of 2025.

## Project Overview

This simulator allows you to compare the performance of different routing algorithms in wireless mesh networks:

1. **Hop Count** - Traditional shortest path routing based on hop count using Breadth-First Search.
2. **WCETT** - Weighted Cumulative Expected Transmission Time
4. **WCETT-LB Pre** - WCETT with pre congestion awareness load balancing
3. **WCETT-LB Post** - WCETT with post congestion awareness load balancing

The simulator measures and compares:
- **Error Rate** - Percentage of packets that failed to reach destination
- **Throughput** - Network throughput in Kbps
- **End-to-End Transmission Time** - Average time for packets to reach destination

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/mamure/BAproj.git
   cd BAproj
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage Examples

### Running from Command Line

#### Run all simulations with default parameters:
```
python sim.py
```

#### Specify a different base load:
Base load of 10 generates test loads of [10, 15, 25, 35, 40] packets/second:
```
python sim.py -b 10
```

#### Run a specific algorithm with custom settings:
```
python sim.py -a wcett_lb_post -b 15 -d 120
```

#### Run simulations without displaying plots (just save them):
```
python sim.py --no-show
```

#### Change network topology (0=small, 1=big):
```
python sim.py -t 0
```

#### Full help information:
```
python sim.py -h
```

### Running from main.py (interactive mode)

#### Run with interactive menu:
```
python main.py
```

#### Run with command line arguments:
```
python main.py -t 0 -d 60 -l 25
```

## Command Line Arguments

### sim.py options

| Argument | Short | Description |
| --- | --- | --- |
| `--algorithm` | `-a` | Routing algorithm: 'hop', 'wcett', 'wcett_lb_post', 'wcett_lb_pre', or 'all' (default: 'all') |
| `--base-load` | `-b` | Base load in packets/second (default: 5). The simulation tests: [base_load, base_load+5, base_load+15, base_load+25, base_load+30] |
| `--duration` | `-d` | Simulation duration in seconds (default: 180) |
| `--topology` | `-t` | Network topology: 0=complex, 1=advanced (default: 1) |
| `--output` | `-o` | Directory to save results |
| `--no-show` | | Do not display plots (just save them) |

### main.py options

| Argument | Short | Description |
| --- | --- | --- |
| `--topology` | `-t` | Network topology: 0=complex, 1=advanced (default: 1) |
| `--duration` | `-d` | Simulation duration in seconds (default: 30) |
| `--load` | `-l` | Network load in packets per second (default: 50) |
| `--routing` | `-r` | Routing algorithm: 'hop', 'wcett', 'wcett_lb_post', 'wcett_lb_pre' (default: 'hop') |

## Network Topologies

The simulator supports two network topologies:

1. **Small Network** (topology=0): A smaller intricate network topology
2. **Big Network** (topology=1): A larger network with more nodes and varied link characteristics

## Results

Simulation results are saved to:
- A directory named with topology information
- Includes JSON data files with detailed simulation results
- Generates comparison plots for error rate, throughput, and end-to-end transmission time.

## Project Structure

- `main.py` - Main simulator entry point with interactive menu
- `sim.py` - Comprehensive simulation runner for comparing algorithms
- `network.py` - Core network implementation
- `routing_alg/` - Directory containing routing algorithm implementations:
  - `hop_count.py` - Hop count based routing
  - `wcett.py` - WCETT routing implementation
  - `routing_utils.py` - Utility functions for routing algorithms
- `networks/` - Network topology definitions
- `log_config.py` - Logging configuration

## Author

Martin Reich, University of Copenhagen

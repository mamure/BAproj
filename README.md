# BAproj

GitHub repository for my bachelor’s project in Computer Science at UCPH in the spring of 2025.

Deadline: 10.6.2025

# TODO
* Read up on mesh network and wireless mesh network definitions.
* Find a way to simulate a network

# Weekly report
## Week 1 (3-9 feb)
I have looked into the definitions of wireless mesh networks (WMNs) and their components: Internet Gateway (IGW), Access Points (AP), and Client Devices (CD). I have also explored the different architectures of WMNs (Backbone, P2P, and Hybrid). I am still reviewing the definitions and relevant materials to determine which type to use for the simulation.

I have briefly examined the different performance metrics used, such as Hop-count, WCEET, and ETX, and I am still considering which one to use.

On the implementation side, I have looked into using the NetworkX Python library. This library uses graph theory for network analysis, which could be useful for implementing different types of nodes (IGW, AP, CD) and edges with various attributes such as connectivity, error rate, and more.

I found a technical report on NS-3 simulation of mesh networks, which I plan to look into next week.
## Week 2 (10-16 feb)
I have read and found, contrary to my initial assumption, that the routing algorithm is essentially a load-balancing algorithm, depending on the metric I choose. I plan to create/use the following routing metrics for the project:
- Hop-count: All links are counted as 1, and the path with the fewest hops wins, effectively making it a Breadth-First Search. This serves as a baseline metric.
- WCETT: Individual link weights are combined into a path metric, Weighted Cumulative Expected Transmission Time (ETT), which explicitly accounts for interference among links using the same channel. This is a more “information-based” metric and will be used for actual comparison.
- WCETT-LB: An enhancement of WCETT that incorporates load balancing—likely the most relevant algorithm for my project.
- (MIC: Improves WCETT by addressing intra-flow and inter-flow interference?) I might look into this since it also involves load balancing.

Load balancing can be interpreted in different ways—either as always selecting the most optimal route (routing) or ensuring that each router shares the workload evenly. I will follow the paradigm of using routing algorithms that incorporate congestion control/load-balancing awareness within their route calculations.

I’ve implemented a very simple Node and Edge class, which together form a network graph. Next, I’ll create a basic hop-count routing algorithm using Breadth-First Search as a baseline, even though it’s an unoptimized algorithm. I’m considering making the routing algorithms recalculate every 2 seconds, except for hop count, which will only consider direct distance without weighting.

As for performance metrics to compare these algorithms, throughput (kbps) was my first thought, but I’m not entirely sure if it’s the best choice.

I’ve slowly started writing the background section. It’s been a bit difficult at first, mainly because I think I just need to get used to it.
## Week 3 (17-23 feb)
## Week 4 (24 feb-2 mar)
## Week 5 (3-9 mar)
## Week 6 (10-16 mar)
## Week 7 (17-23 mar)
## Week 8 (24-30 mar)
## Week 9 (31 mar-6 apr)
## Week 10 (7-13 apr)
## Week 11 (14-20 apr)
## Week 12 (21-27 apr)
## Week 13 (28 apr-4 may)
## Week 14 (5-11 may)
## Week 15 (12-18 may)
## Week 16 (19-25 may)
## Week 17 (26 may-1 jun)
## Week 18 (2-7 jun)
## Week 19 (8-10 jun)
# BAproj

GitHub repository for my bachelor’s project in Computer Science at UCPH in the spring of 2025.

Deadline: 10.6.2025

# TODO
~~Read up on mesh network and wireless mesh network definitions.~~
Find a way to simulate a network
* See how the hop count can be tested in terms of error rate.

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
This week, I've finished the Hop-count and started working on the WCETT. I'm a bit confused about the broader project scope, specifically how to approach the actual testing and benchmark tests. I think it might become clearer once I've implemented the routing algorithms (WCETT and WCETT-LB) so that the "standalone, not dependent on other implementations" routing algorithms are completed.

I've also been thinking about how "realistic" the testing should be, for example, whether the packet contents should reflect real-life packets or just have arbitrary sizes that simulate realistic packet sending. However, I do know that I will be using ACK packets in the project.

Lastly, I've been writing more concurrently alongside the implementation.
## Week 4 (24 feb-2 mar)
I found a library called Pyvis, which has a nice graph visualizer that I can use to confirm network topology.
The theoretical part of WCETT is implemented, but the actual testing and routing table computation are still missing.
I have implemented socket and packet listening in the nodes.
## Week 5 (3-9 mar)
It’s quite similar to last week. I’ve made more progress with testing and simulation, but some parts are still incomplete.

The current progress is:
* The basic network structure is complete.
* Hop Count routing tables are successfully created.
* The simulation framework runs but doesn’t process packets correctly.

For my own TODO: Before I start on WCETT-LB, I still need to:
* ~~Reduce the packet sending rate.~~
* Fix routing table computations for WCETT and debug.
* ~~Simulate traffic over x seconds.~~
* ~~Debug the packet delivery issue.~~
* ~~Complete the WCETT implementation.~~
* Write more on WCETT in the report.
## Week 6 (10-16 mar)
I’ve fixed some issues with the simulation, making the “complex, non-random network” functional, though it still needs testing to verify packet routing behavior. I’m currently working on determining whether packets follow the expected paths through the network. The feedback on your report has been helpful in guiding the level of detail and explanation. This week, I will focus more on writing than coding to follow up.

I still need to fix the routing table computations for WCETT and continue testing to confirm the packet routing paths.
## Week 7 (17-23 mar)
I have tested and confirmed that WCETT works as expected. However, I still need to fix the actual sending. There are issues with following the routing table and the sending process itself.

There are still many packet timeouts and errors that I need to investigate.

In terms of writing, I have addressed the comments.
## Week 8 (24-30 mar)
I have fixed the routing, so the simulation now runs successfully. However, I still need to implement packet drops when a node’s buffer becomes overrun. Additionally, I have started working on WCETT-LB.

I have also looked into research on hop count but haven’t found anything directly relevant to my work so far. Nevertheless, I will continue searching for useful insights.

Lastly, I have started considering which results I want to produce. I plan to assess the different routing algorithms based on error rate while varying the number of packets per second sent from the clients. 
## Week 9 (31 mar-6 apr)
Focused this week on writing, including both design considerations and architecture, as well as a bit on routing algorithms.

The WCETT-LB implementation is almost complete, but there are still some missing features, such as dropping packets when the buffer or queue is full. I also need to write the section about WCETT-LB.
## Week 10 (7-13 apr)
I’ve finished the WCETT-LB implementation so that it works now. I may still need to fine-tune some parameters, such as when a node is considered congested and when path switching should occur, but that will be more of an optimization task, I think. I’ll also look into how I can produce results beyond just the network error rate.

I’ll need to create some larger (non-random) networks to observe how the algorithms perform at scale, including metrics like throughput and the time it takes to read/write messages. I’d like to test this on networks of different sizes.

I’ve written some notes about WCETT-LB and reviewed some of the comments. I’ll begin the implementation section in week 11.
## Week 11 (14-20 apr)
End of this week have implementation section and background ready-ish

The results of the test i should be able to look at and discuss: error rate at different loads, throughput, end-to-end delay. All at different scales.

Maybe make my own routing LB algorithm?

Found that depending on the network the routing path may went through clients from mesh routers which i did not want so fixed that.
## Week 12 (21-27 apr)
I have made some actual testing that have provided some results that I can begin to comment on (error rate, throughput and end-to-end delay). The test were only done on the small network. I have started looking at "stress" testing the network to see how [finish sentence]. I some bits in he report so it was ready for the peer-review. I have started on looking at the WCETT-LB version originally presented (the one i have made utilizes post congestion detextoin, while the "original" does it pre).
## Week 13 (28 apr-4 may)
## Week 14 (5-11 may)
## Week 15 (12-18 may)
## Week 16 (19-25 may)
## Week 17 (26 may-1 jun)
## Week 18 (2-7 jun)
## Week 19 (8-10 jun)
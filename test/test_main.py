import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import main

class TestPacketRate(unittest.TestCase):
    def setUp(self):
        self.simulator = main.MeshNetworkSimulator(1)
        self.simulator.wcett_lb_pre_sim()

    def test_packet_rate(self):
        """Test if the simulator correctly sends packets at the configured rate"""
        
        def count_packets(duration, load):
            """Run simulation for specified duration and load, return packet count"""
            # Reset packet tracking
            self.simulator.network.start_network()
            
            # Track packets sent
            original_send_packet = self.simulator.network.send_packet_graph
            packet_count = [0]
            
            def counting_send_packet(*args, **kwargs):
                packet_count[0] += 1
                return original_send_packet(*args, **kwargs)
            
            # Replace with counting version
            self.simulator.network.send_packet_graph = counting_send_packet
            
            # Run simulation for short duration
            self.simulator.simulate_traffic(duration=duration, load=load)
            
            # Restore original function
            self.simulator.network.send_packet_graph = original_send_packet
            
            return packet_count[0]
        
        # Test cases
        test_duration = 20  # seconds
        
        # Case 1: Just below 20 packets per second
        load_below = 10
        expected_below = test_duration * load_below
        packets_below = count_packets(test_duration, load_below)
        
        # Allow for small variation (±10%)
        self.assertGreaterEqual(packets_below, expected_below * 0.9, 
                               f"Expected ~{expected_below} packets at {load_below} pps, but got {packets_below}")
        self.assertLessEqual(packets_below, expected_below * 1.1,
                            f"Expected ~{expected_below} packets at {load_below} pps, but got {packets_below}")
        
        # Case 2: Exactly 20 packets per second
        load_exact = 20
        expected_exact = test_duration * load_exact
        packets_exact = count_packets(test_duration, load_exact)
        
        self.assertGreaterEqual(packets_exact, expected_exact * 0.9,
                               f"Expected ~{expected_exact} packets at {load_exact} pps, but got {packets_exact}")
        self.assertLessEqual(packets_exact, expected_exact * 1.1,
                            f"Expected ~{expected_exact} packets at {load_exact} pps, but got {packets_exact}")
        
        # Case 3: Above 20 packets per second
        load_above = 30
        expected_above = test_duration * load_above
        packets_above = count_packets(test_duration, load_above)
        
        self.assertGreaterEqual(packets_above, expected_above * 0.9,
                               f"Expected ~{expected_above} packets at {load_above} pps, but got {packets_above}")
        self.assertLessEqual(packets_above, expected_above * 1.1,
                            f"Expected ~{expected_above} packets at {load_above} pps, but got {packets_above}")
        
        # Verify rates increase as expected
        self.assertLess(packets_below, packets_exact, 
                       "Higher packet rate should result in more packets sent")
        self.assertLess(packets_exact, packets_above, 
                       "Higher packet rate should result in more packets sent")

if __name__ == '__main__':
    unittest.main()
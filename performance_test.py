import unittest
import time
from main import EmergencySimulator, Emergency

class StressAndPerformanceTests(unittest.TestCase):
    def setUp(self):
       
        self.simulator = EmergencySimulator(seed=123)

    def test_high_emergency_rate(self):

        for _ in range(100):  # Simulate 100 emergencies quickly
            self.simulator.life_threatening_emergencies.append(
                Emergency(district=3, start_time=0, prio=1)
            )
            self.simulator.non_life_threatening_emergencies.append(
                Emergency(district=7, start_time=0, prio=0)
            )


        start_time = time.time()
        result = self.simulator.simulate(2)
        end_time = time.time()


        execution_time = end_time - start_time
        print("Stress Test Results (High Emergency Rate):")
        print(f"Simulation Execution Time: {execution_time:.2f} seconds")
        print(f"Doctor Utilization: {result['doc_util']}")
        print(f"Remaining Life-Threatening Emergencies: {len(self.simulator.life_threatening_emergencies)}")
        print(f"Remaining Non-Life-Threatening Emergencies: {len(self.simulator.non_life_threatening_emergencies)}")


        self.assertGreater(result["doc_util"], 0.5, "Doctor utilization is too low under stress.")
        self.assertLessEqual(len(self.simulator.life_threatening_emergencies), 10,
                             "Too many life-threatening emergencies left unprocessed.")
        self.assertLessEqual(len(self.simulator.non_life_threatening_emergencies), 15,
                             "Too many non-life-threatening emergencies left unprocessed.")

    def test_long_duration_performance(self):
        # Simulate for 24 hours
        start_time = time.time()
        result = self.simulator.simulate(24)
        end_time = time.time()


        execution_time = end_time - start_time
        print("Performance Test Results (24-Hour Simulation):")
        print(f"Simulation Execution Time: {execution_time:.2f} seconds")
        print(f"Doctor Utilization: {result['doc_util']}")
        print(f"Doctor Time at Center: {result['doc_center']}")
        print(f"Avg Non-Life-Threatening Waiting Time (mins): {result['avg_non_live_threatening_watiing_time_min']}")


        self.assertLess(execution_time, 10, "Simulation execution time is too high for 24-hour simulation.")
        self.assertGreater(result["doc_util"], 0.5, "Doctor utilization is too low over long duration.")
        self.assertGreater(result["doc_center"], 0, "Doctor should spend some time at the center.")

if __name__ == "__main__":
    unittest.main()

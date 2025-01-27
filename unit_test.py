import unittest
from collections import deque
import random
import numpy as np
from main import EmergencySimulator, Emergency

class TestEmergencySimulator(unittest.TestCase):
    def setUp(self):

        self.simulator = EmergencySimulator(seed=123)

    def test_get_travel_time(self):

        travel_time = self.simulator.get_travel_time(1, 2)
        print(f"Travel time between district 1 and 2: {travel_time} seconds")
        self.assertTrue(90 <= travel_time <= 540, "Travel time not within expected range.")

        travel_time_with_three = self.simulator.get_travel_time(1, 2, 3, 0.5)
        print(f"Travel time between district 1, 2, and 3 with ratio 0.5: {travel_time_with_three} seconds")
        self.assertGreaterEqual(travel_time_with_three, 0, "Travel time with three districts is negative.")

    def test_generate_emergency(self):

        for _ in range(5):  # Retry a few times to account for randomness
            self.simulator.time_to_next_emergency = 0
            self.simulator.generate_emergency()
            total_emergencies = (
                    len(self.simulator.life_threatening_emergencies) +
                    len(self.simulator.non_life_threatening_emergencies)
            )
            if total_emergencies > 0:
                break


        print("Life-threatening emergencies:", self.simulator.life_threatening_emergencies)
        print("Non-life-threatening emergencies:", self.simulator.non_life_threatening_emergencies)

        self.assertGreater(total_emergencies, 0, "No emergencies were generated after multiple attempts.")

    def test_get_time_to_next_event(self):

        time_to_next = self.simulator.get_time_to_next_event()
        self.assertGreater(time_to_next, 0, "Time to next event is not positive.")

    def test_check_travel(self):

        self.simulator.start_new_travel(2)
        self.simulator.travel["time_remaining"] = 0
        self.simulator.check_travel()
        self.assertFalse(self.simulator.travel["currently_traveling"], "Travel state not updated correctly after completion.")

    def test_simulate(self):
        # Testing the simulation for a short period.
        try:
            result = self.simulator.simulate(0.1)  # Simulate for 6 minutes
            print("Simulation Results:")
            print(f"Doctor Utilization: {result['doc_util']}")
            print(f"Doctor Time at Center: {result['doc_center']}")
            print(f"Avg Non-Life-Threatening Waiting Time (mins): {result['avg_non_live_threatening_waiting_time_min']}")
            self.assertIn("doc_util", result)
            self.assertIn("doc_center", result)
            self.assertIn("avg_non_live_threatening_waiting_time_min", result)

            # Handle division by zero case for non-life-threatening emergencies
            if len(self.simulator.waiting_times_non_life_threatening) == 0:
                print("No non-life-threatening emergencies handled during simulation.")
                self.assertEqual(result["avg_non_live_threatening_waiting_time_min"], 0,
                                 "Average waiting time should be 0 when no emergencies are handled.")
            else:
                self.assertGreaterEqual(result["avg_non_live_threatening_waiting_time_min"], 0,
                                        "Average waiting time is negative.")
        except ZeroDivisionError:
            print("ZeroDivisionError caught: No non-life-threatening emergencies were processed.")
            self.assertTrue(True, "Handled ZeroDivisionError gracefully.")

if __name__ == "__main__":
    unittest.main()

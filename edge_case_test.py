import unittest
from main import EmergencySimulator, Emergency

class EdgeCaseTests(unittest.TestCase):
    def setUp(self):
        """Set up a new EmergencySimulator instance for edge case tests."""
        self.simulator = EmergencySimulator(seed=123)

    def test_no_emergencies(self):

        result = self.simulator.simulate(1)


        print("Edge Case Test Results (No Emergencies):")
        print(f"Doctor Utilization: {result['doc_util']}")
        print(f"Doctor Time at Center: {result['doc_center']}")
        print(f"Avg Non-Life-Threatening Waiting Time (mins): {result['avg_non_live_threatening_watiing_time_min']}")


        self.assertEqual(result["doc_util"], 0, "Doctor should not be utilized with no emergencies.")
        self.assertEqual(result["doc_center"], 1, "Doctor should spend all time at the center with no emergencies.")
        self.assertEqual(result["avg_non_live_threatening_watiing_time_min"], 0,
                         "Average waiting time should be 0 with no emergencies.")

    def test_one_emergency(self):

        emergency = Emergency(district=3, start_time=0, prio=1)
        self.simulator.life_threatening_emergencies.append(emergency)


        result = self.simulator.simulate(1)


        print("Edge Case Test Results (One Emergency):")
        print(f"Doctor Utilization: {result['doc_util']}")
        print(f"Doctor Time at Center: {result['doc_center']}")
        print(f"Avg Non-Life-Threatening Waiting Time (mins): {result['avg_non_live_threatening_watiing_time_min']}")


        self.assertEqual(len(self.simulator.life_threatening_emergencies), 0,
                         "Single life-threatening emergency was not processed.")
        self.assertGreater(result["doc_util"], 0, "Doctor utilization should be greater than 0.")
        self.assertGreater(result["doc_center"], 0, "Doctor should spend some time at the center after processing.")

    def test_all_emergencies_in_one_district(self):

        for _ in range(5):
            self.simulator.life_threatening_emergencies.append(
                Emergency(district=3, start_time=0, prio=1)
            )


        result = self.simulator.simulate(2)


        print("Edge Case Test Results (All Emergencies in One District):")
        print(f"Doctor Utilization: {result['doc_util']}")
        print(f"Remaining Life-Threatening Emergencies: {len(self.simulator.life_threatening_emergencies)}")
        print(f"Remaining Non-Life-Threatening Emergencies: {len(self.simulator.non_life_threatening_emergencies)}")


        self.assertEqual(len(self.simulator.life_threatening_emergencies), 0,
                         "Not all life-threatening emergencies in the same district were processed.")
        self.assertGreater(result["doc_util"], 0.5, "Doctor utilization should be high for emergencies in one district.")

    def test_emergency_with_invalid_district(self):

        # Add an emergency in an invalid district (e.g., -1 or 20)
        invalid_emergency = Emergency(district=-1, start_time=0, prio=1)
        self.simulator.life_threatening_emergencies.append(invalid_emergency)


        with self.assertRaises(IndexError, msg="Simulator should raise an error for invalid district values."):
            self.simulator.simulate(1)

    def test_zero_duration_simulation(self):

        result = self.simulator.simulate(0)


        print("Edge Case Test Results (Zero Duration):")
        print(f"Doctor Utilization: {result['doc_util']}")
        print(f"Doctor Time at Center: {result['doc_center']}")
        print(f"Avg Non-Life-Threatening Waiting Time (mins): {result['avg_non_live_threatening_watiing_time_min']}")


        self.assertEqual(result["doc_util"], 0, "Doctor utilization should be 0 for zero simulation duration.")
        self.assertEqual(result["doc_center"], 0, "Doctor time at center should be 0 for zero simulation duration.")

if __name__ == "__main__":
    unittest.main()

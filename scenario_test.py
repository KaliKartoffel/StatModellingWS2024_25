import unittest
from main import EmergencySimulator, Emergency

class ScenarioBasedTest(unittest.TestCase):
    def setUp(self):

        self.simulator = EmergencySimulator(seed=123)

    def test_life_threatening_emergency(self):

        emergency = Emergency(district=3, start_time=0, prio=1)
        self.simulator.life_threatening_emergencies.append(emergency)

        result = self.simulator.simulate(0.1)


        print("Scenario: Life-Threatening Emergency")
        print(f"Life-Threatening Emergencies Remaining: {len(self.simulator.life_threatening_emergencies)}")
        print(f"Doctor Utilization: {result['doc_util']}")
        print(f"Doctor Time at Center: {result['doc_center']}")
        print(f"Avg Non-Life-Threatening Waiting Time (mins): {result['avg_non_live_threatening_watiing_time_min']}")

        # Assert that the life-threatening emergency was processed
        self.assertEqual(len(self.simulator.life_threatening_emergencies), 0,
                         "Life-threatening emergency was not processed.")

    def test_mixed_emergency_scenario(self):
        """Simulate a scenario with both life-threatening and non-life-threatening emergencies."""
        # Add one life-threatening and one non-life-threatening emergency
        life_threatening = Emergency(district=2, start_time=0, prio=1)
        non_life_threatening = Emergency(district=5, start_time=0, prio=0)
        self.simulator.life_threatening_emergencies.append(life_threatening)
        self.simulator.non_life_threatening_emergencies.append(non_life_threatening)


        result = self.simulator.simulate(0.2)


        print("Scenario: Mixed Emergency Scenario")
        print(f"Life-Threatening Emergencies Remaining: {len(self.simulator.life_threatening_emergencies)}")
        print(f"Non-Life-Threatening Emergencies Remaining: {len(self.simulator.non_life_threatening_emergencies)}")
        print(f"Doctor Utilization: {result['doc_util']}")
        print(f"Doctor Time at Center: {result['doc_center']}")
        print(f"Avg Non-Life-Threatening Waiting Time (mins): {result['avg_non_live_threatening_watiing_time_min']}")

        # Assert life-threatening emergency was handled first
        self.assertEqual(len(self.simulator.life_threatening_emergencies), 0,
                         "Life-threatening emergency was not processed.")
        self.assertLessEqual(len(self.simulator.non_life_threatening_emergencies), 1,
                             "Non-life-threatening emergency was not prioritized correctly.")

if __name__ == "__main__":
    unittest.main()

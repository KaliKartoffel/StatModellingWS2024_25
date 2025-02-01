import numpy as np
import random
import pandas as pd


class EmergencySimulator:
    def __init__(
        self,
        simulation_duration_seconds=24 * 3600,
        time_step_seconds=1,
        call_interval_seconds=50 * 60,
        life_threatening_prob=0.25,
        num_hqs=1,
        strategy="fifo"  # fifo, closest, random
    ):
        self.time_step_seconds = time_step_seconds
        self.simulation_duration_seconds = simulation_duration_seconds
        self.call_interval_seconds = call_interval_seconds
        self.life_threatening_prob = life_threatening_prob
        self.num_hqs = num_hqs
        self.strategy = strategy

        self.district_population = [
            10000, 35000, 25000, 25000, 15000,
            20000, 45000, 40000, 15000, 35000,
        ]
        self.travel_time_matrix_minutes = np.array(
            [
                [3, 6, 5, 8, 8, 4, 6, 8, 10, 12],
                [6, 4, 5, 8, 14, 6, 4, 10, 7, 6],
                [5, 5, 3, 6, 10, 8, 8, 12, 12, 7],
                [8, 8, 6, 5, 6, 10, 13, 9, 10, 11],
                [8, 14, 10, 6, 5, 7, 9, 7, 10, 20],
                [4, 6, 8, 10, 7, 3, 5, 5, 9, 17],
                [6, 4, 8, 13, 9, 5, 3, 10, 7, 10],
                [8, 10, 12, 9, 7, 5, 10, 5, 14, 20],
                [10, 7, 12, 10, 10, 9, 7, 14, 7, 14],
                [12, 6, 7, 11, 20, 17, 10, 20, 14, 6],
            ]
        )

        self.time_seconds = 0
        self.queue = []  # List to store pending emergencies
        self.hq_vehicles = [
            {
                "status": "available",
                "location": 0,
                "available_from_seconds": 0,
                "time_at_hq_seconds": 0,
            }
            for _ in range(self.num_hqs)
        ]
        self.data_log = []
        self.life_threatening_cases_count = 0
        self.non_life_threatening_cases_count = 0
        self.total_use_duration_seconds = 0
        self.non_life_threatening_wait_times = []

    def generate_emergency(self):
        district = random.choices(range(10), weights=self.district_population)[0]
        life_threatening = random.random() < self.life_threatening_prob
        treatment_time_minutes = (
            random.randint(30, 90) if life_threatening else random.randint(10, 20)
        )
        
        if life_threatening:
            self.life_threatening_cases_count += 1
        else:
            self.non_life_threatening_cases_count += 1

        return {
            "district": district,
            "life_threatening": life_threatening,
            "treatment_time_minutes": treatment_time_minutes,
            "request_time_seconds": self.time_seconds,
        }

    def select_case(self, vehicle):
        life_threatening_cases = [c for c in self.queue if c["life_threatening"]]
        non_life_threatening_cases = [c for c in self.queue if not c["life_threatening"]]
        
        if self.strategy == "fifo":
            category = life_threatening_cases or non_life_threatening_cases
            category.sort(key=lambda x: x["request_time_seconds"])
            return category.pop(0) if category else None

        elif self.strategy == "closest":
            category = life_threatening_cases or non_life_threatening_cases
            if category:
                category.sort(
                    key=lambda x: self.travel_time_matrix_minutes[vehicle["location"]][x["district"]]
                )
                return category.pop(0)
            return None

        elif self.strategy == "random":
            category = life_threatening_cases or non_life_threatening_cases
            return category.pop(random.randint(0, len(category) - 1)) if category else None

        return None

    def run(self):
        while self.time_seconds < self.simulation_duration_seconds:
            if random.expovariate(1 / self.call_interval_seconds) < self.time_step_seconds:
                self.queue.append(self.generate_emergency())

            for vehicle in self.hq_vehicles:
                if vehicle["status"] == "available" and vehicle["available_from_seconds"] <= self.time_seconds and self.queue:
                    current_case = self.select_case(vehicle)
                    if current_case:
                        self.queue.remove(current_case)

                        if not current_case["life_threatening"]:
                            self.non_life_threatening_wait_times.append(
                                self.time_seconds - current_case["request_time_seconds"]
                            )

                        travel_time_seconds = random.uniform(
                            0.5 * self.travel_time_matrix_minutes[vehicle["location"]][current_case["district"]] * 60,
                            1.5 * self.travel_time_matrix_minutes[vehicle["location"]][current_case["district"]] * 60,
                        )
                        treatment_time_seconds = current_case["treatment_time_minutes"] * 60

                        vehicle["status"] = "busy"
                        vehicle["location"] = current_case["district"]
                        vehicle["available_from_seconds"] = self.time_seconds + travel_time_seconds + treatment_time_seconds
                        self.total_use_duration_seconds += travel_time_seconds + treatment_time_seconds
            
            for vehicle in self.hq_vehicles:
                if vehicle["status"] == "busy" and vehicle["available_from_seconds"] <= self.time_seconds:
                    vehicle["status"] = "available"

                if vehicle["status"] == "available":
                    vehicle["time_at_hq_seconds"] += self.time_step_seconds
            
            self.data_log.append({
                "time_seconds": self.time_seconds,
                "queue_length": len(self.queue),
                "active_vehicles": sum(1 for v in self.hq_vehicles if v["status"] != "available"),
                "avg_time_at_hq": np.mean([v["time_at_hq_seconds"] for v in self.hq_vehicles]),
            })
            
            self.time_seconds += self.time_step_seconds


    def output_statistics(self):
        """Output final simulation statistics."""

        print(f"--- {self.num_hqs} HQs, {self.strategy} strategy")

        total_hq_time = sum(
            vehicle["time_at_hq_seconds"] for vehicle in self.hq_vehicles
        )
        percentage_at_hq = (
            total_hq_time / (self.simulation_duration_seconds * self.num_hqs)
        ) * 100

        if self.non_life_threatening_wait_times:
            avg_wait = np.mean(self.non_life_threatening_wait_times)
            print(
                f"Expected waiting time for non-life-threatening cases: {avg_wait / 60:.2f} minutes"
            )
        else:
            print("No non-life-threatening cases recorded.")

        print(f"Total life-threatening cases: {self.life_threatening_cases_count}")
        print(
            f"Total non-life-threatening cases: {self.non_life_threatening_cases_count}"
        )
        print(
            f"Total vehicle use duration (hours): {self.total_use_duration_seconds / 3600:.2f}"
        )
        print(f"Total time spent at HQ (hours): {total_hq_time / 3600:.2f}")
        print(f"Percentage of time spent at HQ: {percentage_at_hq:.2f}%")


if __name__ == "__main__":
    for strategy in ["fifo","closest","random"]:
        simulator = EmergencySimulator(num_hqs=1, strategy=strategy)
        simulator.run()
        simulator.output_statistics()


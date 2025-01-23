import random

from main import EmergencySimulator, Emergency
from collections import deque

class ExtendedEmergencySimulator(EmergencySimulator):
    def __init__(self, num_hqs=1, num_vehicles=1, strategy="fifo", seed=123):
        super().__init__(seed=seed)  # Call parent class initializer
        self.num_hqs = num_hqs
        self.num_vehicles = num_vehicles
        self.strategy = strategy
        self.hqs = list(range(num_hqs))  # District indices for HQs

        # Initialize emergency queues for each vehicle
        self.emergency_queues = [deque() for _ in range(self.num_vehicles)]

        # Initialize doctor/vehicle statuses
        self.doctor_status = [{"current_location": self.hqs[i % len(self.hqs)], "busy": False, "time_remaining": 0}
                              for i in range(self.num_vehicles)]

        # Variables for travel time statistics
        self.travel_time_sum = 0
        self.travel_count = 0

    def generate_emergency(self):
        """Generate a new emergency and add it to a queue."""
        if self.time_to_next_emergency <= 0:
            self.time_to_next_emergency = self.get_time_to_next_event()
            district = random.choices(range(10), weights=self.populations)[0]
            prio = random.choices([0, 1], weights=[3, 1])[0]  # 0 = non-life-threatening, 1 = life-threatening
            emergency = Emergency(district=district, start_time=self.total_time_passed, prio=prio)

            # Assign emergency to the first queue (for simplicity)
            self.emergency_queues[0].append(emergency)
            print(f"New emergency added: {emergency.district}, Priority: {emergency.prio}")

    def assign_doctor(self, doctor_idx):
        """Assigns the doctor to an emergency."""
        queue = self.emergency_queues[doctor_idx]
        if not queue:  # No emergencies in the queue
            return

        # Select emergency based on strategy
        if self.strategy == "fifo":
            emergency = queue.popleft()
        elif self.strategy == "nearest":
            emergency = min(queue,
                            key=lambda em: self.get_travel_time(self.doctor_status[doctor_idx]["current_location"],
                                                                em.district))
            queue.remove(emergency)

        elif self.strategy == "high_priority_first":
            # Select high-priority emergencies first
            emergency = max(queue, key=lambda em: em.prio)
            queue.remove(emergency)


        # Update doctor's status
        doctor = self.doctor_status[doctor_idx]
        travel_time = self.get_travel_time(doctor["current_location"], emergency.district)
        care_time = self.get_em_care_time(emergency)  # Correct method call

        doctor["busy"] = True
        doctor["time_remaining"] = travel_time + care_time
        self.travel_time_sum += travel_time
        self.travel_count += 1
        doctor["current_location"] = emergency.district
        print(f"Doctor {doctor_idx} assigned to emergency at district {emergency.district}")

    def update_doctors(self, time_step):
        """Update the status of all doctors and manage their tasks."""
        for i, doctor in enumerate(self.doctor_status):
            if doctor["busy"]:
                doctor["time_remaining"] -= time_step
                if doctor["time_remaining"] <= 0:
                    doctor["busy"] = False
                    print(f"Doctor {i} has finished their task and is now idle.")

    def simulate(self, total_time_hours=10):
        max_time = total_time_hours * 3600  # Convert hours to seconds
        while self.total_time_passed < max_time:
            if self.time_to_next_emergency <= 0:
                self.generate_emergency()

            # Update doctors
            self.update_doctors(1)

            # Assign doctors to emergencies
            for i, doctor in enumerate(self.doctor_status):
                if not doctor["busy"]:
                    self.assign_doctor(i)

            # Advance time
            self.time_to_next_emergency -= 1
            self.total_time_passed += 1

            # Debugging: Print queue and doctor statuses
            if self.total_time_passed % 3600 == 0:  # Every simulated hour
                print(f"Time: {self.total_time_passed} seconds")
                print(f"Queues: {[len(queue) for queue in self.emergency_queues]}")
                print(f"Doctors: {self.doctor_status}")

        # Calculate average travel time
        avg_travel_time = self.travel_time_sum / self.travel_count if self.travel_count > 0 else 0
        return {
            "avg_travel_time": avg_travel_time / 60,  # Convert to minutes
            "emergency_queues": [len(queue) for queue in self.emergency_queues],
        }


if __name__ == "__main__":
    # Number of headquarters
    hq_configs = [1, 2, 3, 5]  
    # Number of doctors/vehicles
    num_vehicles = 2  
    strategies = ["fifo", "nearest", "high_priority_first"]  
    simulation_hours = 10

    for num_hqs in hq_configs:
        print(f"Testing with {num_hqs} headquarters...")
        results_per_hq = []
        for strategy in strategies:
            print(f"Running simulation with strategy: {strategy}")
            sim = ExtendedEmergencySimulator(num_hqs=num_hqs, num_vehicles=num_vehicles, strategy=strategy, seed=42)
            # Simulate for 10 hours
            results = sim.simulate(simulation_hours)  
            results_per_hq.append({
                "strategy": strategy,
                "avg_travel_time": results["avg_travel_time"],
                "remaining_queues": results["emergency_queues"]
            })
            print(f"Strategy: {strategy}")
            print(f"Average Travel Time (minutes): {results['avg_travel_time']:.2f}")
            print(f"Remaining Emergencies in Queues: {results['emergency_queues']}")
            print("-" * 50)

        # Compare results across strategies for the current HQ configuration
        print(f"Results for {num_hqs} headquarters:")
        for result in results_per_hq:
            print(f"Strategy: {result['strategy']}, Avg Travel Time: {result['avg_travel_time']:.2f} minutes, "
                  f"Remaining Queues: {result['remaining_queues']}")
        print("=" * 50)


import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import pandas as pd
import numpy as np
import random
from matplotlib.animation import FuncAnimation
import time

from main import EmergencySimulator  # Importing the classes from main.py
from task4_and_5 import ExtendedEmergencySimulator


def visualize_time_series(
        doc_util_results,
        doc_center_results,
        waiting_results,
        ):
    """
    Visualize doctor utilization, time at center, and waiting times.
    """

    print(doc_center_results)
    print(doc_util_results)
    print(waiting_results)

    plt.figure(figsize=(12, 6))
    plt.plot(doc_util_results,
             label="Doctor Utilization")
    plt.plot(doc_center_results,
             label="Doctor at Center")
    plt.legend()
    plt.title(
        "Doctor Utilization vs Center Time Across Runs"
        )
    plt.xlabel("Simulation Run")
    plt.ylabel("Ratio")
    plt.show()

    sns.histplot(waiting_results, kde=True)
    plt.title(
        "Distribution of Average Waiting Times (Non-Life-Threatening Emergencies)"
        )
    plt.xlabel("Waiting Time (Minutes)")
    plt.ylabel("Frequency")
    plt.show()

    # ########################################################
    # ########################################################
    #
    # WHAT ABOUT WAITING TIMES FOR LIFE THREATENING EMERGENCIES
    #
    # ########################################################
    # ########################################################


def visualize_emergency_counts(visualization_data):
    """
    Plots the number of life-threatening and non-life-threatening emergencies with respect to time
    """
    times = [data["total_time_passed"] for data in visualization_data]

    non_life_emergency_data = [data["non_life_threatening_emergencies"] for data in visualization_data]
    life_emergency_data = [data["life_threatening_emergencies"] for data in visualization_data]

    non_life_emergencies = [len(entry) for entry in non_life_emergency_data]
    life_emergencies = [len(entry) for entry in life_emergency_data]

    # filter out empty points
    """ empty_points = []
    for i in range(len(times)-1):
        if non_life_emergencies[i] == 0 and life_emergencies[i] == 0:
            empty_points.append(i)

    for i in empty_points[::-1]:
        times.pop(i)
        non_life_emergencies.pop(i)
        life_emergencies.pop(i) """

    print([[times[i], life_emergencies[i], non_life_emergencies[i]] for i in range(10)])

    plt.figure(figsize=(12, 6))

    plt.scatter(times, life_emergencies, label="Life-Threatening Emergencies", color="red")
    plt.scatter(times, non_life_emergencies, label="Non-Life-Threatening Emergencies", color="blue")
    plt.xlabel("Time")
    plt.ylabel("Number of Emergencies")
    plt.title("Number of Emergencies Over Time")
    plt.legend()
    plt.show()


def dynamic_time_series(visualization_data):
    """
    Dynamic visualization of emergency counts over time.
    """

    # Extract data for visualization
    times = [
        data["total_time_passed"]
        for data in visualization_data
        ]
    life_emergencies = [
        len(data["life_threatening_emergencies"])
        for data in visualization_data
        ]
    non_life_emergencies = [
        len(data["non_life_threatening_emergencies"])
        for data in visualization_data
        ]

    # Create the figure and axes, arranging them horizontally
    fig, ax = plt.subplots(1, 2, figsize=(18, 6), sharex=False)

    # Plot 1: Life-Threatening Emergency counts over time
    ax[0].set_title("Emergency Counts Over Time")
    ax[0].set_ylabel("Number of Emergencies")
    ax[0].set_xlim(0, max(times))
    ax[0].set_ylim(0, max(max(life_emergencies),
                          max(non_life_emergencies)
                          ) + 1)
    line_life, = ax[0].plot([],
                            [],
                            label="Life-Threatening Emergencies",
                            color="red",
                            lw=1,
                            )
    ax[0].legend()

    # Plot 2: Non-Life-Threatening Emergency counts over time
    ax[1].set_title("Emergency Counts Over Time")
    ax[1].set_ylabel("Number of Emergencies")
    ax[1].set_xlim(0, max(times))
    ax[1].set_ylim(0, max(max(life_emergencies),
                          max(non_life_emergencies)
                          ) + 1)
    line_non_life, = ax[1].plot([],
                                [],
                                label="Non-Life-Threatening Emergencies",
                                color="blue",
                                lw=1,
                                )
    ax[1].legend()

    def init():
        """Initialize the lines and scatter."""
        line_life.set_data([],
                           [],
                           )
        line_non_life.set_data([],
                               [],
                               )
        return line_life, line_non_life

    def update(frame):
        """Update the lines and scatter with new data."""
        if frame >= len(visualization_data):
            print("Error: Frame index out of range")
            return  # Prevent index errors

        # Update emergency counts
        line_life.set_data(times[:frame],
                           life_emergencies[:frame],
                           )
        line_non_life.set_data(times[:frame],
                               non_life_emergencies[:frame],
                               )

        return line_life, line_non_life

    anim = FuncAnimation(fig,
                         update,
                         frames=len(visualization_data),
                         init_func=init, blit=False,
                         interval=50,
                         )

    plt.tight_layout()
    plt.show()


def dynamic_visualization(visualization_data):
    # Populations and average travel times between districts
    populations = [10000, 35000, 25000, 25000, 15000,
                   20000, 45000, 40000, 15000, 35000]
    avg_travel_times = [
        [3, 6, 5, 8, 8, 4, 6, 8, 10, 12],
        [6, 4, 5, 8, 14, 6, 4, 10, 7, 6],
        [5, 5, 3, 6, 10, 8, 8, 12, 12, 7],
        [8, 8, 6, 5, 6, 10, 13, 9, 10, 11],
        [8, 14, 10, 6, 5, 7, 9, 7, 10, 20],
        [4, 6, 8, 10, 7, 3, 5, 5, 9, 17],
        [6, 4, 8, 13, 9, 5, 3, 10, 7, 10],
        [8, 10, 12, 9, 7, 5, 10, 5, 14, 20],
        [10, 7, 12, 10, 10, 9, 7, 14, 7, 14],
        [12, 6, 7, 11, 20, 17, 10, 20, 14, 6]
    ]

    # Extract data for visualization
    times = [data["total_time_passed"] for data in visualization_data]
    current_districts = [data["current_dist"] for data in visualization_data]

    # Create circular graph layout
    num_districts = len(populations)
    angles = np.linspace(0, 2 * np.pi, num_districts, endpoint=False)
    node_positions = {i: (np.cos(angle), np.sin(angle)) for i, angle in enumerate(angles)}

    # Normalize population and travel duration for visualization
    max_pop = max(populations)
    max_travel = max(max(row) for row in avg_travel_times)
    node_sizes = [300 + 1000 * (pop / max_pop) for pop in populations]  # Scaled sizes
    edge_widths = np.array(avg_travel_times) / max_travel * 3  # Scaled widths for edges

    # Create the figure and axes, arranging them horizontally
    fig, ax = plt.subplots(1, 1, figsize=(8, 8), sharex=False)

    # Circular graph of districts
    ax.set_title("Districts and Doctor's Movement")
    ax.axis("off")  # Turn off axis

    # Add nodes and edges
    for i in range(num_districts):
        for j in range(num_districts):
            if i != j:  # Avoid self-loops
                ax.plot(
                    [node_positions[i][0], node_positions[j][0]],
                    [node_positions[i][1], node_positions[j][1]],
                    color="gray",
                    lw=edge_widths[i][j],
                )
    node_scatter = ax.scatter(
        [pos[0] for pos in node_positions.values()],
        [pos[1] for pos in node_positions.values()],
        s=node_sizes,
        c="lightblue",
        edgecolor="black",
        label="Districts",
        zorder=2  # Ensure nodes are on top of edges but below doctor
    )

    # Add district labels (1-10)
    for i, (x, y) in node_positions.items():
        ax.text(x * 1.1,
                y * 1.1,
                str(i + 1),
                color="black",
                ha="center",
                va="center",
                fontsize=12)

    doctor_marker, = ax.plot([], [], "ro", label="Doctor", markersize=10)
    ax.legend()

    # Initialize the figure and plot elements
    frame_number_text = ax.text(
        0.05, 0.95, "", transform=ax.transAxes, fontsize=12, color="black", ha="left", va="top"
    )
    t0 = round(time.time() * 1000)

    def init():
        """Initialize the lines and scatter."""
        doctor_marker.set_data([], [])
        frame_number_text.set_text("")  # Clear text on initialization
        return doctor_marker, frame_number_text

    def update(frame):
        """Update the lines and scatter with new data."""
        current_time = round(time.time() * 1000) - t0

        # Find the two districts to interpolate between
        for i in range(len(times) - 1):
            if times[i] <= current_time <= times[i + 1]:
                # Calculate interpolation factor
                alpha = (current_time - times[i]) / (times[i + 1] - times[i])

                # Interpolate position
                prev_pos = node_positions[current_districts[i]]
                next_pos = node_positions[current_districts[i + 1]]
                doctor_pos = (
                    prev_pos[0] + alpha * (next_pos[0] - prev_pos[0]),
                    prev_pos[1] + alpha * (next_pos[1] - prev_pos[1])
                )
                doctor_marker.set_data([doctor_pos[0]], [doctor_pos[1]])

                # Update frame number text
                frame_number_text.set_text(f"Time: {current_time}")
                return doctor_marker, frame_number_text

        # If no match, keep the doctor stationary
        doctor_marker.set_data([], [])
        frame_number_text.set_text(f"Time: {current_time}")
        return doctor_marker, frame_number_text

    # Create the FuncAnimation
    anim = FuncAnimation(
        fig, update, frames=len(visualization_data), init_func=init, blit=False, interval=1
    )

    # Display the plot
    plt.tight_layout()
    plt.show()


def advanced_simulation_results(strategies, hq_configs, num_simulations, results):
    """
    Creates scatter plots for simulation results, with the number of HQs on the x-axis and
    multiple data series corresponding to strategies.

    :param strategies: List of strategies used in the simulation.
    :param hq_configs: List of HQ configurations used in the simulation.
    :param num_simulations: Number of simulations to average per configuration.
    :param results: Dictionary with the structure:
                    {
                        hq_config_1: {
                            strategy_1: [{"avg_travel_time": ..., "remaining_queues": [...]}, ...],
                            strategy_2: [...],
                        },
                        hq_config_2: {...},
                        ...
                    }
    """
    # Prepare data for plotting
    plot_data = []
    for hq in hq_configs:
        for strategy in strategies:
            # Average across multiple simulations
            avg_travel_time = sum(run["avg_travel_time"] for run in results[hq][strategy]) / num_simulations
            avg_remaining_queues = sum(sum(run["remaining_queues"]) for run in results[hq][strategy]) / num_simulations

            plot_data.append({
                "HQs": hq,
                "Strategy": strategy,
                "Average Travel Time (minutes)": avg_travel_time,
                "Average Remaining Emergencies": avg_remaining_queues,
            })

    # Convert to DataFrame for Seaborn
    df = pd.DataFrame(plot_data)

    # Scatter plot for Average Travel Time
    plt.figure(figsize=(12, 6))
    sns.scatterplot(data=df, x="HQs", y="Average Travel Time (minutes)", hue="Strategy", s=100)
    plt.title("Average Travel Time vs Number of HQs")
    plt.xlabel("Number of Headquarters")
    plt.ylabel("Average Travel Time (minutes)")
    plt.xticks(ticks=hq_configs)  # Set x-axis to show only integers
    plt.grid(True)
    plt.legend(title="Strategy")
    plt.show()

    # Scatter plot for Average Remaining Emergencies
    plt.figure(figsize=(12, 6))
    sns.scatterplot(data=df, x="HQs", y="Average Remaining Emergencies", hue="Strategy", s=100)
    plt.title("Average Remaining Emergencies vs Number of HQs")
    plt.xlabel("Number of Headquarters")
    plt.ylabel("Average Remaining Emergencies")
    plt.xticks(ticks=hq_configs)  # Set x-axis to show only integers
    plt.grid(True)
    plt.legend(title="Strategy")
    plt.show()




if __name__ == "__main__":
    # Run simulations to collect data
    doc_util_results = []
    doc_center_results = []
    waiting_results = []

    for i in range(0):
        es = EmergencySimulator(seed=i)
        result = es.simulate(1000)
        doc_util_results.append(result["doc_util"])
        doc_center_results.append(result["doc_center"])
        waiting_results.append(result["avg_non_live_threatening_waiting_time_min"])
    
    print(len(waiting_results))
    # print([result["visualization_data"][i]["total_time_passed"] for i in range(10)])

    while False:

        selected_visualisation = int(input("Select visualisation (1: Time Series, 2: Dynamic, 3: Emergencies, 4: Playback): "))

        if selected_visualisation == 1:
            visualize_time_series(doc_util_results, doc_center_results, waiting_results)
        elif selected_visualisation == 2:
            dynamic_time_series(result["visualization_data"])
        elif selected_visualisation == 3:
            visualize_emergency_counts(result["visualization_data"])
        elif selected_visualisation == 4:
            simulator = EmergencySimulator(seed=123)
            result = simulator.simulate(100)
            dynamic_visualization(result["visualization_data"])
            break
        elif selected_visualisation == 0:
            break

        else:
            print(len([ entry["total_time_passed"] for entry in result["visualization_data"] ]))
            print(len([ entry["non_life_threatening_emergencies"] for entry in result["visualization_data"] ]))
            print([result["visualization_data"][i]["life_threatening_emergencies"] for i in range(10)])
            print([result["visualization_data"][i]["non_life_threatening_emergencies"] for i in range(10)])


    # Advanced simulation results
    hq_configs = range(1, 10)  # Integer range of HQs
    num_vehicles = 2
    strategies = ["fifo", "nearest", "high_priority_first"]
    simulation_hours = 10
    num_simulations = 1  # Number of simulations per configuration

    results = {}
    for num_hqs in hq_configs:
        results[num_hqs] = {}
        for strategy in strategies:
            results[num_hqs][strategy] = []
            for _ in range(num_simulations):
                sim = ExtendedEmergencySimulator(num_hqs=num_hqs, num_vehicles=num_vehicles, strategy=strategy, seed=42)
                simulation_result = sim.simulate(simulation_hours)
                results[num_hqs][strategy].append({
                    "avg_travel_time": simulation_result["avg_travel_time"],
                    "remaining_queues": simulation_result["emergency_queues"]
                })

    # Generate scatter plots
    #advanced_simulation_results(strategies, hq_configs, num_simulations, results)


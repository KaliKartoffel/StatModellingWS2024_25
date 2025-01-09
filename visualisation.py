import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import pandas as pd
import numpy as np
from matplotlib.animation import FuncAnimation
from main import EmergencySimulator  # Importing the classes from main.py


def visualize_time_series(doc_util_results, doc_center_results, waiting_results):
    """Visualize doctor utilization, time at center, and waiting times."""
    plt.figure(figsize=(12, 6))
    plt.plot(doc_util_results, label="Doctor Utilization")
    plt.plot(doc_center_results, label="Doctor at Center")
    plt.legend()
    plt.title("Doctor Utilization vs Center Time Across Runs")
    plt.xlabel("Simulation Run")
    plt.ylabel("Ratio")
    plt.show()

    sns.histplot(waiting_results, kde=True)
    plt.title("Distribution of Average Waiting Times (Non-Life-Threatening Emergencies)")
    plt.xlabel("Waiting Time (Minutes)")
    plt.ylabel("Frequency")
    plt.show()

def dynamic_time_series(visualization_data):
    # Extract data for visualization
    times = [data["total_time_passed"] for data in visualization_data]
    life_emergencies = [data["life_threatening_emergencies"] for data in visualization_data]
    non_life_emergencies = [data["non_life_threatening_emergencies"] for data in visualization_data]

    # Create the figure and axes, arranging them horizontally
    fig, ax = plt.subplots(1, 2, figsize=(18, 6), sharex=False)

    # Plot 1: Life-Threatening Emergency counts over time
    ax[0].set_title("Emergency Counts Over Time")
    ax[0].set_ylabel("Number of Emergencies")
    ax[0].set_xlim(0, max(times))
    ax[0].set_ylim(0, max(max(life_emergencies), max(non_life_emergencies)) + 1)
    line_life, = ax[0].plot([], [], label="Life-Threatening Emergencies", color="red", lw=1)
    ax[0].legend()

    # Plot 2: Non-Life-Threatening Emergency counts over time
    ax[1].set_title("Emergency Counts Over Time")
    ax[1].set_ylabel("Number of Emergencies")
    ax[1].set_xlim(0, max(times))
    ax[1].set_ylim(0, max(max(life_emergencies), max(non_life_emergencies)) + 1)
    line_non_life, = ax[1].plot([], [], label="Non-Life-Threatening Emergencies", color="blue", lw=1)
    ax[1].legend()

    def init():
        """Initialize the lines and scatter."""
        line_life.set_data([], [])
        line_non_life.set_data([], [])
        return line_life, line_non_life

    def update(frame):
        """Update the lines and scatter with new data."""
        if frame >= len(visualization_data):
            print("Error: Frame index out of range")
            return  # Prevent index errors

        # Update emergency counts
        line_life.set_data(times[:frame], life_emergencies[:frame])
        line_non_life.set_data(times[:frame], non_life_emergencies[:frame])

        return line_life, line_non_life

    anim = FuncAnimation(fig, update, frames=len(visualization_data), init_func=init, blit=False, interval=500)

    plt.tight_layout()
    plt.show()



def dynamic_visualization(visualization_data):
    # Populations and average travel times between districts
    populations = [10000, 35000, 25000, 25000, 15000, 20000, 45000, 40000, 15000, 35000]
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
    traveling_status = [data["currently_traveling"] for data in visualization_data]

    # Create circular graph layout
    num_districts = len(populations)
    angles = np.linspace(0, 2 * np.pi, num_districts, endpoint=False)
    node_positions = {i: (np.cos(angle), np.sin(angle)) for i, angle in enumerate(angles)}

    # Normalize population and travel duration for visualization
    max_pop = max(populations)
    max_travel = max(max(row) for row in avg_travel_times)
    node_sizes = [300 + 500 * (pop / max_pop) for pop in populations]  # Scaled sizes
    edge_widths = np.array(avg_travel_times) / max_travel * 3  # Scaled widths for edges

    # Create the figure and axes, arranging them horizontally
    fig, ax = plt.subplots(1, 1, figsize=(18, 6), sharex=False)

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
                    lw=edge_widths[i][j]
                )
    node_scatter = ax.scatter(
        [pos[0] for pos in node_positions.values()],
        [pos[1] for pos in node_positions.values()],
        s=node_sizes,
        c="lightblue",
        edgecolor="black",
        label="Districts"
    )

    # Add district labels (1-10)
    for i, (x, y) in node_positions.items():
        ax.text(x * 1.1, y * 1.1, str(i + 1), color="black", ha="center", va="center", fontsize=12, fontweight='bold')

    doctor_marker, = ax.plot([], [], "ro", label="Doctor", markersize=10)
    ax.legend()

    def init():
        """Initialize the lines and scatter."""
        doctor_marker.set_data([], [])
        return doctor_marker

    def update(frame):
        """Update the lines and scatter with new data."""
        if frame >= len(visualization_data):
            print("Error: Frame index out of range")
            return  # Prevent index errors

        # Doctor's position
        if frame > 0:
            doctor_pos = node_positions[current_districts[frame - 1]]
        else:
            doctor_pos = (0, 0)  # Start at district 1

        doctor_marker.set_data([doctor_pos[0]], [doctor_pos[1]])  

        return doctor_marker

    anim = FuncAnimation(fig, update, frames=len(visualization_data), init_func=init, blit=False, interval=500)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # Run simulations to collect data
    doc_util_results = []
    doc_center_results = []
    waiting_results = []

    for i in range(1):  # Run fewer simulations for faster testing
        es = EmergencySimulator(seed=i)
        result = es.simulate(1000)
        doc_util_results.append(result["doc_util"])
        doc_center_results.append(result["doc_center"])
        waiting_results.append(result["avg_non_live_threatening_watiing_time_min"])

    # Call visualization functions
    dynamic_visualization(result["visualization_data"])

    # Animate playback
    # simulator = EmergencySimulator(seed=123)
    # visualize_simulation_playback(simulator, total_time_hours=1)

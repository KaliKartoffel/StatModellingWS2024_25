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


def visualize_simulation_playback(simulator, total_time_hours=1):
    """Animate the simulation playback."""
    fig, ax = plt.subplots(figsize=(8, 8))

    # Set up the district graph (nodes represent districts)
    districts = list(range(10))
    pos = nx.spring_layout(nx.complete_graph(districts))  # Layout for visualization

    # Simulate positions for districts
    for i, (x, y) in enumerate(pos.values()):
        pos[i] = (x * 10, y * 10)  # Scale positions for better visualization

    G = nx.complete_graph(districts)
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color="lightblue", node_size=500)
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=10, font_color="black")

    ln, = ax.plot([], [], "ro-", linewidth=2, markersize=8, animated=True)

    # Simulated doctor path over time (replace with actual simulation data if needed)
    path = [simulator.current_dist]

    def init():
        ax.set_xlim(-15, 15)
        ax.set_ylim(-15, 15)
        ln.set_data([], [])
        return ln,

    def update(frame):
        simulator.generate_emergency()
        simulator.check_travel()

        path.append(simulator.current_dist)
        xdata = [pos[node][0] for node in path]
        ydata = [pos[node][1] for node in path]
        ln.set_data(xdata, ydata)

        time_to_pass = simulator.time_to_next_emergency
        simulator.wait_secs(min(time_to_pass, 60))  # Step simulation
        return ln,

    ani = FuncAnimation(fig, update, frames=range(total_time_hours * 60), init_func=init, blit=True)
    plt.title("Doctor Movement Across Districts")
    plt.show()


if __name__ == "__main__":
    # Run simulations to collect data
    doc_util_results = []
    doc_center_results = []
    waiting_results = []

    for i in range(1000):  # Run fewer simulations for faster testing
        es = EmergencySimulator(seed=i)
        result = es.simulate(1000)
        doc_util_results.append(result["doc_util"])
        doc_center_results.append(result["doc_center"])
        waiting_results.append(result["avg_non_live_threatening_watiing_time_min"])

    # Call visualization functions
    visualize_time_series(doc_util_results, doc_center_results, waiting_results)

    # Animate playback
    # simulator = EmergencySimulator(seed=123)
    # visualize_simulation_playback(simulator, total_time_hours=1)

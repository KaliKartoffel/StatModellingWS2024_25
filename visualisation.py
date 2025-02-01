from simulator import EmergencySimulator

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import networkx as nx
import os


def run_simulation(
        n,
        n_hqs,
        strategy,
        output_file,
        ):
    """
    Run n simulations with n_hqs and save results to output_file.
    """

    results = []
    for i in range(n):
        print(f"Running simulation with "
              f"{n_hqs} HQs and "
              f"{strategy} strategy - "
              f"{(i+1)/n*100:.2f}%  ",
              end="\r")
        
        sim = EmergencySimulator(num_hqs=n_hqs, strategy=strategy)
        sim.run()
        avg_queue_length = np.mean([log["queue_length"]
                                    for log in sim.data_log])
        avg_time_at_hq = np.mean([log["avg_time_at_hq"]
                                  for log in sim.data_log])
        avg_time_at_hq_percentage = (
            avg_time_at_hq / sim.simulation_duration_seconds * 100
        )
        results.append(
            {
                "Run": i + 1,
                "HQs": n_hqs,
                "Strategy": strategy,
                "Avg Queue Length": avg_queue_length,
                "Avg Time at HQ": avg_time_at_hq,
                "Avg Time at HQ (%)": avg_time_at_hq_percentage,
                "Avg Wait Time": (
                    np.mean(sim.non_life_threatening_wait_times) / 60
                    if sim.non_life_threatening_wait_times
                    else None
                ),
            }
        )

    df = pd.DataFrame(results)
    if os.path.exists(output_file):
        # Append to existing file
        df.to_csv(output_file, mode="a", header=False)
    else:
        # Create new file
        df.to_csv(output_file, mode="w")


def load_simulation_results(file="simulation_results.csv"):
    return pd.read_csv(file) if os.path.exists(file) else None


def visualise_results_scatter(path="simulation_results.csv",
                      variable="Avg Queue Length",
                      log_scale=True,
                      ):
    """

    """

    df = load_simulation_results(path)
    if df is None:
        print("No simulation data found. Run simulations first.")
        return

    plt.figure(figsize=(10, 6))
    for num_hq in df["HQs"].unique():
        subset = df[df["HQs"] == num_hq]
        color = sns.color_palette("tab10")[num_hq - 1]
        sns.regplot(
            data=subset,
            x="Run",
            y=variable,
            scatter=True,
            color=color,
            label=f"{num_hq} HQs",
        )

    plt.legend(title="Strategy")
    plt.title(f"Simulation Results: {variable} by Runs and HQs")
    plt.xlabel("Run")
    # ticks at every run
    plt.xticks([i for i in range(1, len(df["Run"].unique())+1)],
               labels=[])
    plt.ylabel(variable)
    # log scale for y-axis
    if log_scale: plt.yscale("log")
    plt.show()


def visualise_results_avg(path="simulation_results.csv", 
                          variable="Avg Queue Length",
                          log_scale=True,
                          ):
    df = load_simulation_results(path)
    if df is None:
        print("No simulation data found. Run simulations first.")
        return

    plt.figure(figsize=(10, 6))

    strategies = df["Strategy"].unique()
    for i, strategy in enumerate(strategies):
        subset = df[df["Strategy"] == strategy]

        # Compute the mean for each HQ count
        avg_subset = subset.groupby("HQs")[variable].mean().reset_index()

        color = sns.color_palette("tab10")[i - 1]
        sns.lineplot(
            data=avg_subset,
            x="HQs",
            y=variable,
            color=color,
            label=f"{strategy}",
        )

    plt.legend(title="Strategy")
    plt.title(f"Simulation Results: {variable} by Strategy and HQs")
    plt.xlabel("HQs")
    plt.ylabel(variable)
    if log_scale: plt.yscale("log")
    plt.show()


def visualise_travel_graph():

    # Get travel time matrix and district population
    sim = EmergencySimulator()
    travel_time_matrix = sim.travel_time_matrix_minutes
    district_population = sim.district_population

    # Create graph
    G = nx.Graph()
    num_districts = len(district_population)

    # Add nodes
    for i in range(num_districts):
        G.add_node(i+1, population=district_population[i])

    # Add edges
    for i in range(num_districts):
        for j in range(i + 1, num_districts):
            travel_time = travel_time_matrix[i][j]
            if travel_time > 0:
                G.add_edge(u_of_edge=i + 1,
                           v_of_edge=j + 1,
                           weight=travel_time)

    # visualise graph
    pos = nx.spring_layout(G)
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_size=700,
        node_color="lightblue",
        font_size=10,
        font_weight="bold",
    )
    edge_labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.title("District Travel Time Graph")
    plt.show()


if __name__ == "__main__":

    reuse_results = input("Reuse existing simulation results? (y/n): ")

    if reuse_results.lower() == "n":
        # Number of simulation runs
        n_simulation_runs_input = input(
            "Number of simulation runs (default 20): ")
        n_simulation_runs = (
            int(n_simulation_runs_input)
            if n_simulation_runs_input.isdigit() else 20
        )

        # Number of HQs
        hq_numbers_input = input(
            "Number of HQs (comma-separated, default [1,2,3,4,5]): ")
        hq_numbers = (
            [int(x) for x in hq_numbers_input.split(",")]
            if hq_numbers_input else [1,2,3,4,5]
        )

        # Strategies
        strategies = ["fifo","closest","random"]
        strategies_input = input(
            f"Strategies (comma-separated, default {strategies}): ")
        strategies = (
            strategies_input.split(",")
            if strategies_input else strategies
        )

        file = "simulation_results.csv"
        # Remove existing file to write new results
        if os.path.exists(file): 
            os.remove(file)

        # Run simulations
        for n_hq in hq_numbers:
            for strategy in strategies:
                run_simulation(n_simulation_runs, n_hq, strategy, file)

    while True:
        selected_graph = input(
            "Select visualisation ("
            "1: Graph, "
            "2: Scatter Plot, "
            "3: Average Plot) "
        )

    
        if selected_graph == "0" or selected_graph.lower() == "exit":
            break
        elif selected_graph == "1":
            visualise_travel_graph()
        elif selected_graph in ["2", "3"]:
            selected_variable_input = input(
                "Select variable ("
                "1: Avg Queue Length, "
                "2: Avg Time at HQ, "
                "3: Avg Time at HQ (%), "
                "4: Avg Wait Time) "
            )
            selected_variable = "Avg Queue Length"
            y_log = True

            if selected_variable_input == "1":
                selected_variable = "Avg Queue Length"
                y_log = True
            elif selected_variable_input == "2":
                selected_variable = "Avg Time at HQ"
                y_log = False
            elif selected_variable_input == "3":
                selected_variable = "Avg Time at HQ (%)"
                y_log = False
            elif selected_variable_input == "4":
                selected_variable = "Avg Wait Time"
                y_log = True
            else:
                print("Invalid selection. Please try again.")
                continue
            

            if selected_graph == "2":
                visualise_results_scatter(variable=selected_variable,
                                log_scale=y_log)
            elif selected_graph == "3":
                visualise_results_avg(variable=selected_variable,
                                    log_scale=y_log)
        else:
            print("Invalid selection. Please try again.")
            continue

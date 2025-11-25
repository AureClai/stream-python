"""
Example Analysis with Rust Backend
This script loads a scenario, runs it using the high-performance Rust core,
and then performs standard analysis (plots, CSV exports).
"""

# imports
from stream.analysis.export import export_travel_times_on_links, export_flow_speed_on_links
from stream.analysis.analysis import *
from stream.initialization.validate_and_complete_scenario import validate_and_complete_scenario
from stream.initialization.assignment import assignment
from stream.initialization.initialize_simulation import initialize_simulation
import stream_rust
import sys
import os
import json
import time
import numpy as np
import matplotlib.pyplot as plt

# Add project root to path (insert at 0 to prioritize local source over installed package)
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")))

# FIXED IMPORTS ORDER

# Helper for JSON serialization


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)


def run_analysis():
    # 1. Load Inputs
    filename = "example/inputs.npy"
    if len(sys.argv) > 1:
        filename = sys.argv[1]

    print(f"Loading inputs from {filename}...")
    if not os.path.exists(filename):
        alt_filename = os.path.join(os.getcwd(), filename)
        if os.path.exists(alt_filename):
            filename = alt_filename
        else:
            print(f"Error: File {filename} not found.")
            return

    Inputs = np.load(filename, allow_pickle=True).item()

    # 2. Initialize Scenario (Python)
    print("Initializing Scenario...")
    S = validate_and_complete_scenario(Inputs)
    S = assignment(S)
    S = initialize_simulation(S)  # Populates 'Events' structure

    # 3. Prepare Data for Rust
    print("Preparing Rust Simulation...")

    node_id_map = {}
    link_id_map = {}
    inv_link_map = {}

    rust_nodes = []
    sorted_node_ids = sorted(S["Nodes"].keys())
    for i, nid in enumerate(sorted_node_ids):
        node_id_map[nid] = i

    for nid in sorted_node_ids:
        rust_nodes.append(
            {"id": node_id_map[nid], "incoming_links": [], "outgoing_links": []})

    rust_links = []
    sorted_link_ids = sorted(S["Links"].keys())
    for i, lid in enumerate(sorted_link_ids):
        link_id_map[lid] = i
        inv_link_map[i] = lid

    for lid in sorted_link_ids:
        link_data = S["Links"][lid]
        rust_links.append({
            "id": link_id_map[lid],
            "length": float(link_data["Length"]),
            "speed_limit": float(link_data["Speed"]),
            "num_lanes": int(link_data["NumLanes"]),
            "capacity": float(link_data["FD"]["C"]) * int(link_data["NumLanes"]),
            "jam_density": float(link_data["FD"]["kx"]) * int(link_data["NumLanes"]) * 1000.0
        })

    for nid in sorted_node_ids:
        node_data = S["Nodes"][nid]
        in_links = node_data["IncomingLinksID"]
        out_links = node_data["OutgoingLinksID"]
        in_links_list = in_links.tolist() if isinstance(
            in_links, np.ndarray) else list(in_links)
        out_links_list = out_links.tolist() if isinstance(
            out_links, np.ndarray) else list(out_links)

        new_in = [link_id_map[lid]
                  for lid in in_links_list if lid in link_id_map]
        new_out = [link_id_map[lid]
                   for lid in out_links_list if lid in link_id_map]
        rust_nodes[node_id_map[nid]]["incoming_links"] = new_in
        rust_nodes[node_id_map[nid]]["outgoing_links"] = new_out

    rust_vehicles = []
    for veh_id, veh_data in S["Vehicles"].items():
        old_path = veh_data["Path"] if isinstance(
            veh_data["Path"], list) else veh_data["Path"].tolist()
        new_path = [link_id_map[lid] for lid in old_path if lid in link_id_map]
        if not new_path:
            continue

        rust_vehicles.append({
            "id": int(veh_id),
            "class_id": int(veh_data["VehicleClass"]),
            "path": new_path,
            "current_link_idx": 0,
            "entry_time": float(veh_data["NetworkArrivalTime"])
        })

    # 4. Run Rust Simulation
    start_time = float(S["General"]["SimulationDuration"][0])
    duration = float(S["General"]["SimulationDuration"][1])

    nodes_json = json.dumps(rust_nodes, cls=NumpyEncoder)
    links_json = json.dumps(rust_links, cls=NumpyEncoder)
    vehicles_json = json.dumps(rust_vehicles, cls=NumpyEncoder)

    sim = stream_rust.Simulation()
    sim.load_scenario(nodes_json, links_json, vehicles_json, start_time)

    print(f"Running Rust Simulation ({duration}s)...")
    t0 = time.time()
    count = sim.run(duration)
    print(
        f"Simulation complete in {time.time()-t0:.4f}s. Processed {count} events.")

    # 5. Merge Results back to Python
    print("Merging results...")
    results_json = sim.get_vehicle_results()
    results = json.loads(results_json)

    for res in results:
        veh_id = res["id"]
        if veh_id in S["Vehicles"]:
            node_times = np.array(res["node_times"])
            S["Vehicles"][veh_id]["NodeTimes"] = node_times

            # Truncate RealPath to match recorded times
            completed_links_count = max(0, len(node_times) - 1)
            full_path = S["Vehicles"][veh_id]["Path"]
            S["Vehicles"][veh_id]["RealPath"] = full_path[:completed_links_count]

    # 6. Run Original Analysis
    Simulation = S

    print("\n--- Starting Analysis ---")

    # Export CSVs
    output_dir = "results"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Exporting CSVs to {output_dir}/...")
    try:
        export_travel_times_on_links(Simulation, output_dir)
        export_flow_speed_on_links(Simulation, output_dir)
    except Exception as e:
        print(f"Warning during export: {e}")

    """
    Graphs
    """
    plt.close("all")
    TravelTimes = compute_travel_times_on_links(Simulation)
    Statistics = compute_stats_on_links(Simulation, TravelTimes)

    print("Plotting Network...")
    plot_network(Simulation)

    linkid = list(Simulation['Links'])[0]
    NumIns = [Simulation['Nodes'][nodeid]['NumIncomingLinks']
              for nodeid in list(Simulation['Nodes'])]
    NumOuts = [Simulation['Nodes'][nodeid]['NumOutgoingLinks']
               for nodeid in list(Simulation['Nodes'])]
    nodeid_arr = np.intersect1d(np.where(np.array(NumIns) > 0)[
                                0],  np.where(np.array(NumOuts) > 0)[0])
    if len(nodeid_arr) == 0:
        nodeid = -1
    else:
        nodeid = nodeid_arr[-1]
        nodeid = list(Simulation['Nodes'])[nodeid]
    nodeid = 1

    print("Plotting Trafficolor...")
    plot_trafficolor_on_network(Simulation, Statistics)
    plot_flow_speed_on_link(Statistics, linkid)
    plot_cvc_on_link(Statistics, linkid)

    if len(Simulation['Routes']) > 4:
        Path = Simulation['Routes'][4]['Path']
        plot_travel_times_on_path(Simulation, Path, bool_network=True)

    print("Analysis complete.")


if __name__ == "__main__":
    run_analysis()

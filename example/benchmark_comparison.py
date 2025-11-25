import time
import numpy as np
import sys
import os
import json

# Ensure we can import stream from root (one level up)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import stream_rust
from stream.initialization.validate_and_complete_scenario import validate_and_complete_scenario
from stream.initialization.assignment import assignment
from stream.initialization.initialize_simulation import initialize_simulation
from stream.simulation.main_simulation_meso import main_simulation_meso

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer): return int(obj)
        elif isinstance(obj, np.floating): return float(obj)
        elif isinstance(obj, np.ndarray): return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

def run_benchmark():
    print("--- Loading Inputs ---")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Default: look for inputs.npy in same folder
    filename = os.path.join(script_dir, "inputs.npy")
    
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    
    if not os.path.exists(filename):
        # Fallback: try example/inputs.npy if running from root but script in example? 
        # (Unlikely if sys.argv is used, but good default)
        print(f"Error: File {filename} not found.")
        return
        
    Inputs = np.load(filename, allow_pickle=True).item()
    
    print("--- Initializing Scenario ---")
    S_base = validate_and_complete_scenario(Inputs)
    S_base = assignment(S_base)
    S_base = initialize_simulation(S_base)
    
    start_time = float(S_base["General"]["SimulationDuration"][0])
    duration = float(S_base["General"]["SimulationDuration"][1])
    
    import copy
    S_python = copy.deepcopy(S_base)
    
    # --- 1. Rust Benchmark ---
    print("\n--- Preparing RUST Core ---")
    # Re-indexing logic from analysis_example.py
    node_id_map = {}
    link_id_map = {}
    inv_link_map = {}
    
    rust_nodes = []
    sorted_node_ids = sorted(S_base["Nodes"].keys())
    for i, nid in enumerate(sorted_node_ids):
        node_id_map[nid] = i
        
    for nid in sorted_node_ids:
        rust_nodes.append({ "id": node_id_map[nid], "incoming_links": [], "outgoing_links": [] })

    rust_links = []
    sorted_link_ids = sorted(S_base["Links"].keys())
    for i, lid in enumerate(sorted_link_ids):
        link_id_map[lid] = i
        inv_link_map[i] = lid

    for lid in sorted_link_ids:
        link_data = S_base["Links"][lid]
        rust_links.append({
            "id": link_id_map[lid],
            "length": float(link_data["Length"]),
            "speed_limit": float(link_data["Speed"]),
            "num_lanes": int(link_data["NumLanes"]),
            "capacity": float(link_data["FD"]["C"]) * int(link_data["NumLanes"]),
            "jam_density": float(link_data["FD"]["kx"]) * int(link_data["NumLanes"]) * 1000.0
        })

    for nid in sorted_node_ids:
        node_data = S_base["Nodes"][nid]
        in_links = node_data["IncomingLinksID"]
        out_links = node_data["OutgoingLinksID"]
        in_links_list = in_links.tolist() if isinstance(in_links, np.ndarray) else list(in_links)
        out_links_list = out_links.tolist() if isinstance(out_links, np.ndarray) else list(out_links)
        
        new_in = [link_id_map[lid] for lid in in_links_list if lid in link_id_map]
        new_out = [link_id_map[lid] for lid in out_links_list if lid in link_id_map]
        rust_nodes[node_id_map[nid]]["incoming_links"] = new_in
        rust_nodes[node_id_map[nid]]["outgoing_links"] = new_out

    rust_vehicles = []
    for veh_id, veh_data in S_base["Vehicles"].items():
        old_path = veh_data["Path"] if isinstance(veh_data["Path"], list) else veh_data["Path"].tolist()
        new_path = [link_id_map[lid] for lid in old_path if lid in link_id_map]
        if not new_path: continue
        
        rust_vehicles.append({
            "id": int(veh_id),
            "class_id": int(veh_data["VehicleClass"]),
            "path": new_path,
            "current_link_idx": 0,
            "entry_time": float(veh_data["NetworkArrivalTime"])
        })

    nodes_json = json.dumps(rust_nodes, cls=NumpyEncoder)
    links_json = json.dumps(rust_links, cls=NumpyEncoder)
    vehicles_json = json.dumps(rust_vehicles, cls=NumpyEncoder)
    
    sim = stream_rust.Simulation()
    try:
        sim.load_scenario(nodes_json, links_json, vehicles_json, start_time)
    except TypeError:
        print("Warning: Rust extension expects 3 arguments (old version?). ignoring start_time.")
        sim.load_scenario(nodes_json, links_json, vehicles_json)
    
    print("\n--- Running RUST Core ---")
    start_rust = time.time()
    events_count = sim.run(duration)
    end_rust = time.time()
    time_rust = end_rust - start_rust
    print(f"Rust Time: {time_rust:.4f} seconds ({events_count} events)")

    # --- 2. Python Benchmark ---
    print("\n--- Running PYTHON Core ---")
    try:
        start_py = time.time()
        S_python = main_simulation_meso(S_python, duration)
        end_py = time.time()
        time_py = end_py - start_py
        print(f"Python Time: {time_py:.4f} seconds")
    except Exception as e:
        print(f"Python Core Failed: {e}")
        import traceback
        traceback.print_exc()
        time_py = -1.0
        S_python = None

    # --- 3. Comparison ---
    print("\n--- Validation ---")
    rust_results_json = sim.get_vehicle_results()
    rust_results = json.loads(rust_results_json)
    rust_map = {r["id"]: r for r in rust_results}
    
    # Metrics
    time_errors = []
    py_durations = []
    ru_durations = []
    py_link_counts = {lid: 0 for lid in S_base["Links"]}
    ru_link_counts = {lid: 0 for lid in S_base["Links"]}

    if S_python:
        for veh_id in S_python["Vehicles"]:
            if veh_id in rust_map:
                py_veh = S_python["Vehicles"][veh_id]
                ru_veh = rust_map[veh_id]
                
                py_times = py_veh["NodeTimes"]
                ru_times = ru_veh["node_times"]
                
                # Compare Times (Aligned)
                min_len = min(len(py_times), len(ru_times))
                if min_len > 0:
                    diff = np.abs(np.array(py_times[:min_len]) - np.array(ru_times[:min_len]))
                    time_errors.extend(diff)
                
                # Compare Durations
                valid_py_times = [t for t in py_times if t > 0.0]
                if len(valid_py_times) > 1:
                    py_durations.append(valid_py_times[-1] - valid_py_times[0])
                
                if len(ru_times) > 1:
                    ru_durations.append(ru_times[-1] - ru_times[0])
                    
                # Link Counts
                py_path = py_veh["RealPath"]
                for link_id in py_path:
                    if link_id in py_link_counts: py_link_counts[link_id] += 1
                
                completed_links = max(0, len(ru_times) - 1)
                ru_path = ru_veh["real_path"]
                for i in range(min(completed_links, len(ru_path))):
                    rust_idx = ru_path[i]
                    orig_id = inv_link_map[rust_idx]
                    if orig_id in ru_link_counts: ru_link_counts[orig_id] += 1
    else:
        # Independent Rust Stats
        for veh_id, ru_veh in rust_map.items():
            ru_times = ru_veh["node_times"]
            if len(ru_times) > 1:
                ru_durations.append(ru_times[-1] - ru_times[0])
            
            completed_links = max(0, len(ru_times) - 1)
            ru_path = ru_veh["real_path"]
            for i in range(min(completed_links, len(ru_path))):
                rust_idx = ru_path[i]
                orig_id = inv_link_map[rust_idx]
                if orig_id in ru_link_counts: ru_link_counts[orig_id] += 1

    # Report
    if len(time_errors) > 0:
        print(f"1. Node Passage Times MAE: {np.mean(time_errors):.2f} s")
    
    if len(ru_durations) > 0:
        ru_avg = np.mean(ru_durations)
        if len(py_durations) > 0:
            py_avg = np.mean(py_durations)
            print(f"2. Avg Trip Duration: Python={py_avg:.2f}s, Rust={ru_avg:.2f}s")
            print(f"   Difference: {abs(py_avg - ru_avg):.2f}s")
        else:
            print(f"2. Avg Trip Duration: Rust={ru_avg:.2f}s (Python failed)")

    l_ids = sorted(list(S_base["Links"].keys()))
    py_counts = np.array([py_link_counts[i] for i in l_ids])
    ru_counts = np.array([ru_link_counts[i] for i in l_ids])
    
    if S_python:
        print(f"3. Link Volume MAE: {np.mean(np.abs(py_counts - ru_counts)):.2f} vehicles")
        print(f"   Total Vehicles Moved: Python={np.sum(py_counts)}, Rust={np.sum(ru_counts)}")
    else:
        print(f"3. Link Volume: Rust={np.sum(ru_counts)} vehicles (Python failed)")

    print("\n==================================")
    print(f"Rust Core:   {time_rust:.4f} s")
    print(f"Python Core: {time_py:.4f} s")
    if time_rust > 0:
        if time_py > 0:
            print(f"Speedup:     {time_py / time_rust:.2f}x")
        else:
            print(f"Speedup:     N/A (Python failed)")
    else:
        print("Speedup:     Infinite (Rust < 0.0001s)")
    print("==================================")

if __name__ == "__main__":
    run_benchmark()


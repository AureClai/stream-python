import numpy as np
import os


def create_scenarios():
    # Load template to preserve schema
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Handle both root and example/ execution contexts
    # If running from root, template is example/inputs.npy
    # If running from example/, template is inputs.npy
    # Assuming script is IN example/ now or will be.
    # I'll look for template relative to script.
    # Template is usually alongside the script if we move script to example/.
    
    template_path = os.path.join(script_dir, "inputs.npy")
    if not os.path.exists(template_path):
        # Fallback if running from root and script is in root (before move)
        template_path = os.path.join(script_dir, "example", "inputs.npy")
    
    if not os.path.exists(template_path):
        print(f"Error: Template inputs.npy not found at {template_path}.")
        return

    base_inputs = np.load(template_path, allow_pickle=True).item()

    # Common definitions
    FD = {'u': 25.0, 'C': 0.5, 'kx': 0.15, 'w': 5.0}

    link_defaults = {"Capacity": None, "road_type": 1,
                     "Priority": None, "name": None}

    # Helpers
    def make_points(x1, y1, x2, y2):
        return np.array([[x1, x2], [y1, y2]])

    def save_inputs(name, data):
        # Save to same dir as script (or example/ if script in root)
        if "example" in script_dir:
             path = os.path.join(script_dir, name)
        else:
             path = os.path.join(script_dir, "example", name)
        np.save(path, data)
        print(f"Saved {path}")

    # ---------------------------------------------------------
    # Scenario 1: Free Flow
    # ---------------------------------------------------------
    print("Generating inputs_freeflow.npy...")
    inputs = base_inputs.copy()

    inputs["Periods"] = {1: {'start': 0}, 2: {'start': 3600}}

    inputs["Nodes"] = {
        1: {"IncomingLinksID": np.array([]), "OutgoingLinksID": np.array([1]), "NumIncomingLinks": 0, "NumOutgoingLinks": 1},
        2: {"IncomingLinksID": np.array([1]), "OutgoingLinksID": np.array([2]), "NumIncomingLinks": 1, "NumOutgoingLinks": 1},
        3: {"IncomingLinksID": np.array([2]), "OutgoingLinksID": np.array([]), "NumIncomingLinks": 1, "NumOutgoingLinks": 0}
    }

    inputs["Links"] = {
        1: {**link_defaults, "NodeUpID": 1, "NodeDownID": 2, "Length": 1000.0, "NumLanes": 1, "Speed": 25.0, "FD": FD,
            "Points": make_points(0, 0, 1000, 0)},
        2: {**link_defaults, "NodeUpID": 2, "NodeDownID": 3, "Length": 1000.0, "NumLanes": 1, "Speed": 25.0, "FD": FD,
            "Points": make_points(1000, 0, 2000, 0)}
    }

    inputs["Entries"] = {1: {}}
    inputs["Exits"] = {3: {}}
    inputs["Demand"] = np.array([[1, 1, 1, 3, 360.0]])
    inputs["General"]["SimulationDuration"] = (0.0, 3600.0)
    save_inputs("inputs_freeflow.npy", inputs)

    # ---------------------------------------------------------
    # Scenario 2: Bottleneck
    # ---------------------------------------------------------
    print("Generating inputs_bottleneck.npy...")
    inputs = base_inputs.copy()

    inputs["Periods"] = {1: {'start': 0}, 2: {'start': 3600}}

    inputs["Nodes"] = {
        1: {"IncomingLinksID": np.array([]), "OutgoingLinksID": np.array([1]), "NumIncomingLinks": 0, "NumOutgoingLinks": 1},
        2: {"IncomingLinksID": np.array([1]), "OutgoingLinksID": np.array([2]), "NumIncomingLinks": 1, "NumOutgoingLinks": 1},
        3: {"IncomingLinksID": np.array([2]), "OutgoingLinksID": np.array([]), "NumIncomingLinks": 1, "NumOutgoingLinks": 0}
    }

    FD_2lane = FD.copy()
    FD_1lane = FD.copy()

    inputs["Links"] = {
        1: {**link_defaults, "NodeUpID": 1, "NodeDownID": 2, "Length": 1000.0, "NumLanes": 2, "Speed": 25.0, "FD": FD_2lane,
            "Points": make_points(0, 0, 1000, 0)},
        2: {**link_defaults, "NodeUpID": 2, "NodeDownID": 3, "Length": 1000.0, "NumLanes": 1, "Speed": 25.0, "FD": FD_1lane,
            "Points": make_points(1000, 0, 2000, 0)}
    }

    inputs["Entries"] = {1: {}}
    inputs["Exits"] = {3: {}}
    inputs["Demand"] = np.array([[1, 1, 1, 3, 2500.0]])
    inputs["General"]["SimulationDuration"] = (0.0, 3600.0)
    save_inputs("inputs_bottleneck.npy", inputs)

    # ---------------------------------------------------------
    # Scenario 3: Diverge
    # ---------------------------------------------------------
    print("Generating inputs_diverge.npy...")
    inputs = base_inputs.copy()

    inputs["Periods"] = {1: {'start': 0}, 2: {'start': 3600}}

    inputs["Nodes"] = {
        1: {"IncomingLinksID": np.array([]), "OutgoingLinksID": np.array([1]), "NumIncomingLinks": 0, "NumOutgoingLinks": 1},
        2: {"IncomingLinksID": np.array([1]), "OutgoingLinksID": np.array([2, 3]), "NumIncomingLinks": 1, "NumOutgoingLinks": 2},
        3: {"IncomingLinksID": np.array([2]), "OutgoingLinksID": np.array([]), "NumIncomingLinks": 1, "NumOutgoingLinks": 0},
        4: {"IncomingLinksID": np.array([3]), "OutgoingLinksID": np.array([]), "NumIncomingLinks": 1, "NumOutgoingLinks": 0}
    }

    inputs["Links"] = {
        1: {**link_defaults, "NodeUpID": 1, "NodeDownID": 2, "Length": 1000.0, "NumLanes": 2, "Speed": 25.0, "FD": FD,
            "Points": make_points(0, 0, 1000, 0)},
        2: {**link_defaults, "NodeUpID": 2, "NodeDownID": 3, "Length": 1000.0, "NumLanes": 1, "Speed": 25.0, "FD": FD,
            "Points": make_points(1000, 0, 2000, 0)},  # Straight to 3
        3: {**link_defaults, "NodeUpID": 2, "NodeDownID": 4, "Length": 1000.0, "NumLanes": 1, "Speed": 25.0, "FD": FD,
            "Points": make_points(1000, 0, 1000, 1000)}  # Up to 4
    }

    inputs["Entries"] = {1: {}}
    inputs["Exits"] = {3: {}, 4: {}}
    inputs["Demand"] = np.array([
        [1, 1, 1, 3, 1500.0],
        [1, 1, 1, 4, 1500.0]
    ])

    inputs["General"]["SimulationDuration"] = (0.0, 3600.0)
    save_inputs("inputs_diverge.npy", inputs)

    # ---------------------------------------------------------
    # Scenario 4: Stress Test (Long Chain)
    # ---------------------------------------------------------
    print("Generating inputs_stress.npy...")
    inputs = base_inputs.copy()

    num_links = 100
    nodes = {}
    links = {}

    # Create a chain: 0 -> 1 -> 2 ... -> 100
    for i in range(num_links + 1):
        in_links = np.array([i-1]) if i > 0 else np.array([])
        out_links = np.array([i]) if i < num_links else np.array([])
        nodes[i] = {
            "IncomingLinksID": in_links,
            "OutgoingLinksID": out_links,
            "NumIncomingLinks": 1 if i > 0 else 0,
            "NumOutgoingLinks": 1 if i < num_links else 0
        }

    for i in range(num_links):
        links[i] = {
            **link_defaults,
            "NodeUpID": i,
            "NodeDownID": i+1,
            "Length": 100.0,  # Short links to maximize event density
            "NumLanes": 1,
            "Speed": 25.0,
            "FD": FD,  # C=0.5 (1800 veh/h)
            "Points": make_points(i*100, 0, (i+1)*100, 0)
        }

    inputs["Nodes"] = nodes
    inputs["Links"] = links
    inputs["Entries"] = {0: {}}
    inputs["Exits"] = {num_links: {}}
    inputs["Periods"] = {1: {'start': 0}, 2: {'start': 7200}}

    # High Demand: 1500 veh/h (Below Cap 1800 to keep moving, but high volume)
    inputs["Demand"] = np.array([[1, 1, 0, num_links, 1500.0]])
    inputs["General"]["SimulationDuration"] = (0.0, 7200.0)

    save_inputs("inputs_stress.npy", inputs)

    # ---------------------------------------------------------
    # Scenario 5: Manhattan Grid (Congestion & Routing)
    # ---------------------------------------------------------
    print("Generating inputs_grid.npy...")
    inputs = base_inputs.copy()

    # 5x5 Grid. Nodes 0..24.
    # Rows i=0..4, Cols j=0..4. NodeID = i*5 + j.
    grid_size = 5
    nodes = {}
    links = {}
    link_id_counter = 1

    # Initialize nodes
    for r in range(grid_size):
        for c in range(grid_size):
            nid = r * grid_size + c
            nodes[nid] = {
                "IncomingLinksID": [],
                "OutgoingLinksID": [],
                "NumIncomingLinks": 0,
                "NumOutgoingLinks": 0,
                # Grid nodes are internal by default
            }

    # Create Links (Bidirectional)
    for r in range(grid_size):
        for c in range(grid_size):
            u = r * grid_size + c
            # Right neighbor
            if c < grid_size - 1:
                v = r * grid_size + (c + 1)
                # u -> v
                lid = link_id_counter
                links[lid] = {**link_defaults, "NodeUpID": u, "NodeDownID": v, "Length": 200.0, "NumLanes": 1,
                              "Speed": 15.0, "FD": FD, "Points": make_points(c*200, r*200, (c+1)*200, r*200)}
                nodes[u]["OutgoingLinksID"] = np.append(
                    nodes[u].get("OutgoingLinksID", []), lid)
                nodes[v]["IncomingLinksID"] = np.append(
                    nodes[v].get("IncomingLinksID", []), lid)
                link_id_counter += 1

                # v -> u
                lid = link_id_counter
                links[lid] = {**link_defaults, "NodeUpID": v, "NodeDownID": u, "Length": 200.0, "NumLanes": 1,
                              "Speed": 15.0, "FD": FD, "Points": make_points((c+1)*200, r*200, c*200, r*200)}
                nodes[v]["OutgoingLinksID"] = np.append(
                    nodes[v].get("OutgoingLinksID", []), lid)
                nodes[u]["IncomingLinksID"] = np.append(
                    nodes[u].get("IncomingLinksID", []), lid)
                link_id_counter += 1

            # Bottom neighbor
            if r < grid_size - 1:
                v = (r + 1) * grid_size + c
                # u -> v
                lid = link_id_counter
                links[lid] = {**link_defaults, "NodeUpID": u, "NodeDownID": v, "Length": 200.0, "NumLanes": 1,
                              "Speed": 15.0, "FD": FD, "Points": make_points(c*200, r*200, c*200, (r+1)*200)}
                nodes[u]["OutgoingLinksID"] = np.append(
                    nodes[u].get("OutgoingLinksID", []), lid)
                nodes[v]["IncomingLinksID"] = np.append(
                    nodes[v].get("IncomingLinksID", []), lid)
                link_id_counter += 1

                # v -> u
                lid = link_id_counter
                links[lid] = {**link_defaults, "NodeUpID": v, "NodeDownID": u, "Length": 200.0, "NumLanes": 1,
                              "Speed": 15.0, "FD": FD, "Points": make_points(c*200, (r+1)*200, c*200, r*200)}
                nodes[v]["OutgoingLinksID"] = np.append(
                    nodes[v].get("OutgoingLinksID", []), lid)
                nodes[u]["IncomingLinksID"] = np.append(
                    nodes[u].get("IncomingLinksID", []), lid)
                link_id_counter += 1

    # Update Node Counts and Types
    entries = {}
    exits = {}
    for nid in nodes:
        nodes[nid]["NumIncomingLinks"] = len(nodes[nid]["IncomingLinksID"])
        nodes[nid]["NumOutgoingLinks"] = len(nodes[nid]["OutgoingLinksID"])
        # Boundary nodes are entries/exits
        r, c = divmod(nid, grid_size)
        if r == 0 or r == grid_size-1 or c == 0 or c == grid_size-1:
            entries[nid] = {}
            exits[nid] = {}

    inputs["Nodes"] = nodes
    inputs["Links"] = links
    inputs["Entries"] = entries
    inputs["Exits"] = exits
    inputs["Periods"] = {1: {'start': 0}, 2: {'start': 3600}}

    # Demand: Cross traffic
    # Top-Left to Bottom-Right (0 -> 24)
    # Top-Right to Bottom-Left (4 -> 20)
    # 1500 veh/h each. They will intersect in the middle.
    inputs["Demand"] = np.array([
        [1, 1, 0, 24, 1500.0],
        [1, 1, 4, 20, 1500.0]
    ])
    inputs["General"]["SimulationDuration"] = (0.0, 3600.0)

    save_inputs("inputs_grid.npy", inputs)

    print("Done.")


if __name__ == "__main__":
    create_scenarios()

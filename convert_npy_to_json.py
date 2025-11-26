import numpy as np
import json
import sys
import os

# Ensure we can import from stream package
sys.path.insert(0, os.path.abspath("."))

from stream.initialization.validate_and_complete_scenario import validate_and_complete_scenario

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

def convert_npy_to_json(input_path, output_path):
    print(f"Loading {input_path}...")
    Inputs = np.load(input_path, allow_pickle=True).item()
    
    # Validate to complete missing fields
    S = validate_and_complete_scenario(Inputs)
    
    # Mapping to new Rust ID space (0-based contiguous)
    node_id_map = {}
    link_id_map = {}
    
    # 1. Nodes
    rust_nodes = []
    sorted_node_ids = sorted(S["Nodes"].keys())
    for i, nid in enumerate(sorted_node_ids):
        node_id_map[nid] = i
    
    # 2. Links
    rust_links = []
    sorted_link_ids = sorted(S["Links"].keys())
    for i, lid in enumerate(sorted_link_ids):
        link_id_map[lid] = i
        
    # Build Links
    for lid in sorted_link_ids:
        l = S["Links"][lid]
        
        # Handle geometry points
        points = []
        if "Points" in l:
            pts = l["Points"]
            # Handle various shapes: 2xN (standard) or Nx2
            if pts.shape[0] == 2 and pts.shape[1] >= 2: # 2xN
                for k in range(pts.shape[1]):
                    points.append((float(pts[0,k]), float(pts[1,k])))
            elif pts.shape[1] == 2 and pts.shape[0] >= 2: # Nx2
                for k in range(pts.shape[0]):
                    points.append((float(pts[k,0]), float(pts[k,1])))
            else:
                pass

        rust_links.append({
            "id": link_id_map[lid],
            "node_up": node_id_map[l["NodeUpID"]],
            "node_down": node_id_map[l["NodeDownID"]],
            "length": float(l["Length"]),
            "speed": float(l["Speed"]),
            "num_lanes": int(l["NumLanes"]),
            "capacity": float(l["FD"]["C"]) * int(l["NumLanes"]),
            "fd": {
                "u": float(l["FD"]["u"]),
                "w": float(l["FD"]["w"]),
                "kx": float(l["FD"]["kx"]),
                "c": float(l["FD"]["C"])
            },
            "points": points,
            "priority": float(l.get("Priority", 1.0))
        })

    # Build Nodes
    for nid in sorted_node_ids:
        n = S["Nodes"][nid]
        in_links = [link_id_map[x] for x in n["IncomingLinksID"] if x in link_id_map]
        out_links = [link_id_map[x] for x in n["OutgoingLinksID"] if x in link_id_map]
        
        # Centroid for points
        px, py = 0.0, 0.0
        found_coords = False
        
        # 1. Try Explicit Points
        if "Points" in n:
            pts = n["Points"]
            if pts.size >= 2:
                if pts.shape[0] == 2: # [[x],[y]]
                    px, py = float(pts[0,0]), float(pts[1,0])
                    found_coords = True
                elif pts.shape[1] == 2: # [[x,y]]
                    px, py = float(pts[0,0]), float(pts[0,1])
                    found_coords = True
        
        # 2. Infer from Outgoing Links (First Point)
        if not found_coords:
            for out_lid in out_links:
                # rust_links is indexed by 0..N, which matches link_id_map values
                link = rust_links[out_lid]
                if link["points"] and len(link["points"]) > 0:
                    px, py = link["points"][0]
                    found_coords = True
                    break
        
        # 3. Infer from Incoming Links (Last Point)
        if not found_coords:
            for in_lid in in_links:
                link = rust_links[in_lid]
                if link["points"] and len(link["points"]) > 0:
                    px, py = link["points"][-1]
                    found_coords = True
                    break

        node_type_int = int(n["Type"])
        node_type_str = "Internal"
        if node_type_int == 1: node_type_str = "Entry"
        elif node_type_int == 2: node_type_str = "Exit"

        rust_nodes.append({
            "id": node_id_map[nid],
            "node_type": node_type_str,
            "incoming_links": in_links,
            "outgoing_links": out_links,
            "points": (px, py),
            "signals": []
        })

    # Build Vehicles
    rust_vehicles = []
    if "Vehicles" in S:
        for vid, v in S["Vehicles"].items():
            raw_path = v["Path"]
            path = [link_id_map[x] for x in raw_path if x in link_id_map]
            
            if not path: continue
                
            origin = rust_links[path[0]]["node_up"]
            dest = rust_links[path[-1]]["node_down"]

            rust_vehicles.append({
                "id": int(vid),
                "class_id": int(v.get("VehicleClass", 0)),
                "path": path,
                "start_time": float(v["NetworkArrivalTime"]),
                "origin": origin,
                "destination": dest
            })

    # Build Demand
    rust_demand = []
    if "Demand" in S and "Periods" in S:
        demand_arr = S["Demand"]
        periods = S["Periods"]
        for row in demand_arr:
            per_idx = int(row[0])
            origin_nid = int(row[2])
            dest_nid = int(row[3])
            count = float(row[4])
            
            if count <= 0: continue
            
            if origin_nid not in node_id_map or dest_nid not in node_id_map:
                continue
                
            rust_origin = node_id_map[origin_nid]
            rust_dest = node_id_map[dest_nid]
            
            p_start = float(periods[per_idx]['start'])
            p_end = p_start + 3600.0 
            if per_idx + 1 in periods:
                p_end = float(periods[per_idx+1]['start'])
            elif "end" in periods[per_idx]:
                p_end = float(periods[per_idx]['end'])
            else:
                p_end = float(S["General"]["SimulationDuration"][1])

            rust_demand.append({
                "period_start": p_start,
                "period_end": p_end,
                "origin": rust_origin,
                "destination": rust_dest,
                "flow": count / ((p_end - p_start)/3600.0),
                "count": count
            })

    scenario = {
        "nodes": rust_nodes,
        "links": rust_links,
        "vehicles": rust_vehicles,
        "demand": rust_demand,
        "start_time": float(S["General"]["SimulationDuration"][0]),
        "duration": float(S["General"]["SimulationDuration"][1])
    }

    with open(output_path, 'w') as f:
        json.dump(scenario, f, cls=NumpyEncoder, indent=2)
    
    print(f"Converted {len(rust_nodes)} nodes, {len(rust_links)} links, {len(rust_vehicles)} vehicles.")
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python convert_npy_to_json.py <input.npy> <output.json>")
        sys.exit(1)
    
    convert_npy_to_json(sys.argv[1], sys.argv[2])

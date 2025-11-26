import json
import os
import sys
import shutil

def decompose(json_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    with open(json_path, 'r') as f:
        data = json.load(f)
        
    # 1. Network (GeoJSON)
    features = []
    
    # Nodes
    for node in data["nodes"]:
        # Check point format
        coords = node["points"]
        # If it's [x, y], great. If tuple, convert.
        
        props = {
            "id": node["id"],
            "type": node["node_type"],
            "signals": node["signals"]
        }
        
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": coords
            },
            "properties": props
        }
        features.append(feature)
        
    # Links
    for link in data["links"]:
        coords = link["points"]
        # Ensure LineString format
        
        props = {
            "id": link["id"],
            "node_up": link["node_up"],
            "node_down": link["node_down"],
            "length": link["length"],
            "speed": link["speed"],
            "lanes": link["num_lanes"],
            "capacity": link["capacity"],
            "fd_u": link["fd"]["u"],
            "fd_w": link["fd"]["w"],
            "fd_kx": link["fd"]["kx"],
            "fd_c": link["fd"]["c"]
        }
        
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": coords
            },
            "properties": props
        }
        features.append(feature)
        
    network_fc = {
        "type": "FeatureCollection",
        "features": features
    }
    
    with open(os.path.join(output_dir, "network.geojson"), 'w') as f:
        json.dump(network_fc, f, indent=2)
        
    # 2. Demand
    with open(os.path.join(output_dir, "demand.json"), 'w') as f:
        json.dump(data["demand"], f, indent=2)
        
    # 3. Config (General)
    config = {
        "start_time": data["start_time"],
        "duration": data["duration"]
    }
    with open(os.path.join(output_dir, "config.json"), 'w') as f:
        json.dump(config, f, indent=2)
        
    print(f"Decomposed {json_path} into {output_dir}/")

if __name__ == "__main__":
    base_dir = "../stream-core-rust/scenarios"
    scenarios = ["bottleneck", "diverge", "grid"]
    
    for s in scenarios:
        json_path = os.path.join(base_dir, f"{s}.json")
        out_dir = os.path.join(base_dir, s)
        if os.path.exists(json_path):
            decompose(json_path, out_dir)


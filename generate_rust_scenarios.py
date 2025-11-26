import numpy as np
import sys
import os
import json

sys.path.insert(0, os.path.abspath("."))
from stream.initialization.validate_and_complete_scenario import validate_and_complete_scenario
from convert_npy_to_json import convert_npy_to_json, NumpyEncoder

def save_as_json(Inputs, output_path):
    # Save temp npy
    temp_npy = "temp.npy"
    np.save(temp_npy, Inputs)
    # Convert
    convert_npy_to_json(temp_npy, output_path)
    # Clean
    if os.path.exists(temp_npy):
        os.remove(temp_npy)

def create_bottleneck():
    print("Creating Bottleneck...")
    # 2 Links: Link 1 (Cap 2000) -> Link 2 (Cap 1000)
    S = {}
    S["General"] = {"SimulationDuration": [0, 3600], "SimulationModel": "MesoLWR"}
    
    # Nodes: 0->Entry, 1->Internal, 2->Exit
    # Points: 2xN format [[x...], [y...]]
    S["Nodes"] = {
        0: {"Type": 1, "IncomingLinksID": [], "OutgoingLinksID": [0], "Points": np.array([[0],[0]])},
        1: {"Type": 0, "IncomingLinksID": [0], "OutgoingLinksID": [1], "Points": np.array([[1000],[0]])},
        2: {"Type": 2, "IncomingLinksID": [1], "OutgoingLinksID": [], "Points": np.array([[2000],[0]])}
    }
    
    # Links
    S["Links"] = {
        0: {
            "NodeUpID": 0, "NodeDownID": 1, "Length": 1000, "Speed": 25, "NumLanes": 2, 
            "Capacity": 1.0, 
            "FD": {"u": 25, "w": 5, "kx": 0.15, "C": 0.5}, 
            "Points": np.array([[0, 1000], [0, 0]]), "Priority": 1
        },
        1: {
            "NodeUpID": 1, "NodeDownID": 2, "Length": 1000, "Speed": 25, "NumLanes": 1,
            "Capacity": 0.5, 
            "FD": {"u": 25, "w": 5, "kx": 0.15, "C": 0.5},
            "Points": np.array([[1000, 2000], [0, 0]]), "Priority": 1
        }
    }
    
    S["Demand"] = np.array([[0, 1, 0, 2, 2500]])
    S["Periods"] = {0: {"start": 0, "end": 3600}}
    S["VehicleClass"] = {1: {"Name": "Car"}}
    S["Traffic"] = {"FD": {"u": 25, "w": 5, "kx": 0.15, "C": 0.5}}
    S["Entries"] = {0: {}}
    S["Exits"] = {2: {}}
    
    save_as_json(S, "../stream-core-rust/scenarios/bottleneck.json")

def create_diverge():
    print("Creating Diverge...")
    S = {}
    S["General"] = {"SimulationDuration": [0, 3600]}
    S["Nodes"] = {
        0: {"Type": 1, "IncomingLinksID": [], "OutgoingLinksID": [0], "Points": np.array([[0],[0]])},
        1: {"Type": 0, "IncomingLinksID": [0], "OutgoingLinksID": [1, 2], "Points": np.array([[1000],[0]])},
        2: {"Type": 2, "IncomingLinksID": [1], "OutgoingLinksID": [], "Points": np.array([[2000],[500]])},
        3: {"Type": 2, "IncomingLinksID": [2], "OutgoingLinksID": [], "Points": np.array([[2000],[-500]])}
    }
    S["Links"] = {
        0: {"NodeUpID": 0, "NodeDownID": 1, "Length": 1000, "Speed": 25, "NumLanes": 2, "Capacity": 1.0, "Points": np.array([[0,1000],[0,0]])},
        1: {"NodeUpID": 1, "NodeDownID": 2, "Length": 1000, "Speed": 25, "NumLanes": 1, "Capacity": 0.5, "Points": np.array([[1000,2000],[0,500]])},
        2: {"NodeUpID": 1, "NodeDownID": 3, "Length": 1000, "Speed": 25, "NumLanes": 1, "Capacity": 0.5, "Points": np.array([[1000,2000],[0,-500]])}
    }
    for l in S["Links"].values():
        l["FD"] = {"u": 25, "w": 5, "kx": 0.15, "C": 0.5}
        l["Priority"] = 1

    S["Demand"] = np.array([[0, 1, 0, 2, 1000], [0, 1, 0, 3, 1000]])
    S["Periods"] = {0: {"start": 0, "end": 3600}}
    S["VehicleClass"] = {1: {"Name": "Car"}}
    S["Traffic"] = {"FD": {"u": 25, "w": 5, "kx": 0.15, "C": 0.5}}
    S["Entries"] = {0: {}}
    S["Exits"] = {2: {}, 3: {}}

    save_as_json(S, "../stream-core-rust/scenarios/diverge.json")

def create_grid():
    print("Creating Grid 3x3...")
    S = {}
    S["General"] = {"SimulationDuration": [0, 3600]}
    
    Nodes = {}
    Links = {}
    lid = 0
    
    rows = 3
    cols = 3
    spacing = 500
    
    # Create Nodes
    for r in range(rows):
        for c in range(cols):
            nid = r * cols + c
            ntype = 0
            if r == 0 and c == 0: ntype = 1 # Entry
            if r == rows-1 and c == cols-1: ntype = 2 # Exit
            
            x = c * spacing
            y = -r * spacing # Y down (like screen coords or map)
            
            Nodes[nid] = {
                "Type": ntype, 
                "IncomingLinksID": [], 
                "OutgoingLinksID": [],
                "Points": np.array([[x], [y]])
            }
            
    # Create Links
    for r in range(rows):
        for c in range(cols):
            u = r * cols + c
            ux, uy = c*spacing, -r*spacing
            
            # Right neighbor
            if c < cols - 1:
                v = r * cols + (c + 1)
                vx, vy = (c+1)*spacing, -r*spacing
                
                Links[lid] = {
                    "NodeUpID": u, "NodeDownID": v, "Length": spacing, "Speed": 15, 
                    "NumLanes": 1, "Capacity": 0.5, 
                    "FD": {"u": 15, "w": 5, "kx": 0.15, "C": 0.5}, 
                    "Points": np.array([[ux, vx], [uy, vy]]), 
                    "Priority": 1
                }
                Nodes[u]["OutgoingLinksID"].append(lid)
                Nodes[v]["IncomingLinksID"].append(lid)
                lid += 1
                
            # Bottom neighbor
            if r < rows - 1:
                v = (r + 1) * cols + c
                vx, vy = c*spacing, -(r+1)*spacing
                
                Links[lid] = {
                    "NodeUpID": u, "NodeDownID": v, "Length": spacing, "Speed": 15, 
                    "NumLanes": 1, "Capacity": 0.5, 
                    "FD": {"u": 15, "w": 5, "kx": 0.15, "C": 0.5}, 
                    "Points": np.array([[ux, vx], [uy, vy]]), 
                    "Priority": 1
                }
                Nodes[u]["OutgoingLinksID"].append(lid)
                Nodes[v]["IncomingLinksID"].append(lid)
                lid += 1

    S["Nodes"] = Nodes
    S["Links"] = Links
    S["Demand"] = np.array([[0, 1, 0, 8, 3000]])
    S["Periods"] = {0: {"start": 0, "end": 3600}}
    S["VehicleClass"] = {1: {"Name": "Car"}}
    S["Traffic"] = {"FD": {"u": 15, "w": 5, "kx": 0.15, "C": 0.5}}
    S["Entries"] = {0: {}}
    S["Exits"] = {8: {}}
    
    save_as_json(S, "../stream-core-rust/scenarios/grid.json")

if __name__ == "__main__":
    create_bottleneck()
    create_diverge()
    create_grid()

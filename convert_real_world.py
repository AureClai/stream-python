import os
import sys
from convert_npy_to_json import convert_npy_to_json
from decompose_json import decompose

def run():
    input_npy = "example/inputs.npy"
    temp_json = "../stream-core-rust/scenarios/real_world_flat.json"
    output_dir = "../stream-core-rust/scenarios/real_world"
    
    if not os.path.exists(input_npy):
        print(f"Error: {input_npy} not found")
        return

    print(f"Converting {input_npy} to JSON...")
    convert_npy_to_json(input_npy, temp_json)
    
    print(f"Decomposing to Project Structure in {output_dir}...")
    decompose(temp_json, output_dir)
    
    # Clean up flat file
    if os.path.exists(temp_json):
        os.remove(temp_json)
        
    print("Done!")

if __name__ == "__main__":
    run()


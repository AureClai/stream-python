# Stream Data Model

This document describes the data structures used in the `stream` simulation, covering the input format (Python), the internal runtime state (Rust), and the output format.

## 1. Input Data Model (Python)

The simulation input is typically loaded from a `.npy` file or constructed as a Python dictionary. This dictionary, often referred to as `S` (Scenario) or `Inputs`, contains the following primary keys:

### 1.1 Nodes

Key: `Nodes` (Dictionary mapping `NodeID` (int) to `NodeData`)

| Field             | Type      | Description                                                |
| ----------------- | --------- | ---------------------------------------------------------- |
| `Type`            | int       | `1`: Entry (Source), `2`: Exit (Sink), `0`: Internal Node. |
| `IncomingLinksID` | list[int] | List of IDs for links entering this node.                  |
| `OutgoingLinksID` | list[int] | List of IDs for links exiting this node.                   |
| `Points`          | array     | `[x, y]` coordinates for visualization.                    |
| `SignalsID`       | list[int] | IDs of traffic signals controlling this node (optional).   |
| `AlphaOD`         | array     | Merge coefficients (optional).                             |

### 1.2 Links

Key: `Links` (Dictionary mapping `LinkID` (int) to `LinkData`)

| Field        | Type  | Description                                            |
| ------------ | ----- | ------------------------------------------------------ |
| `NodeUpID`   | int   | Upstream Node ID.                                      |
| `NodeDownID` | int   | Downstream Node ID.                                    |
| `Length`     | float | Length of the link in meters.                          |
| `Speed`      | float | Free-flow speed limit ($u$) in m/s.                    |
| `NumLanes`   | int   | Number of lanes.                                       |
| `Capacity`   | float | Flow capacity ($C$) in veh/s (total across all lanes). |
| `FD`         | dict  | Fundamental Diagram parameters (`u`, `w`, `kx`, `C`).  |
| `Points`     | array | Geometry points `[[x1, x2, ...], [y1, y2, ...]]`.      |
| `Priority`   | float | Priority weight for merges.                            |

### 1.3 Vehicles (Demand)

Key: `Vehicles` (Dictionary mapping `VehID` (int) to `VehicleData`)

| Field         | Type      | Description                                     |
| ------------- | --------- | ----------------------------------------------- |
| `Path`        | list[int] | Sequence of Link IDs the vehicle will traverse. |
| `StartTime`   | float     | Desired entry time in seconds.                  |
| `Origin`      | int       | Origin Node ID.                                 |
| `Destination` | int       | Destination Node ID.                            |
| `Class`       | int       | Vehicle class ID (for multi-class simulations). |

### 1.4 Events (Derived/Legacy)

Key: `Events` (Dictionary mapping `NodeID` (int) to `NodeEvents`)

This structure is populated during initialization and updated during simulation (in legacy mode) or reconstructed from Vehicle Results (in Rust mode) to support legacy analysis functions like `node_info`.

- **`Arrivals`**: List of dictionaries (one per incoming link `i`).
  - `Time`: Array of arrival timestamps.
  - `VehID`: Array of arriving vehicle IDs.
- **`Exits`**: List of dictionaries (one per outgoing link `j`).
  - `Time`: Array of exit timestamps.
  - `PreviousLinkID`: Array of IDs indicating where the vehicle came from.

---

## 2. Runtime Data Model (Rust)

The high-performance core converts the Python input into efficient Rust structs.

### 2.1 Simulation State

The main `Simulation` struct holds the global state:

```rust
struct Simulation {
    nodes: Vec<Node>,
    links: Vec<Link>,
    vehicles: Vec<Vehicle>,
    events: BinaryHeap<Event>, // Priority Queue for O(log N) scheduling
    current_time: f64,
}
```

### 2.2 Link (Runtime)

Optimized for flow and storage constraints.

| Field                       | Type              | Purpose                                                                               |
| --------------------------- | ----------------- | ------------------------------------------------------------------------------------- |
| `waiting_queue`             | `VecDeque<VehID>` | Vehicles at the end of the link waiting to move to the next link.                     |
| `entry_queue`               | `VecDeque<VehID>` | Vehicles at a Source Node waiting to enter the network.                               |
| `vehicles_on_link`          | `usize`           | Current number of vehicles (Storage Constraint: $\le L \cdot k_{jam}$).               |
| `next_available_entry_time` | `f64`             | Time when the next vehicle can enter (Flow Constraint: $t \ge t_{prev} + 1/C$).       |
| `last_scheduled_ready_time` | `Option<f64>`     | **Optimization**: Tracks pending wake-up events to prevent duplicates ($O(1)$ check). |

### 2.3 Vehicle (Runtime)

Tracks individual agent state.

| Field              | Type           | Purpose                                                  |
| ------------------ | -------------- | -------------------------------------------------------- |
| `state`            | `VehicleState` | Enum: `QueuedAtEntry`, `Moving`, `Waiting`, `Exited`.    |
| `current_link_idx` | `usize`        | Index in the `path` vector pointing to the current link. |
| `node_times`       | `Vec<f64>`     | History of timestamps when the vehicle passed each node. |

### 2.4 Event System

The core driver of the simulation.

| Event Type       | Description                                                                        |
| ---------------- | ---------------------------------------------------------------------------------- |
| `VehicleEntry`   | A vehicle attempts to enter the network from a Source.                             |
| `VehicleArrival` | A vehicle reaches the downstream end of its current link (enters `waiting_queue`). |
| `LinkExit`       | A vehicle fully leaves a link (freeing up storage capacity).                       |
| `LinkReady`      | A link's flow constraint expires or space opens up; wakes up upstream queues.      |

---

## 3. Output Data Model

After the simulation completes, the Rust core returns results to Python.

### 3.1 Vehicle Results

A list of result objects, one per vehicle:

- **`id`**: Vehicle ID (matches Input ID).
- **`real_path`**: The actual sequence of links traversed (useful if dynamic routing is enabled).
- **`node_times`**: A list of floats representing the time the vehicle passed each node in its path.
  - `node_times[0]`: Entry Time.
  - `node_times[1]`: Exit time from Link 1 / Arrival at Node 2.
  - ...
  - `node_times[N]`: Final Exit Time.

### 3.2 Derived Metrics (Python Analysis)

Standard analysis functions compute:

- **Travel Time**: `node_times[-1] - node_times[0]`
- **Link Volumes**: Aggregated counts of vehicles on links over time intervals.
- **Space-Time Trajectories**: Visualization of vehicle positions ($x, t$).

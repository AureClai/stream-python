use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::{BinaryHeap, VecDeque};
use std::cmp::Ordering;

type NodeID = usize;
type LinkID = usize;
type VehID = usize;

#[derive(Copy, Clone, PartialEq, Eq, Debug)]
enum EventType {
    VehicleEntry,   // Vehicle wants to enter the network (Source)
    VehicleArrival, // Vehicle reaches end of link
    LinkExit,       // Vehicle leaves link
    LinkReady,      // Link flow capacity available
}

#[derive(Copy, Clone, PartialEq)]
struct Event {
    time: f64,
    event_type: EventType,
    link_id: LinkID, 
    veh_id: VehID,
}

impl Eq for Event {}

impl Ord for Event {
    fn cmp(&self, other: &Self) -> Ordering {
        other.time.partial_cmp(&self.time).unwrap_or(Ordering::Equal)
    }
}

impl PartialOrd for Event {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

#[derive(Clone, PartialEq, Serialize, Deserialize, Debug)]
enum VehicleState {
    QueuedAtEntry, // New state
    Waiting, 
    Moving,  
    Exited,  
}

fn default_vehicle_state() -> VehicleState { VehicleState::Moving }

#[derive(Clone, Serialize, Deserialize, Debug)]
struct Vehicle {
    id: VehID,
    class_id: usize,
    path: Vec<LinkID>, 
    current_link_idx: usize, 
    
    #[serde(default)]
    entry_time: f64,

    #[serde(skip, default = "default_vehicle_state")]
    state: VehicleState,

    #[serde(skip)]
    node_times: Vec<f64>, 
}

#[derive(Serialize, Deserialize, Debug)]
struct Link {
    id: LinkID,
    length: f64,
    speed_limit: f64,
    num_lanes: u8,
    
    #[serde(default)] 
    capacity: f64, 
    #[serde(default)]
    jam_density: f64, 

    #[serde(skip)]
    waiting_queue: VecDeque<VehID>, // Waiting to leave link
    
    #[serde(skip)]
    entry_queue: VecDeque<VehID>,   // Waiting to ENTER link (Source)
    
    #[serde(skip)]
    next_available_entry_time: f64, 
    
    #[serde(skip)]
    vehicles_on_link: usize,

    #[serde(skip)]
    last_scheduled_ready_time: Option<f64>,
}

#[derive(Serialize, Deserialize, Debug)]
struct Node {
    id: NodeID,
    incoming_links: Vec<LinkID>,
    outgoing_links: Vec<LinkID>,
}

#[pyclass]
struct Simulation {
    nodes: Vec<Node>,
    links: Vec<Link>,
    vehicles: Vec<Vehicle>,
    events: BinaryHeap<Event>,
    current_time: f64,
    start_time: f64,
}

#[pymethods]
impl Simulation {
    #[new]
    fn new() -> Self {
        Simulation {
            nodes: Vec::new(),
            links: Vec::new(),
            vehicles: Vec::new(),
            events: BinaryHeap::new(),
            current_time: 0.0,
            start_time: 0.0,
        }
    }

    fn load_scenario(&mut self, nodes_json: String, links_json: String, vehicles_json: String, start_time: f64) -> PyResult<()> {
        self.nodes = serde_json::from_str(&nodes_json).map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        self.links = serde_json::from_str(&links_json).map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        self.vehicles = serde_json::from_str(&vehicles_json).map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        
        self.start_time = start_time;
        self.current_time = start_time;

        for i in 0..self.vehicles.len() {
             let v = &mut self.vehicles[i];
             v.node_times = Vec::with_capacity(v.path.len() + 1);
             
             if v.path.len() > 0 {
                 let link_idx = v.path[0]; 
                 if link_idx < self.links.len() {
                     // Schedule ENTRY, not Arrival
                     self.events.push(Event {
                         time: v.entry_time,
                         event_type: EventType::VehicleEntry,
                         link_id: link_idx,
                         veh_id: i,
                     });
                     v.state = VehicleState::QueuedAtEntry;
                 }
             }
        }
        Ok(())
    }

    fn run(&mut self, max_time: f64) -> PyResult<usize> {
        let mut events_processed = 0;
        while let Some(event) = self.events.pop() {
            if event.time > max_time {
                self.events.push(event);
                break;
            }
            self.current_time = event.time;
            events_processed += 1;
            
            match event.event_type {
                EventType::VehicleEntry => {
                    self.handle_vehicle_entry(event.link_id, event.veh_id);
                }
                EventType::VehicleArrival => {
                    self.handle_vehicle_arrival(event.link_id, event.veh_id);
                }
                EventType::LinkExit => {
                    self.handle_link_exit(event.link_id);
                }
                EventType::LinkReady => {
                    self.handle_link_ready(event.link_id);
                }
            }
        }
        Ok(events_processed)
    }
    
    fn get_vehicle_results(&self) -> PyResult<String> {
        #[derive(Serialize)]
        struct VehResult {
            id: VehID,
            node_times: Vec<f64>,
            real_path: Vec<LinkID>,
        }
        let results: Vec<VehResult> = self.vehicles.iter().map(|v| VehResult {
            id: v.id,
            node_times: v.node_times.clone(),
            real_path: v.path.clone(), 
        }).collect();
        serde_json::to_string(&results).map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }
}

impl Simulation {
    fn handle_vehicle_entry(&mut self, link_id: LinkID, veh_id: VehID) {
        if link_id >= self.links.len() { return; }
        
        // Record Entry Demand Time (Attempt to enter)
        // self.vehicles[veh_id].node_times.push(self.current_time); // No, node_times is usually "Time Passed Node"
        // If we record entry here, we might record multiple times if queued? 
        // Let's record the scheduled time as the first point.
        if self.vehicles[veh_id].node_times.is_empty() {
             self.vehicles[veh_id].node_times.push(self.current_time);
        }

        let link = &mut self.links[link_id];
        link.entry_queue.push_back(veh_id);
        
        // Try to push from entry queue
        self.process_entry_queue(link_id);
    }

    fn process_entry_queue(&mut self, link_id: LinkID) {
        let link = &mut self.links[link_id]; // Borrow checking issues? 
        // We need to access link state AND event queue.
        // We can copy state variables needed to check.
        
        // Peek
        while let Some(&veh_id) = link.entry_queue.front() {
             let max_veh = (link.length * link.jam_density) as usize; 
             let limit = if link.jam_density > 0.0 { max_veh } else { 9999 };
             
             let can_enter_storage = link.vehicles_on_link < limit;
             let can_enter_flow = self.current_time >= link.next_available_entry_time;
             
             if can_enter_storage && can_enter_flow {
                 link.entry_queue.pop_front();
                 
                 link.vehicles_on_link += 1;
                 let headway = if link.capacity > 0.0 { 1.0 / link.capacity } else { 1.0 };
                 link.next_available_entry_time = self.current_time + headway;
                 
                 // Move vehicle
                 self.vehicles[veh_id].state = VehicleState::Moving;
                 // We could update node_times[0] to actual entry time? 
                 // Usually NodeTimes[0] is Generation Time, NodeTimes[1] is Arrival at end of link 1.
                 // Let's keep [0] as Generation Time.
                 
                 let travel_time = link.length / link.speed_limit;
                 self.events.push(Event {
                     time: self.current_time + travel_time,
                     event_type: EventType::VehicleArrival,
                     link_id: link_id,
                     veh_id: veh_id,
                 });
             } else {
                 if !can_enter_flow && link.next_available_entry_time > self.current_time {
                     // Schedule WakeUp (Deduplicated)
                     if link.last_scheduled_ready_time != Some(link.next_available_entry_time) {
                         self.events.push(Event {
                             time: link.next_available_entry_time,
                             event_type: EventType::LinkReady,
                             link_id: link_id,
                             veh_id: 0,
                         });
                         link.last_scheduled_ready_time = Some(link.next_available_entry_time);
                     }
                 }
                 break; // Blocked
             }
        }
    }

    fn handle_vehicle_arrival(&mut self, link_id: LinkID, veh_id: VehID) {
        if link_id >= self.links.len() { return; }
        let link = &mut self.links[link_id];
        link.waiting_queue.push_back(veh_id);
        
        let mut node_idx_opt = None;
        for node in &self.nodes {
             if node.incoming_links.contains(&link_id) {
                 node_idx_opt = Some(node.id);
                 break;
             }
        }
        if let Some(node_id) = node_idx_opt {
            self.process_node_transfer(node_id);
        } else {
            self.process_exit(link_id);
        }
    }
    
    fn handle_link_exit(&mut self, link_id: LinkID) {
        if link_id >= self.links.len() { return; }
        
        {
            let link = &mut self.links[link_id];
            if link.vehicles_on_link > 0 {
                link.vehicles_on_link -= 1;
            }
        } // End borrow of link
        
        // Space freed on `link_id`.
        // 1. Check if vehicles want to ENTER this link (from Source)
        self.process_entry_queue(link_id);
        
        // 2. Check if vehicles want to ENTER this link (from Upstream Nodes)
        // Identify upstream nodes
        let mut up_node_opt = None;
        for node in &self.nodes {
            if node.outgoing_links.contains(&link_id) {
                up_node_opt = Some(node.id);
                break;
            }
        }
        if let Some(node_id) = up_node_opt {
            self.process_node_transfer(node_id);
        }
    }
    
    fn handle_link_ready(&mut self, link_id: LinkID) {
        // Capacity available on link_id. Check Source queue.
        self.process_entry_queue(link_id);
        
        // Check Upstream transfers
        let mut up_node_opt = None;
        for node in &self.nodes {
            if node.outgoing_links.contains(&link_id) {
                up_node_opt = Some(node.id);
                break;
            }
        }
        if let Some(node_id) = up_node_opt {
            self.process_node_transfer(node_id);
        }
    }
    
    fn process_exit(&mut self, link_id: LinkID) {
        let link = &mut self.links[link_id];
        while let Some(veh_id) = link.waiting_queue.pop_front() {
            if link.vehicles_on_link > 0 {
                 link.vehicles_on_link -= 1;
            }
            self.vehicles[veh_id].state = VehicleState::Exited;
            self.vehicles[veh_id].node_times.push(self.current_time);

            self.events.push(Event {
                time: self.current_time, 
                event_type: EventType::LinkExit,
                link_id: link_id,
                veh_id: veh_id, 
            });
        }
    }

    fn process_node_transfer(&mut self, node_id: NodeID) {
        if node_id >= self.nodes.len() { return; }
        let incoming_links = self.nodes[node_id].incoming_links.clone();
        
        for in_link_idx in incoming_links {
            if in_link_idx >= self.links.len() { continue; }
            
            let num_lanes = self.links[in_link_idx].num_lanes as usize;
            let look_ahead = if num_lanes > 0 { num_lanes } else { 1 };
            let queue_len = self.links[in_link_idx].waiting_queue.len();
            let limit = std::cmp::min(queue_len, look_ahead);
            
            let mut vehicle_to_move_idx = None;
            
            for i in 0..limit {
                let veh_id = self.links[in_link_idx].waiting_queue[i];
                if veh_id >= self.vehicles.len() { continue; }
                
                let next_link_id_opt = {
                    let v = &self.vehicles[veh_id];
                    if v.current_link_idx + 1 < v.path.len() {
                         Some(v.path[v.current_link_idx + 1])
                    } else {
                        None
                    }
                };
                
                if let Some(next_link_idx) = next_link_id_opt {
                     if next_link_idx >= self.links.len() { continue; }
                     
                     let can_enter_storage = {
                         let l = &self.links[next_link_idx];
                         let max_veh = (l.length * l.jam_density) as usize; 
                         let limit = if l.jam_density > 0.0 { max_veh } else { 9999 };
                         l.vehicles_on_link < limit
                     };
                     
                     let next_avail_time = self.links[next_link_idx].next_available_entry_time;
                     let can_enter_flow = self.current_time >= next_avail_time;
                     
                     if can_enter_storage && can_enter_flow {
                         vehicle_to_move_idx = Some((i, next_link_idx));
                         break; // Found one!
                     } else if can_enter_storage && !can_enter_flow {
                         if next_avail_time > self.current_time {
                             let l_next = &mut self.links[next_link_idx];
                             if l_next.last_scheduled_ready_time != Some(next_avail_time) {
                                 self.events.push(Event {
                                     time: next_avail_time,
                                     event_type: EventType::LinkReady,
                                     link_id: next_link_idx,
                                     veh_id: 0, 
                                 });
                                 l_next.last_scheduled_ready_time = Some(next_avail_time);
                             }
                         }
                     }
                } else {
                    // Destination reached
                    vehicle_to_move_idx = Some((i, usize::MAX)); // Marker for exit
                    break;
                }
            }
            
            if let Some((idx, next_link_idx)) = vehicle_to_move_idx {
                let veh_id = self.links[in_link_idx].waiting_queue.remove(idx).unwrap();
                
                if next_link_idx == usize::MAX {
                    // Exit
                    {
                        let v = &mut self.vehicles[veh_id];
                        v.state = VehicleState::Exited;
                        v.node_times.push(self.current_time);
                    }
                    self.events.push(Event {
                        time: self.current_time,
                        event_type: EventType::LinkExit,
                        link_id: in_link_idx,
                        veh_id: veh_id,
                    });
                } else {
                    // Transfer
                    let l_next = &mut self.links[next_link_idx];
                    l_next.vehicles_on_link += 1;
                    let headway = if l_next.capacity > 0.0 { 1.0 / l_next.capacity } else { 1.0 };
                    l_next.next_available_entry_time = self.current_time + headway;
                    
                    {
                        let v = &mut self.vehicles[veh_id];
                        v.current_link_idx += 1;
                        v.state = VehicleState::Moving;
                        v.node_times.push(self.current_time);
                    }
                    
                    let l_next_imm = &self.links[next_link_idx];
                    let travel_time = l_next_imm.length / l_next_imm.speed_limit;
                    
                    self.events.push(Event {
                        time: self.current_time + travel_time,
                        event_type: EventType::VehicleArrival,
                        link_id: next_link_idx,
                        veh_id: veh_id,
                    });
                    
                    self.events.push(Event {
                        time: self.current_time,
                        event_type: EventType::LinkExit,
                        link_id: in_link_idx,
                        veh_id: veh_id,
                    });
                }
            }
        }
    }
}

#[pymodule]
fn stream_rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Simulation>()?;
    Ok(())
}

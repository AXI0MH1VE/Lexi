//! Mamba-SSM State Management for LEX-7 Architecture
//! 
//! This module provides deterministic state-space model management
//! following the Mamba-SSM architecture for persistent node state.

use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use std::collections::HashMap;
use uuid::Uuid;

/// Persistent state vector (h_t) for Mamba-SSM
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StateVector {
    pub node_id: Uuid,
    pub timestamp: DateTime<Utc>,
    pub state_data: Vec<f64>,
    pub hidden_state: Vec<f64>,
    pub control_input: Vec<f64>,
    pub state_id: Uuid,
}

/// Deterministic transition matrix A (LxL)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TransitionMatrix {
    pub matrix: Vec<Vec<f64>>,
    pub size: usize,
}

/// Control input matrix B (LxM)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ControlMatrix {
    pub matrix: Vec<Vec<f64>>,
    pub input_size: usize,
    pub state_size: usize,
}

/// Deterministic state management for each node
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NodeState {
    pub node_type: String,
    pub current_state: StateVector,
    pub transition_matrix: TransitionMatrix,
    pub control_matrix: ControlMatrix,
    pub last_update: DateTime<Utc>,
    pub convergence_threshold: f64,
    pub temperature: f64, // Always 0.0 for deterministic behavior
}

/// State persistence and retrieval
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StateLedger {
    pub states: HashMap<Uuid, NodeState>,
    pub state_history: Vec<StateVector>,
    pub immutable_ledger: Vec<StateVector>, // Ledger locked states
}

/// Mamba-SSM State Manager
pub struct StateManager {
    pub ledger: StateLedger,
    pub deterministic_mode: bool,
}

impl StateManager {
    /// Initialize new state manager
    pub fn new() -> Self {
        Self {
            ledger: StateLedger {
                states: HashMap::new(),
                state_history: Vec::new(),
                immutable_ledger: Vec::new(),
            },
            deterministic_mode: true,
        }
    }

    /// Register a new node with its state-space model
    pub fn register_node(&mut self, node_type: String, state_size: usize, input_size: usize) -> Result<Uuid, String> {
        let node_id = Uuid::new_v4();
        
        // Create deterministic transition matrix (identity + small perturbations for realistic behavior)
        let transition_matrix = self.create_deterministic_transition_matrix(state_size);
        
        // Create control matrix
        let control_matrix = self.create_control_matrix(state_size, input_size);
        
        // Initialize state vector
        let initial_state = StateVector {
            node_id,
            timestamp: Utc::now(),
            state_data: vec![0.0; state_size],
            hidden_state: vec![0.0; state_size],
            control_input: vec![0.0; input_size],
            state_id: Uuid::new_v4(),
        };
        
        let node_state = NodeState {
            node_type,
            current_state: initial_state,
            transition_matrix,
            control_matrix,
            last_update: Utc::now(),
            convergence_threshold: 1e-6,
            temperature: 0.0, // Zero entropy
        };
        
        self.ledger.states.insert(node_id, node_state);
        
        Ok(node_id)
    }

    /// Update node state using Mamba-SSM equations
    /// h_t = A * h_(t-1) + B * u_t
    pub fn update_state(&mut self, node_id: Uuid, control_input: Vec<f64>) -> Result<&StateVector, String> {
        if let Some(node_state) = self.ledger.states.get_mut(&node_id) {
            let prev_state = node_state.current_state.clone();
            
            // Deterministic state transition: h_t = A * h_(t-1) + B * u_t
            let new_state_data = self.compute_next_state(&prev_state, &control_input, node_state);
            
            // Update state vector
            let new_state = StateVector {
                node_id,
                timestamp: Utc::now(),
                state_data: new_state_data,
                hidden_state: prev_state.hidden_state.clone(),
                control_input,
                state_id: Uuid::new_v4(),
            };
            
            node_state.current_state = new_state.clone();
            node_state.last_update = Utc::now();
            
            // Add to history
            self.ledger.state_history.push(new_state.clone());
            
            // Check convergence
            if self.check_convergence(&prev_state, &new_state, node_state.convergence_threshold) {
                // Add to immutable ledger when converged
                self.ledger.immutable_ledger.push(new_state);
            }
            
            Ok(&node_state.current_state)
        } else {
            Err("Node not found".to_string())
        }
    }

    /// Get current node state
    pub fn get_node_state(&self, node_id: Uuid) -> Result<&NodeState, String> {
        self.ledger.states.get(&node_id)
            .ok_or_else(|| "Node state not found".to_string())
    }

    /// Create deterministic transition matrix
    fn create_deterministic_transition_matrix(&self, size: usize) -> TransitionMatrix {
        let mut matrix = vec![vec![0.0; size]; size];
        
        // Create slightly stable identity matrix with deterministic perturbations
        for i in 0..size {
            matrix[i][i] = 0.98 + (i as f64 * 0.0001); // Slightly less than 1 for stability
            if i + 1 < size {
                matrix[i][i + 1] = 0.01 * (i as f64 + 1.0); // Controlled coupling
            }
        }
        
        TransitionMatrix { matrix, size }
    }

    /// Create control input matrix
    fn create_control_matrix(&self, state_size: usize, input_size: usize) -> ControlMatrix {
        let mut matrix = vec![vec![0.0; input_size]; state_size];
        
        // Deterministic control matrix with controlled influence
        for i in 0..state_size.min(input_size) {
            matrix[i][i] = 0.1; // Each input affects its corresponding state
        }
        
        // Cross-coupling for more realistic behavior
        for i in 0..state_size {
            for j in 0..input_size {
                if i != j {
                    matrix[i][j] = 0.02 * ((i + j) as f64 / (state_size + input_size) as f64);
                }
            }
        }
        
        ControlMatrix { matrix, input_size, state_size }
    }

    /// Compute next state using deterministic Mamba-SSM equations
    fn compute_next_state(&self, current_state: &StateVector, control_input: &[f64], node_state: &NodeState) -> Vec<f64> {
        let state_size = current_state.state_data.len();
        let mut next_state = vec![0.0; state_size];
        
        // h_t = A * h_(t-1) + B * u_t
        for i in 0..state_size {
            // A * h_(t-1) term
            for j in 0..state_size {
                next_state[i] += node_state.transition_matrix.matrix[i][j] * current_state.state_data[j];
            }
            
            // B * u_t term
            for j in 0..control_input.len() {
                if i < node_state.control_matrix.matrix.len() && j < node_state.control_matrix.matrix[i].len() {
                    next_state[i] += node_state.control_matrix.matrix[i][j] * control_input[j];
                }
            }
        }
        
        // Apply zero entropy constraint (temperature = 0.0)
        for value in &mut next_state {
            *value = value.clamp(-10.0, 10.0); // Bounded for stability
        }
        
        next_state
    }

    /// Check state convergence
    fn check_convergence(&self, prev_state: &StateVector, new_state: &StateVector, threshold: f64) -> bool {
        let mut max_diff = 0.0;
        
        for (i, (&prev, &new)) in prev_state.state_data.iter().zip(&new_state.state_data).enumerate() {
            let diff = (prev - new).abs();
            if diff > max_diff {
                max_diff = diff;
            }
        }
        
        max_diff < threshold
    }

    /// Get immutable state ledger (converged states)
    pub fn get_immutable_ledger(&self) -> &[StateVector] {
        &self.ledger.immutable_ledger
    }

    /// Create snapshot for backup
    pub fn create_snapshot(&self) -> Result<String, serde_json::Error> {
        serde_json::to_string_pretty(&self.ledger)
    }

    /// Load snapshot from backup
    pub fn load_snapshot(&mut self, snapshot: &str) -> Result<(), serde_json::Error> {
        let ledger: StateLedger = serde_json::from_str(snapshot)?;
        self.ledger = ledger;
        Ok(())
    }
}

impl Default for StateManager {
    fn default() -> Self {
        Self::new()
    }
}

/// Utility functions for state management
pub mod utils {
    use super::*;
    
    /// Generate deterministic state initialization values
    pub fn generate_deterministic_init(size: usize, node_type: &str) -> Vec<f64> {
        match node_type {
            "LEX-VIT" => {
                // Vitality states: bioload, hrv, stress, sleep_quality
                vec![72.0, 65.0, 25.0, 85.0][0..size.min(4)].to_vec()
            },
            "LEX-WTH" => {
                // Financial states: runway, balance, burn_rate, expenses
                vec![6.0, 45000.0, -2500.0, 3200.0][0..size.min(4)].to_vec()
            },
            "LEX-MON" => {
                // Coordination states: load, health, queue_size, active_directives
                vec![15.0, 95.0, 0.0, 0.0][0..size.min(4)].to_vec()
            },
            _ => vec![0.0; size],
        }
    }
    
    /// Calculate state similarity for decision making
    pub fn calculate_state_similarity(state1: &[f64], state2: &[f64]) -> f64 {
        let min_len = state1.len().min(state2.len());
        if min_len == 0 {
            return 1.0;
        }
        
        let mut differences = 0.0;
        for i in 0..min_len {
            let diff = (state1[i] - state2[i]).abs();
            differences += diff * diff;
        }
        
        // Convert to similarity score (0.0 to 1.0)
        let normalized_diff = (differences / min_len as f64).sqrt();
        (1.0 / (1.0 + normalized_diff)).clamp(0.0, 1.0)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_state_manager_creation() {
        let mut manager = StateManager::new();
        let node_id = manager.register_node("LEX-VIT".to_string(), 4, 2).unwrap();
        
        assert_eq!(manager.ledger.states.len(), 1);
        assert!(manager.ledger.states.contains_key(&node_id));
    }

    #[test]
    fn test_state_update() {
        let mut manager = StateManager::new();
        let node_id = manager.register_node("LEX-VIT".to_string(), 4, 2).unwrap();
        
        let control_input = vec![1.0, -0.5];
        let result = manager.update_state(node_id, control_input.clone());
        
        assert!(result.is_ok());
        let new_state = result.unwrap();
        assert_eq!(new_state.control_input, control_input);
    }

    #[test]
    fn test_deterministic_behavior() {
        let mut manager1 = StateManager::new();
        let mut manager2 = StateManager::new();
        
        let node_id1 = manager1.register_node("LEX-VIT".to_string(), 2, 1).unwrap();
        let node_id2 = manager2.register_node("LEX-VIT".to_string(), 2, 1).unwrap();
        
        let control_input = vec![0.1];
        
        // Update both managers with same input
        manager1.update_state(node_id1, control_input.clone());
        let _ = manager2.update_state(node_id2, control_input.clone());
        
        // States should be identical (deterministic)
        let state1 = &manager1.ledger.states[&node_id1].current_state.state_data;
        let state2 = &manager2.ledger.states[&node_id2].current_state.state_data;
        
        for (s1, s2) in state1.iter().zip(state2.iter()) {
            assert!((s1 - s2).abs() < 1e-10);
        }
    }
}

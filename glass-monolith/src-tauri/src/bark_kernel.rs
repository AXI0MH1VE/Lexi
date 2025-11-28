use serde::{Deserialize, Serialize};
use tauri::State;

use crate::lex_bridge::{run_mamba, BridgeResult};

// Directive schema (Glass Box, no free-form chat)
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct Directive {
    pub id: String,
    pub command: String,
    pub target_nodes: Vec<String>,
    pub signature: String, // SRP/Ed25519 signature of the payload
}

#[derive(Default)]
pub struct KernelConfig {
    pub enforce_zero_entropy: bool,
}

// Entry point invoked from the UI command vector
#[tauri::command]
pub fn execute_vector(command: String, state: State<KernelConfig>) -> String {
    let directive = parse_intent(command);

    if state.enforce_zero_entropy && !verify_signature(&directive.signature) {
        return "ERROR: UNVERIFIED DIRECTIVE. ENTROPY DETECTED.".to_string();
    }

    match run_mamba(&directive) {
        Ok(BridgeResult { state_delta, proof_hash }) => format!(
            "STATE UPDATED: {state_delta}. PROOF: {proof_hash}"
        ),
        Err(e) => format!("ERROR: {}", e),
    }
}

fn parse_intent(command: String) -> Directive {
    // Minimal router stub; replace with a real parser/validator.
    Directive {
        id: "directive-local".into(),
        command: command.clone(),
        target_nodes: vec!["LEX-MON".into(), "LEX-VIT".into(), "LEX-WTH".into()],
        signature: "srp://local/mock-signature".into(),
    }
}

fn verify_signature(signature: &str) -> bool {
    // Replace with real Ed25519 verification + nonce replay protection.
    !signature.is_empty() && signature.contains("srp://")
}

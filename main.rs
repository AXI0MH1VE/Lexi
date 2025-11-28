use bark_protocol::{BarkDirective, BarkResponse, ResponseStatus, TargetNode};
use serde_json::json;
use std::io;

/// LEX-VIT: The vitality and bio-state monitoring node.
fn main() {
    println!("[LEX-VIT] Node online. Awaiting directives...");

    // Simulate listening for a directive from LEX-MON.
    let mut buffer = String::new();
    if io::stdin().read_line(&mut buffer).is_ok() {
        if let Ok(directive) = serde_json::from_str::<BarkDirective>(&buffer) {
            println!("[LEX-VIT] Received directive: {:?}", directive.kind);
            let response = handle_directive(directive);
            println!("[LEX-VIT] Sending response: {}", serde_json::to_string(&response).unwrap());
        }
    }
}

fn handle_directive(directive: BarkDirective) -> BarkResponse {
    // Simulate analyzing bioload.
    let bioload = 72.0; // Mock value
    let hrv = 65; // Mock value

    let response_payload = json!({
        "bioload_percentage": bioload,
        "hrv_morning": hrv,
        "cognitive_load_estimate": "7/10",
        "status": "Acceptable"
    });

    BarkResponse {
        request_id: directive.request_id,
        source_node: TargetNode::LexVit,
        status: ResponseStatus::Success,
        payload: response_payload,
        signature: "[signed_by_lex_vit]".to_string(),
    }
}

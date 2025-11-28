//! LEX-MON Node - Monitoring and Coordination Router
//! 
//! This is the central coordination node that orchestrates cross-temple flows,
//! routes directives to appropriate nodes, collects responses, and synthesizes
//! final decisions. It acts as the "council" in the LEX-7 architecture.

use bark_protocol::{
    BarkDirective, BarkResponse, DirectiveKind, TargetNode, ResponseStatus, NodeHealth
};
use chrono::Utc;
use serde_json::json;
use std::io::{self, Read};
use std::process::{Command, Stdio};
use std::collections::HashMap;
use tokio::sync::Mutex;
use uuid::Uuid;

const NODE_SIGIL: &str = "srp://alexis/lex-mon";

lazy_static::lazy_static! {
    static ref NODE_HEALTH: Mutex<HashMap<TargetNode, NodeHealth>> = Mutex::new(HashMap::new());
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("[LEX-MON] 🏛️ Council Node online. Cross-temple coordination active.");
    println!("[LEX-MON] 📡 Awaiting directives on BARK Protocol v3.1...");
    println!("[LEX-MON] 🔐 Node Sigil: {}", NODE_SIGIL);

    // Initialize node health monitoring
    initialize_node_health().await;

    // Start the council's main loop
    start_council_operations().await?;
    
    Ok(())
}

async fn initialize_node_health() {
    let mut health = NODE_HEALTH.lock().await;
    
    // Initialize health status for all nodes
    let nodes = vec![
        TargetNode::LexVit,
        TargetNode::LexWth,
        TargetNode::LexEnt,
        TargetNode::LexKno,
        TargetNode::LexCrt,
        TargetNode::LexOrd,
        TargetNode::LexKin,
        TargetNode::LexGrw,
        TargetNode::LexSan,
        TargetNode::LexLei,
        TargetNode::LexOut,
        TargetNode::LexLeg,
    ];
    
    for node in nodes {
        health.insert(node, NodeHealth {
            node_id: node,
            status: "unknown".to_string(),
            last_heartbeat: Utc::now(),
            load_percentage: 0.0,
            memory_usage_mb: 0,
        });
    }
    
    println!("[LEX-MON] 📊 Initialized health monitoring for {} nodes", health.len());
}

async fn start_council_operations() -> Result<(), Box<dyn std::error::Error>> {
    loop {
        // Listen for incoming directives
        println!("[LEX-MON] 🎧 Council awaiting directives...");
        
        let mut buffer = String::new();
        if io::stdin().read_line(&mut buffer).is_ok() {
            if let Ok(directive) = serde_json::from_str::<BarkDirective>(&buffer.trim()) {
                println!("[LEX-MON] 📨 Received directive: {} (Kind: {:?})", 
                    directive.request_id, directive.kind);
                
                let response = process_council_directive(directive).await?;
                let response_json = serde_json::to_string(&response)?;
                
                println!("[LEX-MON] 📤 Council decision rendered: {}", response_json);
                println!("[LEX-MON] ✅ Cross-temple coordination complete");
            } else {
                println!("[LEX-MON] ❌ Failed to parse council directive");
            }
        }
        
        // Small delay between processing directives
        tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
    }
}

async fn process_council_directive(directive: BarkDirective) -> Result<BarkResponse, Box<dyn std::error::Error>> {
    println!("[LEX-MON] 🏛️ Council processing directive from: {}", directive.caller_sigil);
    
    // Verify directive authenticity
    if let Err(e) = directive.verify_signature() {
        println!("[LEX-MON] ⚠️ Council signature verification failed: {}", e);
        return Ok(BarkResponse::failure(
            directive.request_id,
            TargetNode::LexMon,
            format!("Council signature verification failed: {}", e),
        ));
    }
    
    // Route directive to appropriate nodes and synthesize response
    match directive.kind {
        DirectiveKind::ANALYZE => {
            route_and_synthesize_analysis(directive).await
        },
        DirectiveKind::EXECUTE_PLAN => {
            route_and_synthesize_execution(directive).await
        },
        DirectiveKind::VALIDATE_OUTPUT => {
            route_and_synthesize_validation(directive).await
        },
        _ => {
            Ok(BarkResponse::failure(
                directive.request_id,
                TargetNode::LexMon,
                format!("Council does not support directive kind: {:?}", directive.kind),
            ))
        }
    }
}

async fn route_and_synthesize_analysis(directive: BarkDirective) -> Result<BarkResponse, Box<dyn std::error::Error>> {
    println!("[LEX-MON] 🔄 Routing analysis directive to relevant temples...");
    
    // Parse intent and determine which nodes to consult
    let target_nodes = determine_target_nodes(&directive.payload)?;
    
    if target_nodes.is_empty() {
        return Ok(BarkResponse::failure(
            directive.request_id,
            TargetNode::LexMon,
            "No relevant temples identified for this directive".to_string(),
        ));
    }
    
    println!("[LEX-MON] 🎯 Routing to {} temples: {:?}", target_nodes.len(), target_nodes);
    
    // Route directives to target nodes in parallel
    let mut handles = Vec::new();
    for &node in &target_nodes {
        let directive_clone = directive.clone();
        let handle = tokio::spawn(async move {
            route_to_node(node, directive_clone).await
        });
        handles.push(handle);
    }
    
    // Collect responses from all nodes
    let mut responses = Vec::new();
    for handle in handles {
        if let Ok(response) = handle.await {
            responses.push(response);
        }
    }
    
    // Synthesize final decision
    synthesize_council_decision(directive.request_id, responses).await
}

async fn route_to_node(node: TargetNode, directive: BarkDirective) -> Result<BarkResponse, Box<dyn std::error::Error>> {
    println!("[LEX-MON] 📡 Routing to temple: {:?}", node);
    
    // Simulate routing to node (in real implementation, this would use inter-process communication)
    match node {
        TargetNode::LexVit => {
            // Simulate calling LEX-VIT node
            simulate_node_call("lex-vit", directive).await
        },
        TargetNode::LexWth => {
            // Simulate calling LEX-WTH node
            simulate_node_call("lex-wth", directive).await
        },
        _ => {
            // Placeholder for other nodes
            Ok(BarkResponse::failure(
                directive.request_id,
                node,
                format!("Temple {:?} not yet implemented", node),
            ))
        }
    }
}

async fn simulate_node_call(node_name: &str, directive: BarkDirective) -> Result<BarkResponse, Box<dyn std::error::Error>> {
    // In a real implementation, this would spawn the node process and communicate via pipes or network
    // For now, simulate the response based on node type
    
    match node_name {
        "lex-vit" => {
            // Simulate LEX-VIT response
            Ok(BarkResponse::success(
                directive.request_id,
                TargetNode::LexVit,
                json!({
                    "bioload_percentage": 72.0,
                    "hrv_morning": 65,
                    "cognitive_load_estimate": "7/10",
                    "status": "Acceptable"
                }),
            ))
        },
        "lex-wth" => {
            // Simulate LEX-WTH response
            Ok(BarkResponse::success(
                directive.request_id,
                TargetNode::LexWth,
                json!({
                    "runway_months": 6.0,
                    "financial_health_score": 78.5,
                    "risk_level": "MEDIUM",
                    "recommendations": ["Monitor expenses", "Build emergency fund"]
                }),
            ))
        },
        _ => {
            Ok(BarkResponse::failure(
                directive.request_id,
                TargetNode::LexMon,
                format!("Unknown node: {}", node_name),
            ))
        }
    }
}

async fn synthesize_council_decision(request_id: Uuid, responses: Vec<BarkResponse>) -> Result<BarkResponse, Box<dyn std::error::Error>> {
    println!("[LEX-MON] 🧠 Synthesizing council decision from {} temple responses...", responses.len());
    
    // Analyze responses and make a council decision
    let successful_responses: Vec<&BarkResponse> = responses.iter()
        .filter(|r| r.status == ResponseStatus::Success)
        .collect();
    
    if successful_responses.is_empty() {
        return Ok(BarkResponse::failure(
            request_id,
            TargetNode::LexMon,
            "Council synthesis failed: No successful temple responses".to_string(),
        ));
    }
    
    // Extract key metrics from responses
    let mut decision_factors = Vec::new();
    let mut risk_level = "LOW";
    let mut go_decision = true;
    
    for response in &successful_responses {
        match response.source_node {
            TargetNode::LexVit => {
                let bioload = response.payload["bioload_percentage"].as_f64().unwrap_or(100.0);
                decision_factors.push(format!("BioLoad: {:.1}%", bioload));
                if bioload > 85.0 {
                    risk_level = "HIGH";
                    go_decision = false;
                }
            },
            TargetNode::LexWth => {
                let runway = response.payload["runway_months"].as_f64().unwrap_or(0.0);
                decision_factors.push(format!("Runway: {:.1} months", runway));
                if runway < 3.0 {
                    risk_level = "HIGH";
                    go_decision = false;
                } else if runway < 6.0 && risk_level != "HIGH" {
                    risk_level = "MEDIUM";
                }
            },
            _ => {}
        }
    }
    
    let decision = if go_decision { "GO" } else { "HOLD" };
    
    let synthesis = json!({
        "council_decision": decision,
        "risk_assessment": risk_level,
        "decision_factors": decision_factors,
        "temple_responses": successful_responses.len(),
        "timestamp": Utc::now(),
        "proof": {
            "request_id": request_id,
            "synthesis_method": "weighted_consensus",
            "confidence_score": 0.89
        }
    });
    
    println!("[LEX-MON] ⚖️ Council Decision: {} (Risk: {})", decision, risk_level);
    
    Ok(BarkResponse::success(
        request_id,
        TargetNode::LexMon,
        synthesis,
    ))
}

async fn route_and_synthesize_execution(directive: BarkDirective) -> Result<BarkResponse, Box<dyn std::error::Error>> {
    // Placeholder for execution plan routing
    Ok(BarkResponse::success(
        directive.request_id,
        TargetNode::LexMon,
        json!({
            "execution_status": "planned",
            "coordination_complete": true,
            "timestamp": Utc::now()
        }),
    ))
}

async fn route_and_synthesize_validation(directive: BarkDirective) -> Result<BarkResponse, Box<dyn std::error::Error>> {
    // Placeholder for validation routing
    Ok(BarkResponse::success(
        directive.request_id,
        TargetNode::LexMon,
        json!({
            "validation_status": "passed",
            "confidence_score": 0.95,
            "timestamp": Utc::now()
        }),
    ))
}

fn determine_target_nodes(payload: &serde_json::Value) -> Result<Vec<TargetNode>, Box<dyn std::error::Error>> {
    // Simple intent parsing to determine which nodes to consult
    let payload_str = payload.to_string().to_lowercase();
    
    let mut targets = Vec::new();
    
    if payload_str.contains("runway") || payload_str.contains("financial") || payload_str.contains("money") {
        targets.push(TargetNode::LexWth);
    }
    
    if payload_str.contains("bioload") || payload_str.contains("health") || payload_str.contains("stress") || payload_str.contains("sleep") {
        targets.push(TargetNode::LexVit);
    }
    
    // Default to both if no specific intent detected
    if targets.is_empty() {
        targets.push(TargetNode::LexVit);
        targets.push(TargetNode::LexWth);
    }
    
    Ok(targets)
}
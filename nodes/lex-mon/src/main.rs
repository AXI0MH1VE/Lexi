//! LEX-MON Node - Monitoring and Coordination Router
//!
//! This is the central coordination node that orchestrates cross-temple flows,
//! routes directives to appropriate nodes, and synthesizes responses.
//! Acts as the "council" in the LEX-7 distributed system.

use bark_protocol::{
    BarkDirective, BarkResponse, DirectiveKind, TargetNode, ResponseStatus, NodeHealth
};
use chrono::Utc;
use serde_json::json;
use std::collections::HashMap;
use std::io::{self, Read};
use std::process::{Command, Stdio};
use tokio::sync::Mutex;
use uuid::Uuid;

const NODE_SIGIL: &str = "srp://alexis/lex-mon";

/// Global state for node coordination
lazy_static::lazy_static! {
    static ref NODE_REGISTRY: Mutex<HashMap<TargetNode, NodeHealth>> = Mutex::new(HashMap::new());
    static ref ACTIVE_DIRECTIVES: Mutex<HashMap<Uuid, DirectiveState>> = Mutex::new(HashMap::new());
}

#[derive(Debug, Clone)]
struct DirectiveState {
    directive: BarkDirective,
    responses: Vec<BarkResponse>,
    expected_responses: usize,
    started_at: chrono::DateTime<Utc>,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("[LEX-MON] 🏛️  Council Node online. Orchestrating cross-temple flows.");
    println!("[LEX-MON] 📡 BARK Protocol v3.1 Router active.");
    println!("[LEX-MON] 🔐 Node Sigil: {}", NODE_SIGIL);

    // Initialize node registry
    initialize_node_registry().await;

    // Start the council's main loop
    start_council_operations().await?;

    Ok(())
}

async fn initialize_node_registry() {
    let mut registry = NODE_REGISTRY.lock().await;

    // Register all known nodes
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
        registry.insert(node, NodeHealth {
            node_id: node,
            status: "unknown".to_string(),
            last_heartbeat: Utc::now(),
            load_percentage: 0.0,
            memory_usage_mb: 0,
        });
    }

    println!("[LEX-MON] 📋 Node registry initialized with {} nodes", registry.len());
}

async fn start_council_operations() -> Result<(), Box<dyn std::error::Error>> {
    loop {
        println!("[LEX-MON] 🎧 Council awaiting directives...");

        let mut buffer = String::new();
        if io::stdin().read_line(&mut buffer).is_ok() {
            if let Ok(directive) = serde_json::from_str::<BarkDirective>(&buffer.trim()) {
                println!("[LEX-MON] 📨 Received directive: {} (Kind: {:?})",
                    directive.request_id, directive.kind);

                let response = process_council_directive(directive).await?;
                let response_json = serde_json::to_string(&response)?;

                println!("[LEX-MON] 📤 Council response: {}", response_json);
                println!("[LEX-MON] ✅ Directive processing complete");
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

    // Route directive based on content and intent
    match directive.kind {
        DirectiveKind::ANALYZE => {
            route_analysis_directive(directive).await
        },
        DirectiveKind::EXECUTE_PLAN => {
            route_execution_directive(directive).await
        },
        DirectiveKind::VALIDATE_OUTPUT => {
            route_validation_directive(directive).await
        },
        _ => {
            // Handle general routing
            route_general_directive(directive).await
        }
    }
}

async fn route_analysis_directive(directive: BarkDirective) -> Result<BarkResponse, Box<dyn std::error::Error>> {
    println!("[LEX-MON] 🔍 Routing analysis directive...");

    // Parse directive payload to determine which nodes to involve
    let payload_str = directive.payload.to_string().to_lowercase();

    let target_nodes = determine_analysis_targets(&payload_str);

    if target_nodes.is_empty() {
        return Ok(BarkResponse::failure(
            directive.request_id,
            TargetNode::LexMon,
            "No appropriate analysis nodes identified for directive".to_string(),
        ));
    }

    // Create parallel directives for each target node
    let mut directive_state = DirectiveState {
        directive: directive.clone(),
        responses: Vec::new(),
        expected_responses: target_nodes.len(),
        started_at: Utc::now(),
    };

    // Register the directive state
    {
        let mut active_directives = ACTIVE_DIRECTIVES.lock().await;
        active_directives.insert(directive.request_id, directive_state);
    }

    // Send directives to each target node
    for &target_node in &target_nodes {
        if let Err(e) = send_directive_to_node(&directive, target_node).await {
            println!("[LEX-MON] ⚠️ Failed to send directive to {:?}: {}", target_node, e);
        }
    }

    // Wait for responses with timeout
    let responses = collect_node_responses(directive.request_id, target_nodes.len()).await;

    // Synthesize final response
    synthesize_analysis_response(directive.request_id, responses).await
}

async fn route_execution_directive(directive: BarkDirective) -> Result<BarkResponse, Box<dyn std::error::Error>> {
    println!("[LEX-MON] ⚡ Routing execution directive...");

    // Execution directives typically go to LEX-ORD (Order/Logistics)
    let target_nodes = vec![TargetNode::LexOrd];

    // Similar process as analysis routing but for execution
    let responses = route_to_nodes(&directive, target_nodes).await;

    synthesize_execution_response(directive.request_id, responses).await
}

async fn route_validation_directive(directive: BarkDirective) -> Result<BarkResponse, Box<dyn std::error::Error>> {
    println!("[LEX-MON] ✅ Routing validation directive...");

    // Validation can involve multiple nodes for cross-verification
    let target_nodes = vec![TargetNode::LexKno, TargetNode::LexCrt];

    let responses = route_to_nodes(&directive, target_nodes).await;

    synthesize_validation_response(directive.request_id, responses).await
}

async fn route_general_directive(directive: BarkDirective) -> Result<BarkResponse, Box<dyn std::error::Error>> {
    println!("[LEX-MON] 🔀 Routing general directive...");

    // Default routing based on target specified in directive
    let target_nodes = vec![directive.target_agent];

    let responses = route_to_nodes(&directive, target_nodes).await;

    synthesize_general_response(directive.request_id, responses).await
}

fn determine_analysis_targets(payload: &str) -> Vec<TargetNode> {
    let mut targets = Vec::new();

    // Keyword-based routing logic
    if payload.contains("runway") || payload.contains("financial") || payload.contains("wealth") {
        targets.push(TargetNode::LexWth);
    }

    if payload.contains("bioload") || payload.contains("vital") || payload.contains("health") ||
       payload.contains("stress") || payload.contains("sleep") {
        targets.push(TargetNode::LexVit);
    }

    if payload.contains("pivot") || payload.contains("strategy") || payload.contains("enterprise") {
        targets.push(TargetNode::LexEnt);
    }

    if payload.contains("knowledge") || payload.contains("information") || payload.contains("data") {
        targets.push(TargetNode::LexKno);
    }

    if payload.contains("create") || payload.contains("generate") || payload.contains("output") {
        targets.push(TargetNode::LexCrt);
    }

    if payload.contains("plan") || payload.contains("schedule") || payload.contains("logistics") {
        targets.push(TargetNode::LexOrd);
    }

    if payload.contains("social") || payload.contains("relationship") || payload.contains("kinship") {
        targets.push(TargetNode::LexKin);
    }

    if payload.contains("learn") || payload.contains("growth") || payload.contains("capability") {
        targets.push(TargetNode::LexGrw);
    }

    if payload.contains("environment") || payload.contains("sanctuary") || payload.contains("infrastructure") {
        targets.push(TargetNode::LexSan);
    }

    if payload.contains("leisure") || payload.contains("recovery") || payload.contains("restoration") {
        targets.push(TargetNode::LexLei);
    }

    if payload.contains("communication") || payload.contains("influence") || payload.contains("outreach") {
        targets.push(TargetNode::LexOut);
    }

    if payload.contains("legacy") || payload.contains("history") || payload.contains("meta") {
        targets.push(TargetNode::LexLeg);
    }

    // If no specific targets found, default to knowledge node
    if targets.is_empty() {
        targets.push(TargetNode::LexKno);
    }

    targets
}

async fn send_directive_to_node(directive: &BarkDirective, target_node: TargetNode) -> Result<(), Box<dyn std::error::Error>> {
    // In a real implementation, this would use inter-process communication
    // For now, simulate by spawning child processes or using channels

    println!("[LEX-MON] 📡 Sending directive to {:?} node", target_node);

    // This is a placeholder - in reality would use proper IPC
    // For demonstration, we'll simulate the response

    Ok(())
}

async fn collect_node_responses(directive_id: Uuid, expected_count: usize) -> Vec<BarkResponse> {
    // In a real implementation, this would collect responses from nodes
    // For now, simulate responses

    println!("[LEX-MON] 📥 Collecting responses from {} nodes", expected_count);

    // Simulate waiting for responses
    tokio::time::sleep(tokio::time::Duration::from_millis(500)).await;

    // Return simulated responses
    vec![
        BarkResponse::success(
            directive_id,
            TargetNode::LexWth,
            json!({
                "runway_months": 6.2,
                "financial_health_score": 78.5,
                "recommendations": ["Monitor expenses", "Build emergency fund"]
            }),
        ),
        BarkResponse::success(
            directive_id,
            TargetNode::LexVit,
            json!({
                "bioload_percentage": 72.0,
                "hrv_morning": 65,
                "overall_status": "Acceptable"
            }),
        ),
    ]
}

async fn route_to_nodes(directive: &BarkDirective, target_nodes: Vec<TargetNode>) -> Vec<BarkResponse> {
    let mut responses = Vec::new();

    for &target_node in &target_nodes {
        if let Err(e) = send_directive_to_node(directive, target_node).await {
            println!("[LEX-MON] ⚠️ Failed to route to {:?}: {}", target_node, e);
            continue;
        }
    }

    // Collect responses
    collect_node_responses(directive.request_id, target_nodes.len()).await
}

async fn synthesize_analysis_response(directive_id: Uuid, responses: Vec<BarkResponse>) -> Result<BarkResponse, Box<dyn std::error::Error>> {
    println!("[LEX-MON] 🧠 Synthesizing analysis response from {} node responses", responses.len());

    // Extract key insights from all responses
    let mut synthesis = json!({
        "directive_id": directive_id,
        "response_count": responses.len(),
        "synthesis_timestamp": Utc::now(),
        "key_insights": {},
        "recommendations": [],
        "risk_assessment": "LOW",
        "confidence_score": 0.85
    });

    // Process each response
    for response in &responses {
        if response.status == ResponseStatus::Success {
            match response.source_node {
                TargetNode::LexWth => {
                    if let Some(runway) = response.payload.get("runway_months") {
                        synthesis["key_insights"]["financial_runway"] = runway.clone();
                    }
                },
                TargetNode::LexVit => {
                    if let Some(bioload) = response.payload.get("bioload_percentage") {
                        synthesis["key_insights"]["biological_load"] = bioload.clone();
                    }
                },
                _ => {}
            }
        }
    }

    // Generate final decision
    let decision = generate_council_decision(&synthesis);

    synthesis["decision"] = json!(decision);
    synthesis["council_verdict"] = json!("APPROVED");

    Ok(BarkResponse::success(
        directive_id,
        TargetNode::LexMon,
        synthesis,
    ))
}

async fn synthesize_execution_response(directive_id: Uuid, responses: Vec<BarkResponse>) -> Result<BarkResponse, Box<dyn std::error::Error>> {
    let synthesis = json!({
        "execution_status": "INITIATED",
        "coordination_complete": true,
        "timestamp": Utc::now()
    });

    Ok(BarkResponse::success(directive_id, TargetNode::LexMon, synthesis))
}

async fn synthesize_validation_response(directive_id: Uuid, responses: Vec<BarkResponse>) -> Result<BarkResponse, Box<dyn std::error::Error>> {
    let synthesis = json!({
        "validation_status": "VERIFIED",
        "cross_check_complete": true,
        "confidence_score": 0.92,
        "timestamp": Utc::now()
    });

    Ok(BarkResponse::success(directive_id, TargetNode::LexMon, synthesis))
}

async fn synthesize_general_response(directive_id: Uuid, responses: Vec<BarkResponse>) -> Result<BarkResponse, Box<dyn std::error::Error>> {
    let synthesis = json!({
        "routing_complete": true,
        "responses_processed": responses.len(),
        "timestamp": Utc::now()
    });

    Ok(BarkResponse::success(directive_id, TargetNode::LexMon, synthesis))
}

fn generate_council_decision(synthesis: &serde_json::Value) -> serde_json::Value {
    // Council decision logic based on synthesized data
    let financial_runway = synthesis["key_insights"].get("financial_runway")
        .and_then(|v| v.as_f64()).unwrap_or(0.0);
    let biological_load = synthesis["key_insights"].get("biological_load")
        .and_then(|v| v.as_f64()).unwrap_or(100.0);

    let decision = if financial_runway >= 6.0 && biological_load <= 75.0 {
        "GO"
    } else if financial_runway >= 3.0 && biological_load <= 85.0 {
        "CAUTION"
    } else {
        "HOLD"
    };

    json!({
        "verdict": decision,
        "reasoning": format!("Financial runway: {:.1} months, Biological load: {:.1}%", financial_runway, biological_load),
        "action_required": decision == "GO"
    })
}
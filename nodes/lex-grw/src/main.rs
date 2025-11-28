//! LEX-GRW Node - Growth and Learning Management
//!
//! This node handles learning and growth, capability development, and skill acquisition.
//! It responds to BARK Protocol directives for educational planning and skill development.

use bark_protocol::{
    BarkDirective, BarkResponse, DirectiveKind, TargetNode, ResponseStatus
};
use chrono::Utc;
use serde_json::json;
use std::io::{self, Read};
use uuid::Uuid;

const NODE_SIGIL: &str = "srp://alexis/lex-grw";

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("[LEX-GRW] 🌱 Node online. Growth and learning active.");
    println!("[LEX-GRW] 📡 Awaiting directives on BARK Protocol v3.1...");
    println!("[LEX-GRW] 🔐 Node Sigil: {}", NODE_SIGIL);

    // Start the node's main loop
    start_growth_management().await?;

    Ok(())
}

async fn start_growth_management() -> Result<(), Box<dyn std::error::Error>> {
    loop {
        // Listen for incoming directives
        println!("[LEX-GRW] 🎧 Listening for directives...");

        let mut buffer = String::new();
        if io::stdin().read_line(&mut buffer).is_ok() {
            if let Ok(trimmed) = serde_json::from_str::<BarkDirective>(&buffer.trim()) {
                println!("[LEX-GRW] 📨 Received directive: {} (Kind: {:?})",
                    trimmed.request_id, trimmed.kind);

                let response = process_directive(trimmed).await?;
                let response_json = serde_json::to_string(&response)?;

                println!("[LEX-GRW] 📤 Sending response: {}", response_json);
                println!("[LEX-GRW] ✅ Response sent successfully");
            } else {
                println!("[LEX-GRW] ❌ Failed to parse directive");
            }
        }

        // Small delay between processing directives
        tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
    }
}

async fn process_directive(directive: BarkDirective) -> Result<BarkResponse, Box<dyn std::error::Error>> {
    println!("[LEX-GRW] 🔍 Processing directive from: {}", directive.caller_sigil);

    // Verify directive authenticity (placeholder implementation)
    if let Err(e) = directive.verify_signature() {
        println!("[LEX-GRW] ⚠️ Signature verification failed: {}", e);
        return Ok(BarkResponse::failure(
            directive.request_id,
            TargetNode::LexGrw,
            format!("Signature verification failed: {}", e),
        ));
    }

    // Process based on directive kind
    match directive.kind {
        DirectiveKind::ANALYZE => {
            analyze_learning_needs(directive).await
        },
        DirectiveKind::GENERATE => {
            generate_learning_plan(directive).await
        },
        _ => {
            Ok(BarkResponse::failure(
                directive.request_id,
                TargetNode::LexGrw,
                format!("Unsupported directive kind: {:?}", directive.kind),
            ))
        }
    }
}

async fn analyze_learning_needs(directive: BarkDirective) -> Result<BarkResponse, Box<dyn std::error::Error>> {
    println!("[LEX-GRW] 📊 Analyzing learning needs...");

    // Placeholder learning analysis
    let analysis = json!({
        "learning_analysis": "completed",
        "current_skill_level": "intermediate",
        "knowledge_gaps": ["advanced_topic_a", "skill_b"],
        "learning_style": "hands_on",
        "recommended_focus_areas": ["technical_skills", "soft_skills"],
        "timestamp": Utc::now()
    });

    println!("[LEX-GRW] 🎓 Learning needs analysis complete.");

    Ok(BarkResponse::success(
        directive.request_id,
        TargetNode::LexGrw,
        analysis,
    ))
}

async fn generate_learning_plan(directive: BarkDirective) -> Result<BarkResponse, Box<dyn std::error::Error>> {
    println!("[LEX-GRW] 📋 Generating learning plan...");

    // Placeholder learning plan
    let plan = json!({
        "plan_type": "personal_development",
        "duration": "6_months",
        "objectives": [
            "Improve technical proficiency",
            "Develop leadership skills",
            "Expand domain knowledge"
        ],
        "milestones": [
            {"month": 1, "focus": "foundation_building"},
            {"month": 3, "focus": "skill_application"},
            {"month": 6, "focus": "mastery_achievement"}
        ],
        "resources_needed": ["online_courses", "mentorship", "practice_projects"],
        "generated_at": Utc::now()
    });

    Ok(BarkResponse::success(
        directive.request_id,
        TargetNode::LexGrw,
        plan,
    ))
}

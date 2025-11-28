//! LEX-CRT Node - Content Creation and Output Generation
//!
//! This node handles content creation, output generation, and creative synthesis.
//! It responds to BARK Protocol directives for generating various types of content.

use bark_protocol::{
    BarkDirective, BarkResponse, DirectiveKind, TargetNode, ResponseStatus
};
use chrono::Utc;
use serde_json::json;
use std::io::{self, Read};
use uuid::Uuid;

const NODE_SIGIL: &str = "srp://alexis/lex-crt";

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("[LEX-CRT] 🎨 Node online. Content creation active.");
    println!("[LEX-CRT] 📡 Awaiting directives on BARK Protocol v3.1...");
    println!("[LEX-CRT] 🔐 Node Sigil: {}", NODE_SIGIL);

    // Start the node's main loop
    start_content_creation().await?;

    Ok(())
}

async fn start_content_creation() -> Result<(), Box<dyn std::error::Error>> {
    loop {
        // Listen for incoming directives
        println!("[LEX-CRT] 🎧 Listening for directives...");

        let mut buffer = String::new();
        if io::stdin().read_line(&mut buffer).is_ok() {
            if let Ok(trimmed) = serde_json::from_str::<BarkDirective>(&buffer.trim()) {
                println!("[LEX-CRT] 📨 Received directive: {} (Kind: {:?})",
                    trimmed.request_id, trimmed.kind);

                let response = process_directive(trimmed).await?;
                let response_json = serde_json::to_string(&response)?;

                println!("[LEX-CRT] 📤 Sending response: {}", response_json);
                println!("[LEX-CRT] ✅ Response sent successfully");
            } else {
                println!("[LEX-CRT] ❌ Failed to parse directive");
            }
        }

        // Small delay between processing directives
        tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
    }
}

async fn process_directive(directive: BarkDirective) -> Result<BarkResponse, Box<dyn std::error::Error>> {
    println!("[LEX-CRT] 🔍 Processing directive from: {}", directive.caller_sigil);

    // Verify directive authenticity (placeholder implementation)
    if let Err(e) = directive.verify_signature() {
        println!("[LEX-CRT] ⚠️ Signature verification failed: {}", e);
        return Ok(BarkResponse::failure(
            directive.request_id,
            TargetNode::LexCrt,
            format!("Signature verification failed: {}", e),
        ));
    }

    // Process based on directive kind
    match directive.kind {
        DirectiveKind::GENERATE => {
            generate_content(directive).await
        },
        DirectiveKind::ANALYZE => {
            analyze_content_requirements(directive).await
        },
        _ => {
            Ok(BarkResponse::failure(
                directive.request_id,
                TargetNode::LexCrt,
                format!("Unsupported directive kind: {:?}", directive.kind),
            ))
        }
    }
}

async fn generate_content(directive: BarkDirective) -> Result<BarkResponse, Box<dyn std::error::Error>> {
    println!("[LEX-CRT] 🎨 Generating content...");

    // Placeholder content generation
    let content = json!({
        "content_type": "generated_text",
        "topic": "placeholder",
        "length": "medium",
        "style": "professional",
        "generated_content": "This is placeholder generated content.",
        "timestamp": Utc::now()
    });

    println!("[LEX-CRT] 📝 Content generation complete.");

    Ok(BarkResponse::success(
        directive.request_id,
        TargetNode::LexCrt,
        content,
    ))
}

async fn analyze_content_requirements(directive: BarkDirective) -> Result<BarkResponse, Box<dyn std::error::Error>> {
    println!("[LEX-CRT] 📊 Analyzing content requirements...");

    // Placeholder analysis
    let analysis = json!({
        "requirements_analysis": "completed",
        "content_type_suggestions": ["article", "report", "presentation"],
        "estimated_complexity": "medium",
        "recommended_approach": "structured_generation",
        "timestamp": Utc::now()
    });

    Ok(BarkResponse::success(
        directive.request_id,
        TargetNode::LexCrt,
        analysis,
    ))
}
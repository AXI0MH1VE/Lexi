//! LEX-VIT Node - Vitality and Bio-State Monitoring
//! 
//! This node handles monitoring of vital signs, stress levels, sleep quality,
//! and overall biological state metrics. It responds to BARK Protocol directives
//! for health analysis and bioload assessment.

use bark_protocol::{
    BarkDirective, BarkResponse, DirectiveKind, TargetNode, ResponseStatus
};
use chrono::Utc;
use serde_json::json;
use std::io::{self, Read};
use uuid::Uuid;

const NODE_SIGIL: &str = "srp://alexis/lex-vit";

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("[LEX-VIT] 🧬 Node online. Vitality monitoring active.");
    println!("[LEX-VIT] 📡 Awaiting directives on BARK Protocol v3.1...");
    println!("[LEX-VIT] 🔐 Node Sigil: {}", NODE_SIGIL);

    // Start the node's main loop
    start_vitality_monitoring().await?;
    
    Ok(())
}

async fn start_vitality_monitoring() -> Result<(), Box<dyn std::error::Error>> {
    loop {
        // Listen for incoming directives
        println!("[LEX-VIT] 🎧 Listening for directives...");
        
        let mut buffer = String::new();
        if io::stdin().read_line(&mut buffer).is_ok() {
            if let Ok(trimmed) = serde_json::from_str::<BarkDirective>(&buffer.trim()) {
                println!("[LEX-VIT] 📨 Received directive: {} (Kind: {:?})", 
                    trimmed.request_id, trimmed.kind);
                
                let response = process_directive(trimmed).await?;
                let response_json = serde_json::to_string(&response)?;
                
                println!("[LEX-VIT] 📤 Sending response: {}", response_json);
                println!("[LEX-VIT] ✅ Response sent successfully");
            } else {
                println!("[LEX-VIT] ❌ Failed to parse directive");
            }
        }
        
        // Small delay between processing directives
        tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
    }
}

async fn process_directive(directive: BarkDirective) -> Result<BarkResponse, Box<dyn std::error::Error>> {
    println!("[LEX-VIT] 🔍 Processing directive from: {}", directive.caller_sigil);
    
    // Verify directive authenticity (placeholder implementation)
    if let Err(e) = directive.verify_signature() {
        println!("[LEX-VIT] ⚠️ Signature verification failed: {}", e);
        return Ok(BarkResponse::failure(
            directive.request_id,
            TargetNode::LexVit,
            format!("Signature verification failed: {}", e),
        ));
    }
    
    // Process based on directive kind
    match directive.kind {
        DirectiveKind::ANALYZE => {
            analyze_biological_state(directive).await
        },
        DirectiveKind::VERIFY => {
            verify_biological_metrics(directive).await
        },
        DirectiveKind::GENERATE => {
            generate_health_report(directive).await
        },
        _ => {
            Ok(BarkResponse::failure(
                directive.request_id,
                TargetNode::LexVit,
                format!("Unsupported directive kind: {:?}", directive.kind),
            ))
        }
    }
}

async fn analyze_biological_state(directive: BarkDirective) -> Result<BarkResponse, Box<dyn std::error::Error>> {
    println!("[LEX-VIT] 🧪 Analyzing biological state...");
    
    // Simulate real-time health data collection
    let bioload_percentage = simulate_bioload_monitoring();
    let hrv_morning = simulate_hrv_reading();
    let sleep_quality = simulate_sleep_analysis();
    let stress_level = simulate_stress_assessment();
    let cognitive_load = estimate_cognitive_load();
    
    // Determine overall health status
    let status = determine_health_status(bioload_percentage, stress_level, hrv_morning);
    
    let payload = json!({
        "bioload_percentage": bioload_percentage,
        "hrv_morning": hrv_morning,
        "sleep_quality_score": sleep_quality,
        "stress_level": stress_level,
        "cognitive_load_estimate": cognitive_load,
        "overall_status": status,
        "timestamp": Utc::now(),
        "metrics": {
            "resting_hr": 62 + (bioload_percentage as i32 * 0.1) as i32,
            "sleep_efficiency": 85 + (sleep_quality as i32 * 0.15) as i32,
            "recovery_index": 100 - stress_level,
            "vitality_score": calculate_vitality_score(bioload_percentage, hrv_morning, sleep_quality, stress_level)
        }
    });
    
    println!("[LEX-VIT] 📊 Analysis complete. BioLoad: {:.1}%, Status: {}", bioload_percentage, status);
    
    Ok(BarkResponse::success(
        directive.request_id,
        TargetNode::LexVit,
        payload,
    ))
}

async fn verify_biological_metrics(directive: BarkDirective) -> Result<BarkResponse, Box<dyn std::error::Error>> {
    println!("[LEX-VIT] ✅ Verifying biological metrics...");
    
    // Simulate metric verification
    let verification_result = json!({
        "verified": true,
        "confidence_score": 0.94,
        "metrics_checked": ["heart_rate", "hrv", "sleep", "stress"],
        "anomalies_detected": 0,
        "timestamp": Utc::now()
    });
    
    Ok(BarkResponse::success(
        directive.request_id,
        TargetNode::LexVit,
        verification_result,
    ))
}

async fn generate_health_report(directive: BarkDirective) -> Result<BarkResponse, Box<dyn std::error::Error>> {
    println!("[LEX-VIT] 📋 Generating comprehensive health report...");
    
    let report = json!({
        "report_type": "comprehensive_health",
        "period": "7_days",
        "summary": {
            "overall_wellness": "Good",
            "bio_load_trend": "stable",
            "sleep_consistency": "excellent",
            "stress_management": "adequate"
        },
        "recommendations": [
            "Maintain current sleep schedule",
            "Continue current stress management practices",
            "Consider increasing light exercise"
        ],
        "generated_at": Utc::now()
    });
    
    Ok(BarkResponse::success(
        directive.request_id,
        TargetNode::LexVit,
        report,
    ))
}

// Simulation functions for health metrics (placeholder implementations)
fn simulate_bioload_monitoring() -> f32 {
    // Simulate realistic bioload between 60-85%
    65.0 + (rand::random::<f32>() * 20.0)
}

fn simulate_hrv_reading() -> i32 {
    // HRV typically 50-80ms for healthy adults
    50 + (rand::random::<u32>() % 31) as i32
}

fn simulate_sleep_analysis() -> f32 {
    // Sleep quality score 0-100
    75.0 + (rand::random::<f32>() * 25.0)
}

fn simulate_stress_assessment() -> f32 {
    // Stress level 0-100 (lower is better)
    20.0 + (rand::random::<f32>() * 40.0)
}

fn estimate_cognitive_load() -> String {
    // Cognitive load scale 1-10
    let load = 5 + (rand::random::<u32>() % 6) as i32;
    format!("{}/10", load)
}

fn determine_health_status(bioload: f32, stress: f32, hrv: i32) -> String {
    match (bioload, stress, hrv) {
        (b, s, h) if b < 70.0 && s < 40.0 && h > 60 => "Excellent".to_string(),
        (b, s, h) if b < 75.0 && s < 50.0 && h > 55 => "Good".to_string(),
        (b, s, h) if b < 80.0 && s < 60.0 && h > 50 => "Acceptable".to_string(),
        _ => "Needs Attention".to_string(),
    }
}

fn calculate_vitality_score(bioload: f32, hrv: i32, sleep: f32, stress: f32) -> f32 {
    // Calculate composite vitality score (0-100)
    let bioload_score = (100.0 - bioload) * 0.4;
    let hrv_score = (hrv as f32 / 80.0) * 100.0 * 0.25;
    let sleep_score = sleep * 0.2;
    let stress_score = (100.0 - stress) * 0.15;
    
    (bioload_score + hrv_score + sleep_score + stress_score).clamp(0.0, 100.0)
}
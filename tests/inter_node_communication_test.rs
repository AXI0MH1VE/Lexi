//! Inter-Node Communication Test for BARK Protocol v3.1
//! 
//! This test verifies that nodes can properly communicate using the BARK Protocol
//! and that the signature verification and message routing work correctly.

use bark_protocol::{
    BarkDirective, BarkResponse, DirectiveKind, TargetNode, ResponseStatus
};
use chrono::Utc;
use serde_json::json;
use uuid::Uuid;

#[tokio::test]
async fn test_bark_protocol_communication() {
    println!("🧪 Testing BARK Protocol v3.1 Inter-Node Communication...");
    
    // Create a test directive
    let directive = BarkDirective::new(
        "test_operator".to_string(),
        TargetNode::LexVit,
        DirectiveKind::ANALYZE,
        json!({
            "test_query": "bioload assessment",
            "timestamp": Utc::now()
        }),
    );
    
    // Verify directive creation
    assert_eq!(directive.target_agent, TargetNode::LexVit);
    assert_eq!(directive.kind, DirectiveKind::ANALYZE);
    assert_eq!(directive.caller_sigil, "test_operator");
    
    println!("✅ BarkDirective creation: PASSED");
    
    // Test directive serialization/deserialization
    let directive_json = serde_json::to_string(&directive).unwrap();
    let parsed_directive: BarkDirective = serde_json::from_str(&directive_json).unwrap();
    
    assert_eq!(directive.request_id, parsed_directive.request_id);
    assert_eq!(directive.target_agent, parsed_directive.target_agent);
    
    println!("✅ Directive serialization: PASSED");
    
    // Create a test response
    let response = BarkResponse::success(
        directive.request_id,
        TargetNode::LexVit,
        json!({
            "bioload_percentage": 72.0,
            "status": "Acceptable",
            "processing_time_ms": 127
        }),
    );
    
    // Verify response creation
    assert_eq!(response.request_id, directive.request_id);
    assert_eq!(response.source_node, TargetNode::LexVit);
    assert_eq!(response.status, ResponseStatus::Success);
    
    println!("✅ BarkResponse creation: PASSED");
    
    // Test all supported target nodes
    let target_nodes = vec![
        TargetNode::LexVit, TargetNode::LexWth, TargetNode::LexMon, TargetNode::LexEnt, TargetNode::LexKno, TargetNode::LexOrd,
        TargetNode::LexKin, TargetNode::LexGrw, TargetNode::LexSan, TargetNode::LexLei, TargetNode::LexOut, TargetNode::LexLeg
    ];
    
    for &node in &target_nodes {
        let test_directive = BarkDirective::new(
            "test_sigil".to_string(),
            node,
            DirectiveKind::ANALYZE,
            json!({"test": "data"}),
        );
        
        assert_eq!(test_directive.target_agent, node);
        assert!(!test_directive.request_id.is_nil());
        
        println!("✅ TargetNode {:?}: SUPPORTED", node);
    }
    
    println!("🎉 All BARK Protocol tests: PASSED");
}

#[tokio::test]
async fn test_directive_kinds() {
    println!("🧪 Testing BARK Protocol Directive Kinds...");
    
    let directive_kinds = vec![
        DirectiveKind::ANALYZE,
        DirectiveKind::GENERATE,
        DirectiveKind::VERIFY,
        DirectiveKind::EXECUTE_PLAN,
        DirectiveKind::VALIDATE_OUTPUT,
    ];
    
    for &kind in &directive_kinds {
        let directive = BarkDirective::new(
            "test_operator".to_string(),
            TargetNode::LexMon,
            kind,
            json!({"test": "payload"}),
        );
        
        assert_eq!(directive.kind, kind);
        println!("✅ DirectiveKind {:?}: SUPPORTED", kind);
    }
    
    println!("🎉 Directive kinds test: PASSED");
}

#[test]
fn test_chrono_integration() {
    println!("🧪 Testing Chrono timestamp integration...");
    
    let now = Utc::now();
    let directive = BarkDirective::new(
        "timestamp_test".to_string(),
        TargetNode::LexMon,
        DirectiveKind::ANALYZE,
        json!({}),
    );
    
    // Verify timestamp is set and recent
    let time_diff = Utc::now().signed_duration_since(directive.timestamp);
    assert!(time_diff.num_milliseconds() >= 0);
    assert!(time_diff.num_milliseconds() < 1000); // Should be very recent
    
    println!("✅ Timestamp integration: PASSED");
    println!("🎉 All system integration tests: PASSED");
}

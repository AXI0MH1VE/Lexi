//! BARK Protocol v3.1 - Shared Communication Library
//! 
//! This crate defines the core message types and communication protocol
//! used for inter-node communication in the LEX-7 distributed system.

use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use uuid::Uuid;

/// Valid node types in the LEX-7 system
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum TargetNode {
    LexVit,   // Vitality monitoring node
    LexWth,   // Wealth/financial analysis node
    LexMon,   // Monitoring/coordination router
    LexEnt,   // Enterprise/strategic node
    LexKno,   // Knowledge processing node
    LexCrt,   // Creation/output node
    LexOrd,   // Order/logistics node
    LexKin,   // Kinship/social node
    LexGrw,   // Growth/learning node
    LexSan,   // Sanctuary/environment node
    LexLei,   // Leisure/recovery node
    LexOut,   // Outreach/communication node
    LexLeg,   // Legacy/meta-analysis node
}

/// Valid directive kinds for the BARK protocol
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum DirectiveKind {
    ANALYZE,        // Request analysis of data
    GENERATE,       // Request content generation
    VERIFY,         // Request verification of data
    EXECUTE_PLAN,   // Execute a strategic plan
    VALIDATE_OUTPUT, // Validate generated output
}

/// Core directive structure for BARK Protocol v3.1
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BarkDirective {
    pub request_id: Uuid,
    pub caller_sigil: String,
    pub target_agent: TargetNode,
    pub kind: DirectiveKind,
    pub payload: serde_json::Value,
    pub governance_vector: Option<String>,
    pub timestamp: DateTime<Utc>,
    pub signature: Option<String>,
}

/// Response status types
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum ResponseStatus {
    Success,
    Failure,
    Pending,
    Rejected,
}

/// Response structure for BARK Protocol
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BarkResponse {
    pub request_id: Uuid,
    pub source_node: TargetNode,
    pub status: ResponseStatus,
    pub payload: serde_json::Value,
    pub signature: String,
    pub timestamp: DateTime<Utc>,
}

use ed25519_dalek::{SigningKey, VerifyingKey, SigningKeyError, VerifyingKeyError, Signature};
use ed25519_dalek::ed25519::signature::{Signer, Verifier};

impl BarkDirective {
    /// Create a new directive with minimal required fields
    pub fn new(
        caller_sigil: String,
        target_agent: TargetNode,
        kind: DirectiveKind,
        payload: serde_json::Value,
    ) -> Self {
        Self {
            request_id: Uuid::new_v4(),
            caller_sigil,
            target_agent,
            kind,
            payload,
            governance_vector: None,
            timestamp: Utc::now(),
            signature: None,
        }
    }

    /// Create a new directive with signature
    pub fn new_signed(
        caller_sigil: String,
        target_agent: TargetNode,
        kind: DirectiveKind,
        payload: serde_json::Value,
        signing_key: &SigningKey,
    ) -> Result<Self, SigningKeyError> {
        let mut directive = Self {
            request_id: Uuid::new_v4(),
            caller_sigil,
            target_agent,
            kind,
            payload,
            governance_vector: None,
            timestamp: Utc::now(),
            signature: None,
        };
        
        directive.sign(signing_key)?;
        Ok(directive)
    }

    /// Verify the directive signature using Ed25519
    pub fn verify_signature(&self, verifying_key: &VerifyingKey) -> Result<bool, VerifyingKeyError> {
        if let Some(signature_str) = &self.signature {
            // Parse the signature from hex string
            let signature_bytes = hex::decode(signature_str).map_err(|_| {
                VerifyingKeyError::SignatureNotCanonical
            })?;
            
            let signature = Signature::from_bytes(&signature_bytes);
            
            // Create canonical message for signing
            let canonical_message = self.canonical_message();
            
            verifying_key.verify(&canonical_message, &signature)
        } else {
            Ok(false)
        }
    }

    /// Sign the directive with the caller's private key using Ed25519
    pub fn sign(&mut self, signing_key: &SigningKey) -> Result<(), SigningKeyError> {
        let canonical_message = self.canonical_message();
        let signature = signing_key.sign(&canonical_message);
        
        // Store signature as hex string
        self.signature = Some(hex::encode(signature.to_bytes()));
        Ok(())
    }

    /// Create canonical message for signing/verification
    fn canonical_message(&self) -> Vec<u8> {
        // Create deterministic message from directive fields
        let message = format!(
            "{}{}{}{}{}{}{}{}",
            self.request_id,
            self.caller_sigil,
            self.target_agent as u8,
            self.kind as u8,
            self.payload,
            self.governance_vector.as_ref().unwrap_or(&"null".to_string()),
            self.timestamp.timestamp(),
            self.request_id
        );
        message.into_bytes()
    }
}

impl BarkResponse {
    /// Create a successful response
    pub fn success(
        request_id: Uuid,
        source_node: TargetNode,
        payload: serde_json::Value,
    ) -> Self {
        Self {
            request_id,
            source_node,
            status: ResponseStatus::Success,
            payload,
            signature: "[signed_success]".to_string(),
            timestamp: Utc::now(),
        }
    }

    /// Create a failure response
    pub fn failure(
        request_id: Uuid,
        source_node: TargetNode,
        error_message: String,
    ) -> Self {
        Self {
            request_id,
            source_node,
            status: ResponseStatus::Failure,
            payload: serde_json::json!({ "error": error_message }),
            signature: "[signed_failure]".to_string(),
            timestamp: Utc::now(),
        }
    }
}

/// Node health status for monitoring
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NodeHealth {
    pub node_id: TargetNode,
    pub status: String, // "online", "offline", "degraded"
    pub last_heartbeat: DateTime<Utc>,
    pub load_percentage: f32,
    pub memory_usage_mb: u64,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_directive_creation() {
        let directive = BarkDirective::new(
            "operator_test".to_string(),
            TargetNode::LexVit,
            DirectiveKind::ANALYZE,
            serde_json::json!({ "data": "test" }),
        );

        assert_eq!(directive.target_agent, TargetNode::LexVit);
        assert_eq!(directive.kind, DirectiveKind::ANALYZE);
        assert!(directive.signature.is_none());
    }

    #[test]
    fn test_response_creation() {
        let response = BarkResponse::success(
            Uuid::new_v4(),
            TargetNode::LexVit,
            serde_json::json!({ "result": "success" }),
        );

        assert_eq!(response.status, ResponseStatus::Success);
        assert_eq!(response.source_node, TargetNode::LexVit);
    }
}

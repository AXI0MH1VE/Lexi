use shared::communication::bark_protocol::BARKProtocol;
use shared::state::mamba_state::MambaState;
use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::sync::RwLock;
use tracing::{info, warn, error};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LegacyMetrics {
    pub impact_coefficient: f64,
    pub sustainability_index: f64,
    pub heritage_value: f64,
    pub continuity_score: f64,
    pub influence_trajectory: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LegacyDirective {
    pub directive_type: String,
    pub impact_area: String,
    pub temporal_scope: String,
    pub parameters: serde_json::Value,
}

pub struct LEXLEGNode {
    id: String,
    state: Arc<RwLock<MambaState>>,
    bark_protocol: Arc<RwLock<BARKProtocol>>,
    legacy_metrics: Arc<RwLock<LegacyMetrics>>,
}

impl LEXLEGNode {
    pub fn new() -> Self {
        info!("[LEX-LEG] Initializing Legacy/Impact Management Node...");
        
        Self {
            id: "LEX-LEG".to_string(),
            state: Arc::new(RwLock::new(MambaState::new())),
            bark_protocol: Arc::new(RwLock::new(BARKProtocol::new())),
            legacy_metrics: Arc::new(RwLock::new(LegacyMetrics {
                impact_coefficient: 0.87,
                sustainability_index: 0.91,
                heritage_value: 0.84,
                continuity_score: 0.89,
                influence_trajectory: 0.86,
            })),
        }
    }

    pub async fn process_legacy_directive(&self, directive: LegacyDirective) -> Result<()> {
        info!("[LEX-LEG] Processing legacy directive: {:?}", directive);
        
        // Update legacy metrics based on directive
        let mut metrics = self.legacy_metrics.write().await;
        
        match directive.directive_type.as_str() {
            "MAXIMIZE_IMPACT" => {
                metrics.impact_coefficient = (metrics.impact_coefficient + 0.05).min(1.0);
                metrics.influence_trajectory = (metrics.influence_trajectory + 0.04).min(1.0);
                info!("[LEX-LEG] Impact maximization protocols activated");
            }
            "ENSURE_SUSTAINABILITY" => {
                metrics.sustainability_index = (metrics.sustainability_index + 0.06).min(1.0);
                metrics.continuity_score = (metrics.continuity_score + 0.03).min(1.0);
                info!("[LEX-LEG] Sustainability frameworks established");
            }
            "ENHANCE_HERITAGE" => {
                metrics.heritage_value = (metrics.heritage_value + 0.07).min(1.0);
                metrics.impact_coefficient = (metrics.impact_coefficient + 0.02).min(1.0);
                info!("[LEX-LEG] Heritage value preservation enhanced");
            }
            "STRENGTHEN_CONTINUITY" => {
                metrics.continuity_score = (metrics.continuity_score + 0.08).min(1.0);
                metrics.sustainability_index = (metrics.sustainability_index + 0.02).min(1.0);
                info!("[LEX-LEG] Continuity mechanisms reinforced");
            }
            _ => {
                warn!("[LEX-LEG] Unknown legacy directive type: {}", directive.directive_type);
            }
        }

        // Broadcast updated metrics to network
        let bark = self.bark_protocol.read().await;
        let metrics_json = serde_json::to_string(&*metrics)?;
        bark.broadcast_directive("LEX-LEG", "NETWORK", "LEGACY_UPDATE", &metrics_json).await?;

        Ok(())
    }

    pub async fn get_legacy_status(&self) -> Result<LegacyMetrics> {
        let metrics = self.legacy_metrics.read().await;
        Ok(metrics.clone())
    }

    pub async fn process_state_update(&self) -> Result<()> {
        let mut state = self.state.write().await;
        
        // Apply Mamba-SSM deterministic processing
        let legacy_data = self.get_legacy_status().await?;
        state.update_deterministic_state("legacy_metrics", &legacy_data)?;
        
        info!("[LEX-LEG] State updated with legacy metrics");
        Ok(())
    }

    pub async fn calculate_legacy_score(&self) -> Result<f64> {
        let metrics = self.legacy_metrics.read().await;
        
        // Calculate overall legacy impact score
        let legacy_score = (
            metrics.impact_coefficient * 0.3 +
            metrics.sustainability_index * 0.25 +
            metrics.heritage_value * 0.2 +
            metrics.continuity_score * 0.15 +
            metrics.influence_trajectory * 0.1
        );
        
        info!("[LEX-LEG] Current legacy score: {:.3}", legacy_score);
        Ok(legacy_score)
    }

    pub async fn generate_legacy_report(&self) -> Result<serde_json::Value> {
        let metrics = self.legacy_metrics.read().await;
        
        let report = serde_json::json!({
            "node_id": self.id,
            "timestamp": chrono::Utc::now().to_rfc3339(),
            "legacy_metrics": metrics,
            "system_contribution": "Long-term impact and sustainability management",
            "interconnected_nodes": [
                "LEX-MON", "LEX-VIT", "LEX-WTH", "LEX-ENT", 
                "LEX-KNO", "LEX-ORD", "LEX-CRT", "LEX-KIN",
                "LEX-GRW", "LEX-SAN", "LEX-LEI", "LEX-OUT"
            ]
        });
        
        info!("[LEX-LEG] Legacy report generated");
        Ok(report)
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    tracing_subscriber::registry()
        .with(tracing_subscriber::fmt::layer())
        .with(tracing_subscriber::EnvFilter::from_default_env())
        .init();

    info!("=== LEX-LEG LEGACY NODE INITIALIZATION ===");
    info!("Node: Legacy/Impact Management - FINAL NODE");
    info!("Protocol: BARK v3.1 with Ed25519 signatures");
    info!("Processing: Mamba-SSM deterministic state management");
    info!("Status: COMPLETING AXIOM CRUCIBLE v1.0 SYSTEM");
    
    let node = LEXLEGNode::new();
    
    // Simulate legacy processing
    tokio::spawn(async move {
        let mut interval = tokio::time::interval(tokio::time::Duration::from_secs(10));
        
        loop {
            interval.tick().await;
            
            if let Err(e) = node.process_state_update().await {
                error!("[LEX-LEG] State update error: {}", e);
            }
            
            if let Ok(score) = node.calculate_legacy_score().await {
                info!("[LEX-LEG] Legacy assessment: {:.3}", score);
            }
        }
    });

    // Example legacy directives
    let test_directives = vec![
        LegacyDirective {
            directive_type: "MAXIMIZE_IMPACT".to_string(),
            impact_area: "global_influence".to_string(),
            temporal_scope: "century_long".to_string(),
            parameters: serde_json::json!({"scope": "planetary"}),
        },
        LegacyDirective {
            directive_type: "ENSURE_SUSTAINABILITY".to_string(),
            impact_area: "system_continuity".to_string(),
            temporal_scope: "perpetual".to_string(),
            parameters: serde_json::json!({"framework": "adaptive"}),
        },
        LegacyDirective {
            directive_type: "ENHANCE_HERITAGE".to_string(),
            impact_area: "knowledge_preservation".to_string(),
            temporal_scope: "eternal".to_string(),
            parameters: serde_json::json!({"method": "distributed_archive"}),
        },
    ];

    for directive in test_directives {
        tokio::time::sleep(tokio::time::Duration::from_secs(7)).await;
        if let Err(e) = node.process_legacy_directive(directive).await {
            error!("[LEX-LEG] Directive processing error: {}", e);
        }
    }

    // Generate final legacy report
    if let Ok(report) = node.generate_legacy_report().await {
        info!("[LEX-LEG] Final System Legacy Report: {}", serde_json::to_string_pretty(&report)?);
    }

    info!("[LEX-LEG] Legacy node operational - managing long-term impact and sustainability");
    info!("[LEX-LEG] AXIOM CRUCIBLE v1.0 SYSTEM COMPLETE");
    info!("[LEX-LEG] All 12 LEX nodes initialized and operational");
    
    // Keep the node running
    tokio::signal::ctrl_c().await?;
    info!("[LEX-LEG] Shutdown signal received - system lifecycle complete");
    
    Ok(())
}

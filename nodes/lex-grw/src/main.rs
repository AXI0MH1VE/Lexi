use shared::communication::bark_protocol::BARKProtocol;
use shared::state::mamba_state::MambaState;
use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::sync::RwLock;
use tracing::{info, warn, error};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GrowthMetrics {
    pub expansion_rate: f64,
    pub capability_enhancement: f64,
    pub learning_velocity: f64,
    pub innovation_index: f64,
    pub scalability_factor: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GrowthDirective {
    pub directive_type: String,
    pub growth_area: String,
    pub expansion_target: String,
    pub parameters: serde_json::Value,
}

pub struct LEXGRWNode {
    id: String,
    state: Arc<RwLock<MambaState>>,
    bark_protocol: Arc<RwLock<BARKProtocol>>,
    growth_metrics: Arc<RwLock<GrowthMetrics>>,
}

impl LEXGRWNode {
    pub fn new() -> Self {
        info!("[LEX-GRW] Initializing Growth/Development Node...");
        
        Self {
            id: "LEX-GRW".to_string(),
            state: Arc::new(RwLock::new(MambaState::new())),
            bark_protocol: Arc::new(RwLock::new(BARKProtocol::new())),
            growth_metrics: Arc::new(RwLock::new(GrowthMetrics {
                expansion_rate: 0.73,
                capability_enhancement: 0.81,
                learning_velocity: 0.68,
                innovation_index: 0.77,
                scalability_factor: 0.85,
            })),
        }
    }

    pub async fn process_growth_directive(&self, directive: GrowthDirective) -> Result<()> {
        info!("[LEX-GRW] Processing growth directive: {:?}", directive);
        
        // Update growth metrics based on directive
        let mut metrics = self.growth_metrics.write().await;
        
        match directive.directive_type.as_str() {
            "EXPAND_CAPABILITIES" => {
                metrics.capability_enhancement = (metrics.capability_enhancement + 0.06).min(1.0);
                metrics.expansion_rate = (metrics.expansion_rate + 0.04).min(1.0);
                info!("[LEX-GRW] Capabilities enhanced and expanded");
            }
            "ACCELERATE_LEARNING" => {
                metrics.learning_velocity = (metrics.learning_velocity + 0.08).min(1.0);
                info!("[LEX-GRW] Learning velocity increased");
            }
            "BOOST_INNOVATION" => {
                metrics.innovation_index = (metrics.innovation_index + 0.05).min(1.0);
                metrics.scalability_factor = (metrics.scalability_factor + 0.03).min(1.0);
                info!("[LEX-GRW] Innovation metrics boosted");
            }
            "OPTIMIZE_SCALING" => {
                metrics.scalability_factor = (metrics.scalability_factor + 0.07).min(1.0);
                info!("[LEX-GRW] Scalability optimization completed");
            }
            _ => {
                warn!("[LEX-GRW] Unknown growth directive type: {}", directive.directive_type);
            }
        }

        // Broadcast updated metrics to network
        let bark = self.bark_protocol.read().await;
        let metrics_json = serde_json::to_string(&*metrics)?;
        bark.broadcast_directive("LEX-GRW", "NETWORK", "GROWTH_UPDATE", &metrics_json).await?;

        Ok(())
    }

    pub async fn get_growth_status(&self) -> Result<GrowthMetrics> {
        let metrics = self.growth_metrics.read().await;
        Ok(metrics.clone())
    }

    pub async fn process_state_update(&self) -> Result<()> {
        let mut state = self.state.write().await;
        
        // Apply Mamba-SSM deterministic processing
        let growth_data = self.get_growth_status().await?;
        state.update_deterministic_state("growth_metrics", &growth_data)?;
        
        info!("[LEX-GRW] State updated with growth metrics");
        Ok(())
    }

    pub async fn calculate_growth_trajectory(&self) -> Result<f64> {
        let metrics = self.growth_metrics.read().await;
        
        // Calculate composite growth trajectory
        let trajectory = (
            metrics.expansion_rate * 0.25 +
            metrics.capability_enhancement * 0.25 +
            metrics.learning_velocity * 0.2 +
            metrics.innovation_index * 0.15 +
            metrics.scalability_factor * 0.15
        );
        
        info!("[LEX-GRW] Growth trajectory calculated: {:.3}", trajectory);
        Ok(trajectory)
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    tracing_subscriber::registry()
        .with(tracing_subscriber::fmt::layer())
        .with(tracing_subscriber::EnvFilter::from_default_env())
        .init();

    info!("=== LEX-GRW GROWTH NODE INITIALIZATION ===");
    info!("Node: Growth/Development Management");
    info!("Protocol: BARK v3.1 with Ed25519 signatures");
    info!("Processing: Mamba-SSM deterministic state management");
    
    let node = LEXGRWNode::new();
    
    // Simulate growth processing
    tokio::spawn(async move {
        let mut interval = tokio::time::interval(tokio::time::Duration::from_secs(7));
        
        loop {
            interval.tick().await;
            
            if let Err(e) = node.process_state_update().await {
                error!("[LEX-GRW] State update error: {}", e);
            }
            
            if let Ok(trajectory) = node.calculate_growth_trajectory().await {
                info!("[LEX-GRW] Current growth trajectory: {:.3}", trajectory);
            }
        }
    });

    // Example growth directives
    let test_directives = vec![
        GrowthDirective {
            directive_type: "EXPAND_CAPABILITIES".to_string(),
            growth_area: "cognitive_processing".to_string(),
            expansion_target: "multi_domain".to_string(),
            parameters: serde_json::json!({"intensity": 0.85}),
        },
        GrowthDirective {
            directive_type: "BOOST_INNOVATION".to_string(),
            growth_area: "algorithmic_efficiency".to_string(),
            expansion_target: "optimization".to_string(),
            parameters: serde_json::json!({"scope": "system_wide"}),
        },
        GrowthDirective {
            directive_type: "ACCELERATE_LEARNING".to_string(),
            growth_area: "adaptive_patterns".to_string(),
            expansion_target: "dynamic_optimization".to_string(),
            parameters: serde_json::json!({"velocity": "high"}),
        },
    ];

    for directive in test_directives {
        tokio::time::sleep(tokio::time::Duration::from_secs(3)).await;
        if let Err(e) = node.process_growth_directive(directive).await {
            error!("[LEX-GRW] Directive processing error: {}", e);
        }
    }

    info!("[LEX-GRW] Growth node operational - expanding capabilities and learning velocity");
    
    // Keep the node running
    tokio::signal::ctrl_c().await?;
    info!("[LEX-GRW] Shutdown signal received");
    
    Ok(())
}

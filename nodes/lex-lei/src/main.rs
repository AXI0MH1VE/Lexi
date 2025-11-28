use shared::communication::bark_protocol::BARKProtocol;
use shared::state::mamba_state::MambaState;
use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::sync::RwLock;
use tracing::{info, warn, error};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LeisureMetrics {
    pub balance_factor: f64,
    pub recreation_index: f64,
    pub creativity_level: f64,
    pub relaxation_coefficient: f64,
    pub inspiration_score: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LeisureDirective {
    pub directive_type: String,
    pub activity_type: String,
    pub intensity_level: String,
    pub parameters: serde_json::Value,
}

pub struct LEXLEINode {
    id: String,
    state: Arc<RwLock<MambaState>>,
    bark_protocol: Arc<RwLock<BARKProtocol>>,
    leisure_metrics: Arc<RwLock<LeisureMetrics>>,
}

impl LEXLEINode {
    pub fn new() -> Self {
        info!("[LEX-LEI] Initializing Leisure/Creativity Node...");
        
        Self {
            id: "LEX-LEI".to_string(),
            state: Arc::new(RwLock::new(MambaState::new())),
            bark_protocol: Arc::new(RwLock::new(BARKProtocol::new())),
            leisure_metrics: Arc::new(RwLock::new(LeisureMetrics {
                balance_factor: 0.79,
                recreation_index: 0.83,
                creativity_level: 0.88,
                relaxation_coefficient: 0.76,
                inspiration_score: 0.85,
            })),
        }
    }

    pub async fn process_leisure_directive(&self, directive: LeisureDirective) -> Result<()> {
        info!("[LEX-LEI] Processing leisure directive: {:?}", directive);
        
        // Update leisure metrics based on directive
        let mut metrics = self.leisure_metrics.write().await;
        
        match directive.directive_type.as_str() {
            "ENHANCE_CREATIVITY" => {
                metrics.creativity_level = (metrics.creativity_level + 0.06).min(1.0);
                metrics.inspiration_score = (metrics.inspiration_score + 0.04).min(1.0);
                info!("[LEX-LEI] Creativity enhancement applied");
            }
            "BOOST_RECREATION" => {
                metrics.recreation_index = (metrics.recreation_index + 0.05).min(1.0);
                metrics.balance_factor = (metrics.balance_factor + 0.03).min(1.0);
                info!("[LEX-LEI] Recreation metrics boosted");
            }
            "PROMOTE_RELAXATION" => {
                metrics.relaxation_coefficient = (metrics.relaxation_coefficient + 0.07).min(1.0);
                metrics.balance_factor = (metrics.balance_factor + 0.02).min(1.0);
                info!("[LEX-LEI] Relaxation protocols activated");
            }
            "BALANCE_WORK_LIFE" => {
                metrics.balance_factor = (metrics.balance_factor + 0.08).min(1.0);
                info!("[LEX-LEI] Work-life balance optimization");
            }
            _ => {
                warn!("[LEX-LEI] Unknown leisure directive type: {}", directive.directive_type);
            }
        }

        // Broadcast updated metrics to network
        let bark = self.bark_protocol.read().await;
        let metrics_json = serde_json::to_string(&*metrics)?;
        bark.broadcast_directive("LEX-LEI", "NETWORK", "LEISURE_UPDATE", &metrics_json).await?;

        Ok(())
    }

    pub async fn get_leisure_status(&self) -> Result<LeisureMetrics> {
        let metrics = self.leisure_metrics.read().await;
        Ok(metrics.clone())
    }

    pub async fn process_state_update(&self) -> Result<()> {
        let mut state = self.state.write().await;
        
        // Apply Mamba-SSM deterministic processing
        let leisure_data = self.get_leisure_status().await?;
        state.update_deterministic_state("leisure_metrics", &leisure_data)?;
        
        info!("[LEX-LEI] State updated with leisure metrics");
        Ok(())
    }

    pub async fn calculate_wellbeing_index(&self) -> Result<f64> {
        let metrics = self.leisure_metrics.read().await;
        
        // Calculate overall wellbeing index
        let wellbeing = (
            metrics.balance_factor * 0.25 +
            metrics.recreation_index * 0.2 +
            metrics.creativity_level * 0.25 +
            metrics.relaxation_coefficient * 0.15 +
            metrics.inspiration_score * 0.15
        );
        
        info!("[LEX-LEI] Current wellbeing index: {:.3}", wellbeing);
        Ok(wellbeing)
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    tracing_subscriber::registry()
        .with(tracing_subscriber::fmt::layer())
        .with(tracing_subscriber::EnvFilter::from_default_env())
        .init();

    info!("=== LEX-LEI LEISURE NODE INITIALIZATION ===");
    info!("Node: Leisure/Creativity Management");
    info!("Protocol: BARK v3.1 with Ed25519 signatures");
    info!("Processing: Mamba-SSM deterministic state management");
    
    let node = LEXLEINode::new();
    
    // Simulate leisure processing
    tokio::spawn(async move {
        let mut interval = tokio::time::interval(tokio::time::Duration::from_secs(8));
        
        loop {
            interval.tick().await;
            
            if let Err(e) = node.process_state_update().await {
                error!("[LEX-LEI] State update error: {}", e);
            }
            
            if let Ok(wellbeing) = node.calculate_wellbeing_index().await {
                info!("[LEX-LEI] Wellbeing assessment: {:.3}", wellbeing);
            }
        }
    });

    // Example leisure directives
    let test_directives = vec![
        LeisureDirective {
            directive_type: "ENHANCE_CREATIVITY".to_string(),
            activity_type: "artistic_expression".to_string(),
            intensity_level: "medium".to_string(),
            parameters: serde_json::json!({"focus": "innovation"}),
        },
        LeisureDirective {
            directive_type: "PROMOTE_RELAXATION".to_string(),
            activity_type: "mindfulness".to_string(),
            intensity_level: "gentle".to_string(),
            parameters: serde_json::json!({"duration": 15}),
        },
    ];

    for directive in test_directives {
        tokio::time::sleep(tokio::time::Duration::from_secs(5)).await;
        if let Err(e) = node.process_leisure_directive(directive).await {
            error!("[LEX-LEI] Directive processing error: {}", e);
        }
    }

    info!("[LEX-LEI] Leisure node operational - maintaining creativity and wellbeing balance");
    
    // Keep the node running
    tokio::signal::ctrl_c().await?;
    info!("[LEX-LEI] Shutdown signal received");
    
    Ok(())
}

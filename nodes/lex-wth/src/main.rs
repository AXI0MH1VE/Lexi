//! LEX-WTH Node - Wealth and Financial Runway Analysis
//! 
//! This node manages financial state, runway calculations, expense tracking,
//! and economic forecasting. It responds to BARK Protocol directives for
//! financial analysis and strategic financial decisions.

use bark_protocol::{
    BarkDirective, BarkResponse, DirectiveKind, TargetNode, ResponseStatus
};
use chrono::Utc;
use serde_json::json;
use std::io::{self, Read};
use uuid::Uuid;

const NODE_SIGIL: &str = "srp://alexis/lex-wth";

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("[LEX-WTH] 💰 Node online. Financial runway monitoring active.");
    println!("[LEX-WTH] 📡 Awaiting directives on BARK Protocol v3.1...");
    println!("[LEX-WTH] 🔐 Node Sigil: {}", NODE_SIGIL);

    // Start the node's main loop
    start_wealth_monitoring().await?;
    
    Ok(())
}

async fn start_wealth_monitoring() -> Result<(), Box<dyn std::error::Error>> {
    loop {
        // Listen for incoming directives
        println!("[LEX-WTH] 🎧 Listening for financial directives...");
        
        let mut buffer = String::new();
        if io::stdin().read_line(&mut buffer).is_ok() {
            if let Ok(trimmed) = serde_json::from_str::<BarkDirective>(&buffer.trim()) {
                println!("[LEX-WTH] 📨 Received directive: {} (Kind: {:?})", 
                    trimmed.request_id, trimmed.kind);
                
                let response = process_directive(trimmed).await?;
                let response_json = serde_json::to_string(&response)?;
                
                println!("[LEX-WTH] 📤 Sending response: {}", response_json);
                println!("[LEX-WTH] ✅ Financial analysis complete");
            } else {
                println!("[LEX-WTH] ❌ Failed to parse financial directive");
            }
        }
        
        // Small delay between processing directives
        tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
    }
}

async fn process_directive(directive: BarkDirective) -> Result<BarkResponse, Box<dyn std::error::Error>> {
    println!("[LEX-WTH] 🔍 Processing financial directive from: {}", directive.caller_sigil);
    
    // Verify directive authenticity
    if let Err(e) = directive.verify_signature() {
        println!("[LEX-WTH] ⚠️ Signature verification failed: {}", e);
        return Ok(BarkResponse::failure(
            directive.request_id,
            TargetNode::LexWth,
            format!("Signature verification failed: {}", e),
        ));
    }
    
    // Process based on directive kind
    match directive.kind {
        DirectiveKind::ANALYZE => {
            analyze_financial_runway(directive).await
        },
        DirectiveKind::VERIFY => {
            verify_financial_metrics(directive).await
        },
        DirectiveKind::GENERATE => {
            generate_financial_report(directive).await
        },
        _ => {
            Ok(BarkResponse::failure(
                directive.request_id,
                TargetNode::LexWth,
                format!("Unsupported directive kind: {:?}", directive.kind),
            ))
        }
    }
}

async fn analyze_financial_runway(directive: BarkDirective) -> Result<BarkResponse, Box<dyn std::error::Error>> {
    println!("[LEX-WTH] 📊 Analyzing financial runway...");
    
    // Simulate financial data collection
    let current_balance = simulate_current_balance();
    let monthly_expenses = simulate_monthly_expenses();
    let projected_income = simulate_monthly_income();
    let emergency_reserve = simulate_emergency_fund();
    let debt_levels = simulate_debt_analysis();
    
    // Calculate key financial metrics
    let burn_rate = calculate_burn_rate(monthly_expenses, projected_income);
    let runway_months = calculate_runway(current_balance, burn_rate);
    let financial_health_score = calculate_financial_health_score(current_balance, runway_months, debt_levels);
    let risk_assessment = assess_financial_risk(runway_months, debt_levels);
    
    // Generate recommendations
    let recommendations = generate_financial_recommendations(runway_months, burn_rate, debt_levels);
    
    let payload = json!({
        "current_balance_usd": current_balance,
        "monthly_expenses_usd": monthly_expenses,
        "monthly_income_usd": projected_income,
        "emergency_reserve_usd": emergency_reserve,
        "burn_rate_usd_per_month": burn_rate,
        "runway_months": runway_months,
        "financial_health_score": financial_health_score,
        "risk_assessment": risk_assessment,
        "debt_analysis": debt_levels,
        "recommendations": recommendations,
        "timestamp": Utc::now(),
        "risk_level": if runway_months < 3.0 {
            "HIGH"
        } else if runway_months < 6.0 {
            "MEDIUM"
        } else {
            "LOW"
        },
        "optimization_opportunities": identify_optimization_opportunities(monthly_expenses, projected_income)
    });
    
    println!("[LEX-WTH] 📈 Runway analysis complete. Months remaining: {:.1}", runway_months);
    
    Ok(BarkResponse::success(
        directive.request_id,
        TargetNode::LexWth,
        payload,
    ))
}

async fn verify_financial_metrics(directive: BarkDirective) -> Result<BarkResponse, Box<dyn std::error::Error>> {
    println!("[LEX-WTH] ✅ Verifying financial metrics...");
    
    // Simulate metric verification with audit trail
    let verification_result = json!({
        "verified": true,
        "confidence_score": 0.97,
        "data_sources_verified": [
            "bank_accounts",
            "expense_tracking",
            "investment_portfolio",
            "debt_obligations"
        ],
        "last_sync": Utc::now(),
        "anomalies_detected": 0,
        "audit_trail": {
            "balance_verified": true,
            "expenses_validated": true,
            "income_confirmed": true
        }
    });
    
    Ok(BarkResponse::success(
        directive.request_id,
        TargetNode::LexWth,
        verification_result,
    ))
}

async fn generate_financial_report(directive: BarkDirective) -> Result<BarkResponse, Box<dyn std::error::Error>> {
    println!("[LEX-WTH] 📋 Generating comprehensive financial report...");
    
    let report = json!({
        "report_type": "financial_health_analysis",
        "period": "30_days",
        "executive_summary": {
            "overall_status": "Stable",
            "runway_assessment": "Adequate",
            "key_concerns": [],
            "opportunities": ["expense_optimization", "income_diversification"]
        },
        "financial_metrics": {
            "net_worth_change": "+2.3%",
            "savings_rate": "15.2%",
            "debt_to_income_ratio": "0.15",
            "emergency_fund_months": 4.2
        },
        "projections": {
            "next_30_days": "stable",
            "next_90_days": "positive",
            "next_12_months": "growth"
        },
        "generated_at": Utc::now()
    });
    
    Ok(BarkResponse::success(
        directive.request_id,
        TargetNode::LexWth,
        report,
    ))
}

// Simulation functions for financial metrics
fn simulate_current_balance() -> f64 {
    // Simulate balance between $15,000 - $85,000
    15000.0 + (rand::random::<f64>() * 70000.0)
}

fn simulate_monthly_expenses() -> f64 {
    // Simulate monthly expenses between $2,500 - $8,000
    2500.0 + (rand::random::<f64>() * 5500.0)
}

fn simulate_monthly_income() -> f64 {
    // Simulate monthly income between $4,000 - $12,000
    4000.0 + (rand::random::<f64>() * 8000.0)
}

fn simulate_emergency_fund() -> f64 {
    // Emergency fund typically 3-6 months of expenses
    18000.0 + (rand::random::<f64>() * 42000.0)
}

fn simulate_debt_analysis() -> serde_json::Value {
    json!({
        "total_debt_usd": 15000.0 + (rand::random::<f64>() * 25000.0),
        "monthly_debt_payments": 800.0 + (rand::random::<f64>() * 1200.0),
        "debt_to_income_ratio": 0.1 + (rand::random::<f64>() * 0.3),
        "credit_score": 720 + (rand::random::<u32>() % 60) as u32,
        "interest_rates": {
            "average_apr": 4.5 + (rand::random::<f64>() * 8.0)
        }
    })
}

fn calculate_burn_rate(monthly_expenses: f64, monthly_income: f64) -> f64 {
    // Burn rate = expenses - income (positive means net outflow)
    (monthly_expenses - monthly_income).max(0.0)
}

fn calculate_runway(current_balance: f64, burn_rate: f64) -> f64 {
    // Runway calculation
    if burn_rate <= 0.0 {
        f64::INFINITY // Income >= Expenses
    } else {
        current_balance / burn_rate
    }
}

fn calculate_financial_health_score(balance: f64, runway: f64, debt: serde_json::Value) -> f64 {
    let debt_total: f64 = debt["total_debt_usd"].as_f64().unwrap_or(0.0);
    
    // Base score
    let mut score = 100.0;
    
    // Deduct for low runway
    if runway < 3.0 {
        score -= 40.0;
    } else if runway < 6.0 {
        score -= 20.0;
    } else if runway < 12.0 {
        score -= 10.0;
    }
    
    // Deduct for high debt
    let debt_ratio: f64 = debt["debt_to_income_ratio"].as_f64().unwrap_or(0.0);
    if debt_ratio > 0.5 {
        score -= 30.0;
    } else if debt_ratio > 0.3 {
        score -= 15.0;
    }
    
    // Deduct for low balance
    if balance < 10000.0 {
        score -= 20.0;
    } else if balance < 25000.0 {
        score -= 10.0;
    }
    
    score.clamp(0.0, 100.0)
}

fn assess_financial_risk(runway: f64, debt: serde_json::Value) -> String {
    let debt_ratio: f64 = debt["debt_to_income_ratio"].as_f64().unwrap_or(0.0);
    
    match (runway, debt_ratio) {
        (r, d) if r < 3.0 || d > 0.5 => "HIGH".to_string(),
        (r, d) if r < 6.0 || d > 0.3 => "MEDIUM".to_string(),
        _ => "LOW".to_string(),
    }
}

fn generate_financial_recommendations(runway: f64, burn_rate: f64, debt: serde_json::Value) -> Vec<String> {
    let mut recommendations = Vec::new();
    
    if runway < 3.0 {
        recommendations.push("URGENT: Build emergency fund immediately".to_string());
        recommendations.push("Consider expense reduction strategies".to_string());
    } else if runway < 6.0 {
        recommendations.push("Increase emergency fund to 6+ months".to_string());
    }
    
    let debt_ratio: f64 = debt["debt_to_income_ratio"].as_f64().unwrap_or(0.0);
    if debt_ratio > 0.3 {
        recommendations.push("Focus on debt reduction".to_string());
    }
    
    if burn_rate > 1000.0 {
        recommendations.push("Optimize monthly expenses".to_string());
    }
    
    recommendations.push("Continue monitoring and tracking expenses".to_string());
    recommendations
}

fn identify_optimization_opportunities(expenses: f64, income: f64) -> Vec<String> {
    let mut opportunities = Vec::new();
    
    if expenses > income * 0.8 {
        opportunities.push("Expense optimization potential identified".to_string());
    }
    
    if income < 8000.0 {
        opportunities.push("Income diversification opportunity".to_string());
    }
    
    opportunities.push("Review and optimize subscriptions".to_string());
    opportunities
}
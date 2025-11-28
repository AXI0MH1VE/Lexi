use std::process::Command;

/// Axiom Crucible v1.0 - Main Runtime
/// This binary is the entrypoint for the entire system.
/// It launches the LEX-MON router and all other nodes in isolated processes.
#[tokio::main]
async fn main() {
    println!("═══════════════════════════════════════════════════════════════");
    println!("AXIOM CRUCIBLE v1.0 (Glass Monolith)");
    println!("STATUS: KERNEL_ONLINE");
    println!("═══════════════════════════════════════════════════════════════");

    // In a real system, these would be launched inside Firecracker MicroVMs.
    // For this build, we launch them as child processes.
    println!("[CRUCIBLE] Launching LEX-MON...");
    Command::new("cargo").args(&["run", "--package", "lex-mon"]).spawn().expect("Failed to start lex-mon");

    println!("[CRUCIBLE] Launching LEX-VIT...");
    Command::new("cargo").args(&["run", "--package", "lex-vit"]).spawn().expect("Failed to start lex-vit");

    println!("[CRUCIBLE] Launching LEX-WTH...");
    Command::new("cargo").args(&["run", "--package", "lex-wth"]).spawn().expect("Failed to start lex-wth");

    println!("\n[CRUCIBLE] All nodes launched. System is standing by.");
    println!("AWAITING INPUT > _");

    // The main process would wait here, managing node health.
    // For this example, we'll let it exit while children run.
    tokio::time::sleep(tokio::time::Duration::from_secs(3600)).await;
}
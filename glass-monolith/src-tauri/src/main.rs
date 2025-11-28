#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod bark_kernel;
mod lex_bridge;

use bark_kernel::{execute_vector, KernelConfig};

fn main() {
    tauri::Builder::default()
        .manage(KernelConfig {
            enforce_zero_entropy: true,
        })
        .invoke_handler(tauri::generate_handler![execute_vector])
        .run(tauri::generate_context!())
        .expect("failed to start Glass Monolith runtime");
}

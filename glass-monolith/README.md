# Glass Monolith (LEX-7 Control Plane)

Deterministic, local-first control plane that surfaces the LEX-7 lattice as a spatial instrument, not a chat window. This skeleton maps the spec (Brand → Experience → Architecture → Code) into files you can extend.

## What’s here
- **Press + UX narrative:** baked into this README for quick briefing.
- **UI scaffold (`src-ui/`):** React + @react-three/fiber “Prism” lattice, command vector, proof card.
- **Kernel scaffold (`src-tauri/`):** Rust entrypoint with Zero-Entropy guardrail and a bridge hook for Mamba inference.

## Experience (Prism UI)
- Palette: obsidian background, phosphor white text, gold = verified, red = entropy.
- Interaction: `CMD/CTRL+K` opens the command vector; directives refract into node beams; convergence snaps into a proof card.
- Visualization: 12 temples in a ring; statuses drive emissive colors and spin while processing.

## Architecture (GMR-v1)
- Layer 1 (Chrome): Tauri + React + Three/WebGPU (fiber used here).
- Layer 2 (Lattice): Rust kernel, zero-entropy validation, bridge to Mamba (candle/mamba placeholder).
- Layer 3 (Protocol): Ed25519 signing placeholders; ready to swap in Zenoh for P2P.

## Quick start (scaffold)
1) UI: `cd glass-monolith/src-ui && npm install && npm run dev` (add @react-three/fiber, three, @tauri-apps/api).
2) Kernel: `cd glass-monolith/src-tauri && cargo tauri dev` (fill Cargo.toml with tauri-build/tauri, add ed25519, candle/mamba crates).
3) Wire: use `invoke('execute_vector', { command })` from `CommandVector.tsx`.

## Next build steps
- Implement real signature verification (ed25519) and schema validation in `bark_kernel.rs`.
- Replace the stub bridge in `lex_bridge.rs` with an actual Mamba runner (candle or Python FFI).
- Add state sync + telemetry feed to drive node statuses and proof cards from live data.

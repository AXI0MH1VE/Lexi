# Axiom Crucible — Technical Specification
*Desktop-hosted hypervisor + sovereign lattice, ready for build.*

## System Overview
- **Type:** Type-2 hypervisor app (host-managed MicroVM).
- **Host shell:** Rust (Tauri v2), zero host FS except config dir.
- **Guest:** Firecracker microVM (Alpine), Candle/Mamba runtime, Zenoh+BARK over vsock only.
- **Interface:** React + Three (Fiber) “Prism” overlay; HUD-only, no chat history.
- **Safety:** Air-gapped by default, signed BARK directives over vsock, kill-switch snapshots.

## Layered Architecture
- **Layer A — Host Shell**
  - Tauri window: transparent overlay, global hotkey, forwards keystrokes/mouse to VM via vsock.
  - Manages VM lifecycle: boot (<125ms), pause/resume, snapshot (kill switch), quota telemetry.
  - Host data: encrypted SQLite for UI prefs/keys; no project FS access.
- **Layer B — Bridge**
  - Transport: VirtIO vsock (single channel).
  - Protocol: BARK v3.1 JSON; all packets Ed25519-signed; nonce + monotonic counter.
  - Policy: allowlist message types (directive, permit_request, snapshot, heartbeat).
- **Layer C — Guest (Crucible VM)**
  - OS: Alpine/minikernel; footprint <100MB.
  - Runtime: Candle + Mamba-2 (quantized). 12 needles + 1 supervisor sharing a single wgpu device/allocator.
  - Networking: Zenoh P2P on 10.0.0.x internal only; no outbound TCP unless host grants a timed permit.
  - Workspace: isolated FS; “Coding Chamber” = ephemeral chroot/container for executing/generated code with seccomp.
  - State: per-needle persistent `h_t`, encrypted at rest; append-only audit log for directives/results.

## UI/UX Specification (Prism Overlay)
- **Visual:** Obsidian glass, refractive accents. Gold = verified, Red = entropy/error.
- **Layout:** Center lattice (12 nodes ring + router), bottom vector line (command), peripheral ghost notifications.
- **Flow:**
  1) Hotkey (`Cmd/Ctrl+Space`) summons overlay; screen dims.
  2) Input fires into router; beams refract to active nodes; live log shows node events.
  3) Output: proof card (action + signature + cost/impact) or sanitized code block.
  4) Approval (`Enter`/`Y`) sends signed directive; lattice pulses; overlay fades.
- **Ghost Stream:** Passive HUD feed of detections (e.g., OCR/screen context) with TAB-to-apply ghost text.
- **God Mode Panel:** Shows VM RAM/CPU, vsock queue depth, active permits, kill-switch (snapshot + freeze).

## Data Flow (Happy Path)
1) UI captures directive → signs → sends BARK packet over vsock.
2) Guest dispatcher validates signature/nonce → routes to supervisor.
3) Supervisor schedules needles; runs inference with cached `h_t`.
4) If code generation: send to Coding Chamber → run in sandbox → collect stdout/stderr/side-effects.
5) Validator enforces schema/sovereign rules → signs result → returns over vsock.
6) Host UI renders proof card and optional diff/ghost text.

## Security Controls
- Air-gapped default: no outbound net; permits are time-boxed and scoped.
- Keystroke biometric heartbeat (host-side) required; missing/mismatch freezes output channel.
- All directives/results signed (Ed25519); nonces prevent replay; audit log append-only (mmap + fsync).
- Kill switch: host triggers VM snapshot + pause; optional state wipe on resume.

## Build/Deploy Plan
- **Host shell:** Tauri v2 app (`src-tauri/`): vsock client, hotkey hook, overlay UI (React/Three).
- **Hypervisor manager:** Rust crate to launch Firecracker/Cloud-Hypervisor with provided kernel/rootfs, set vsock, CPU/mem caps.
- **Guest image:** Build script to assemble Alpine rootfs with candle+mamba binaries, Zenoh, sandbox tooling, and BARK daemon; output `axiom-alpine-mamba.bin` + rootfs.
- **Configs:** `lex7_architecture/axiom-crucible-config.json` as single source of truth for VM/hardware/UX defaults.

## Immediate Tasks (MVP Cut)
1) Host: implement vsock bridge + Tauri command to start/stop VM and forward signed directives.
2) Guest: BARK daemon stub that echoes signed responses; wire Zenoh disabled by default.
3) UI: render static lattice + command vector + proof card; integrate vsock invoke path.
4) Safety: add Ed25519 signing/verification in host+guest; nonce store; audit log writer.
5) Build scripts: `scripts/build_guest.sh` (or `.ps1`) to produce kernel/rootfs; `scripts/run_crucible.sh` to boot VM with vsock.

## References
- Config: `lex7_architecture/axiom-crucible-config.json`
- Host UI scaffold: `glass-monolith/src-ui/` (Prism overlay styling baseline)
- Kernel stub: `glass-monolith/src-tauri/` (bridge pattern to reuse)

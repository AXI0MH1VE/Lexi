# Lexi - Axiom Crucible

> A deterministic AI lattice system implementing zero-entropy state management with 12 specialized cognitive nodes

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Rust](https://img.shields.io/badge/rust-1.70+-orange.svg)](https://www.rust-lang.org/)

## Overview

**Lexi** is a next-generation deterministic AI system built on the Axiom Crucible architecture. It implements a 12-node hexagonal lattice topology where each node operates as an isolated, specialized cognitive unit. The system achieves zero-entropy decision-making through Mamba-2 state-space models and authenticated inter-node communication via the BARK Protocol.

### Key Features

- **🔒 Deterministic Operation**: Zero-temperature Mamba-SSM ensures 100% reproducible state transitions
- **🌐 Lattice Topology**: 12-node hexagonal architecture with central coordination
- **🔐 Cryptographic Authentication**: Ed25519-signed BARK Protocol for all inter-node communication
- **⚡ Isolated Execution**: Each node runs in Firecracker microVMs for security and performance
- **🎯 Specialized Nodes**: Domain-specific cognitive units (Vitality, Wealth, Knowledge, Strategy, etc.)
- **💎 Glass Monolith UI**: Tauri-based desktop interface with React + Three.js visualization
- **📊 Immutable Ledger**: State convergence tracking with human validation workflows

## Architecture

### The 12-Node Lattice

Lexi's cognitive architecture consists of 12 specialized nodes arranged in a hexagonal lattice:

| Node | Purpose | Status |
|------|---------|--------|
| **LEX-MON** | Central coordination router, directive orchestration | ✅ Operational |
| **LEX-VIT** | Vitality monitoring, bio-state analysis | ✅ Operational |
| **LEX-WTH** | Financial analysis, wealth management | ✅ Operational |
| **LEX-ENT** | Strategic enterprise planning, pivot analysis | ✅ Operational |
| **LEX-KNO** | Knowledge processing, information synthesis | ✅ Operational |
| **LEX-CRT** | Content creation, output generation | 🔄 In Development |
| **LEX-ORD** | Logistics coordination, operational planning | ✅ Operational |
| **LEX-KIN** | Social relationship management, network analysis | 🔄 In Development |
| **LEX-GRW** | Learning and growth, capability development | 🔄 In Development |
| **LEX-SAN** | Environmental monitoring, infrastructure management | 🔄 In Development |
| **LEX-LEI** | Leisure and recovery, restoration planning | 🔄 In Development |
| **LEX-OUT** | Communication outreach, influence management | 🔄 In Development |

### Core Components

#### BARK Protocol v3.1
Authenticated messaging system featuring:
- Directive-based communication (ANALYZE, GENERATE, VERIFY, EXECUTE_PLAN)
- Ed25519 cryptographic signing for message authenticity
- JSON serialization with canonical construction
- Response status tracking (Success, Failure, Pending, Rejected)

#### Mamba-SSM State Management
Deterministic state-space model implementation:
```
h_t = A × h_(t-1) + B × u_t
```
- Temperature = 0.0 (zero-entropy operation)
- Convergence detection with immutable ledger commits
- Node-specific state initialization vectors
- State similarity calculations for decision-making

#### Firecracker MicroVM Orchestration
- Isolated execution environment per node
- Resource allocation based on node requirements
- Inter-VM communication via vsock or shared memory
- Health monitoring and lifecycle management

#### Glass Monolith UI
- Transparent Tauri desktop application (800x600)
- Real-time 3D lattice visualization with Three.js
- Node status indicators and health metrics
- Directive flow animations and state convergence displays

## Installation

For detailed installation instructions, see [INSTALL.md](INSTALL.md).

### Quick Start

**Prerequisites:**
- Python 3.12+
- Rust 1.70+
- Node.js 18+
- (Optional) CUDA toolkit for GPU acceleration

**Setup:**
```bash
# Clone the repository
git clone https://github.com/AXI0MH1VE/Lexi.git
cd Lexi

# Run setup scripts (Windows)
setup_venv.bat
install_deps.bat
install_torch.bat

# Run setup script (Unix/Linux)
./optimize.sh

# Launch the system
cargo run
```

## Usage

Once the system is running, the Glass Monolith UI will display the 12-node lattice with real-time status updates.

### Sending Directives

Interact with nodes by sending BARK Protocol directives:

```rust
let directive = Directive {
    id: Uuid::new_v4(),
    timestamp: Utc::now(),
    sender: "LEX-MON".to_string(),
    recipient: "LEX-ENT".to_string(),
    action: DirectiveAction::Analyze,
    payload: json!({"query": "strategic pivot analysis"}),
};
```

### Node Communication Flow

1. User interaction → UI component → Tauri IPC → Kernel
2. Kernel creates signed BARK directive → Routes to target node(s)
3. Node processes directive → Updates Mamba-SSM state
4. Response synthesis → UI visualization update
5. Convergence detection → Immutable ledger commit (if required)

## Development

For contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

### Project Structure

```
Lexi/
├── nodes/              # 12 specialized node implementations
├── shared/             # Cross-node shared libraries
│   ├── communication/  # BARK Protocol implementation
│   ├── state/          # Mamba-SSM state management
│   └── models/         # Mamba-2 model implementations
├── kernel/             # Tauri + Rust core runtime
├── glass-monolith-ui/  # React + Three.js interface
├── firecracker/        # MicroVM orchestration
├── deployment/         # Hardware-specific optimizations
└── tests/              # Integration and communication tests
```

### Running Tests

```bash
# Run all tests
cargo test

# Run specific test suite
cargo test inter_node_communication

# Run with output
cargo test -- --nocapture
```

## Roadmap

See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for detailed implementation phases.

**Current Status:** Phase 2 Complete ✅

- [x] Phase 1: Core Infrastructure (BARK Protocol, Mamba-SSM, Tauri setup)
- [x] Phase 2: Critical Nodes (MON, VIT, WTH, ENT, KNO, ORD)
- [ ] Phase 3: Glass Monolith UI (In Progress)
- [ ] Phase 4: Additional Nodes (CRT, KIN, GRW, SAN, LEI, OUT, LEG)
- [ ] Phase 5: Advanced Features (MicroVM isolation, Zenoh P2P, ML integration)

## Documentation

- **[structure.md](structure.md)** - Complete architecture documentation
- **[IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)** - Development roadmap and status
- **[axiom_crucible_roadmap.md](axiom_crucible_roadmap.md)** - Strategic roadmap
- **[API.md](API.md)** - BARK Protocol and node interface documentation

## Technical Specifications

### Dependencies

**Rust Ecosystem:**
- `tauri` - Desktop application framework
- `tokio` - Async runtime
- `serde` - Serialization
- `ed25519-dalek` - Cryptographic signing
- `uuid` - Unique identifiers
- `chrono` - Time handling

**Frontend:**
- `react` - UI framework
- `three.js` - 3D visualization
- `@tauri-apps/api` - IPC communication

**System:**
- Firecracker - MicroVM runtime (optional)
- CUDA/TensorRT - GPU acceleration (optional)
- Metal/CoreML - Apple Silicon optimization (optional)

### Performance

- **Response Time**: <50ms deterministic latency
- **State Transitions**: Zero-entropy (temperature = 0.0)
- **Memory Footprint**: Optimized for minimal hardware requirements
- **Scalability**: 12 concurrent node operations

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on the principles of deterministic AI and zero-knowledge machine learning
- Implements Mamba-2 state-space models for reproducible cognition
- Inspired by distributed systems architecture and cognitive neuroscience

## Contact

- **GitHub**: [@AXI0MH1VE](https://github.com/AXI0MH1VE)
- **Project**: [Lexi - Axiom Crucible](https://github.com/AXI0MH1VE/Lexi)

---

**Note**: This is an experimental research project. The system is under active development and APIs may change.

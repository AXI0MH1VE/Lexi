# LEX-7 Architecture Directory Structure

## Overview
The LEX-7 Architecture follows a distributed swarm topology with specialized nodes (LEX-VIT, LEX-WTH, LEX-MON) that communicate through shared protocols. The directory structure supports modular development, shared resources, and hardware-specific deployments.

## Directory Tree

```
lex7/
├── nodes/                    # Individual node implementations
│   ├── lex-vit/             # Vision processing node
│   ├── lex-wth/             # Weather/environmental node
│   └── lex-mon/             # Monitoring/coordination node
├── shared/                  # Common components across nodes
│   ├── models/              # Shared AI/ML models
│   ├── datasets/            # Training and reference datasets
│   └── communication/       # Inter-node communication protocols
├── runtime/                 # Runtime environments and wrappers
│   ├── rust/                # Rust runtime components
│   └── tauri/               # Tauri desktop application wrappers
└── deployment/              # Hardware-specific deployment configs
    ├── apple-silicon/       # Apple Silicon GPU optimizations
    └── nvidia-gpu/          # NVIDIA GPU optimizations
```

## Directory Descriptions

### nodes/
Contains the implementation for each swarm node:
- **lex-vit/**: Handles computer vision tasks, image processing, and visual data analysis
- **lex-wth/**: Manages environmental data, weather patterns, and external sensor inputs
- **lex-mon/**: Coordinates swarm activities, monitors node health, and manages distributed state

### shared/
Reusable components that support multiple nodes:
- **models/**: Pre-trained models, model weights, and inference engines
- **datasets/**: Shared datasets for training, validation, and benchmarking
- **communication/**: Message protocols, serialization formats, and network interfaces

### runtime/
Execution environments for the swarm:
- **rust/**: Core runtime logic, performance-critical components, and system interfaces
- **tauri/**: Desktop application wrappers for local deployment and user interfaces

### deployment/
Hardware-specific optimizations and configurations:
- **apple-silicon/**: Metal shaders, Core ML integrations, and Apple-specific optimizations
- **nvidia-gpu/**: CUDA kernels, TensorRT optimizations, and NVIDIA-specific configurations

## Usage Guidelines
- Each node directory should contain its own source code, configuration files, and node-specific assets
- Shared components should be designed for cross-node compatibility and reusability
- Runtime environments should provide consistent interfaces across different hardware platforms
- Deployment directories should contain platform-specific build scripts, dependencies, and optimization settings
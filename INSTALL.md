# Installation Guide - Lexi (Axiom Crucible)

This guide provides detailed instructions for installing and setting up the Lexi - Axiom Crucible system on Windows, macOS, and Linux.

## Table of Contents

- [System Requirements](#system-requirements)
- [Prerequisites](#prerequisites)
- [Windows Installation](#windows-installation)
- [macOS Installation](#macos-installation)
- [Linux Installation](#linux-installation)
- [GPU Acceleration Setup](#gpu-acceleration-setup)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements

- **CPU**: 4+ cores (Intel/AMD x86_64 or ARM64)
- **RAM**: 8 GB minimum, 16 GB recommended
- **Storage**: 10 GB free space
- **OS**: Windows 10+, macOS 12+, or Linux (Ubuntu 20.04+, Debian 11+, Fedora 35+)

### Recommended Requirements

- **CPU**: 8+ cores
- **RAM**: 32 GB
- **GPU**: NVIDIA GPU with CUDA support (optional but recommended)
- **Storage**: 20 GB SSD

### Software Prerequisites

- **Python**: 3.12 or higher
- **Rust**: 1.70 or higher
- **Node.js**: 18.0 or higher (for UI development)
- **Git**: Latest version

## Prerequisites

Install the following tools before proceeding:

### Install Python 3.12+

**Windows:**
```powershell
# Download from python.org or use winget
winget install Python.Python.3.12
```

**macOS:**
```bash
# Using Homebrew
brew install python@3.12
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip
```

### Install Rust

All platforms:
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env  # Unix/macOS
# Restart terminal on Windows
```

Verify installation:
```bash
rustc --version
cargo --version
```

### Install Node.js (Optional - for UI development)

**Windows:**
```powershell
winget install OpenJS.NodeJS.LTS
```

**macOS:**
```bash
brew install node
```

**Linux:**
```bash
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt install -y nodejs
```

## Windows Installation

### Step 1: Clone the Repository

```powershell
git clone https://github.com/AXI0MH1VE/Lexi.git
cd Lexi
```

### Step 2: Set Up Python Environment

```batch
# Create and activate virtual environment
setup_venv.bat

# The script will:
# - Create a Python virtual environment
# - Activate it automatically
```

### Step 3: Install Python Dependencies

```batch
# Install required Python packages
install_deps.bat

# This installs:
# - numpy, torch, mamba-ssm
# - zenoh, cryptography
# - Other dependencies from requirements.txt
```

### Step 4: Install PyTorch (GPU Support)

```batch
# For NVIDIA GPU with CUDA support
install_torch.bat

# For CPU-only installation
pip install torch torchvision torchaudio
```

### Step 5: Build Rust Components

```powershell
# Build all Rust components
cargo build --release

# This compiles:
# - BARK Protocol communication layer
# - Mamba-SSM state management
# - Node implementations
# - Tauri kernel
```

### Step 6: Build UI (Optional)

If you're working on the Glass Monolith UI:

```powershell
cd glass-monolith-ui
npm install
npm run build
cd ..
```

### Step 7: Run Initial Tests

```powershell
# Run test suite
run_test.bat

# Or use cargo directly
cargo test
```

## macOS Installation

### Step 1: Install Xcode Command Line Tools

```bash
xcode-select --install
```

### Step 2: Clone the Repository

```bash
git clone https://github.com/AXI0MH1VE/Lexi.git
cd Lexi
```

### Step 3: Run Optimization Script

```bash
# Make script executable
chmod +x optimize.sh

# Run optimization and setup
./optimize.sh

# This script will:
# - Set up Python virtual environment
# - Install Python dependencies
# - Build Rust components with optimizations
# - Configure Metal/CoreML acceleration (Apple Silicon)
```

### Step 4: Install Additional Dependencies

For Python packages:

```bash
source venv/bin/activate  # Activate virtual environment
pip install -r requirements.txt
```

### Step 5: Build with Apple Silicon Optimization (M1/M2/M3)

```bash
# Enable Metal acceleration
export PYTORCH_ENABLE_MPS_FALLBACK=1

# Build with Metal support
cargo build --release --features metal
```

### Step 6: Run Tests

```bash
cargo test --release
```

## Linux Installation

### Step 1: Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y build-essential pkg-config libssl-dev \
    python3-dev python3-venv git curl
```

**Fedora/RHEL:**
```bash
sudo dnf groupinstall "Development Tools"
sudo dnf install openssl-devel python3-devel git curl
```

**Arch Linux:**
```bash
sudo pacman -S base-devel openssl python git curl
```

### Step 2: Clone the Repository

```bash
git clone https://github.com/AXI0MH1VE/Lexi.git
cd Lexi
```

### Step 3: Run Optimization Script

```bash
chmod +x optimize.sh
./optimize.sh
```

### Step 4: Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5: Build Rust Components

```bash
# Standard build
cargo build --release

# With specific optimizations
RUSTFLAGS="-C target-cpu=native" cargo build --release
```

### Step 6: Run Tests

```bash
cargo test --release
```

## GPU Acceleration Setup

### NVIDIA CUDA Setup

#### Install CUDA Toolkit

**Ubuntu/Debian:**
```bash
# Add NVIDIA package repositories
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt update
sudo apt install cuda
```

**Windows:**
- Download CUDA Toolkit from NVIDIA website
- Install with default settings
- Add CUDA to PATH

#### Install PyTorch with CUDA Support

```bash
source venv/bin/activate  # Unix/macOS
# venv\Scripts\activate  # Windows

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### Verify CUDA Installation

```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
print(f"GPU count: {torch.cuda.device_count()}")
```

### Apple Silicon (Metal) Setup

For M1/M2/M3 Macs:

```bash
# PyTorch with MPS (Metal Performance Shaders)
pip install torch torchvision torchaudio

# Verify Metal support
python -c "import torch; print(f'MPS available: {torch.backends.mps.is_available()}')"
```

## Verification

Verify your installation:

### 1. Check Component Versions

```bash
# Python version
python --version  # Should be 3.12+

# Rust version
rustc --version  # Should be 1.70+

# Cargo version
cargo --version

# Node version (if installed)
node --version  # Should be 18+
```

### 2. Run Test Suite

```bash
# All tests
cargo test --release

# Specific test categories
cargo test communication  # BARK Protocol tests
cargo test state          # Mamba-SSM tests
cargo test nodes          # Node implementation tests
```

### 3. Launch the System

```bash
# Run in development mode
cargo run

# Run optimized release build
cargo run --release
```

You should see:
```
[INFO] Initializing Axiom Crucible...
[INFO] Loading BARK Protocol v3.1...
[INFO] Starting Mamba-SSM state management...
[INFO] Launching nodes: LEX-MON, LEX-VIT, LEX-WTH, LEX-ENT, LEX-KNO, LEX-ORD
[INFO] Glass Monolith UI starting on port 1420
[INFO] System ready.
```

### 4. Access the UI

Open your browser to:
```
http://localhost:1420
```

You should see the Glass Monolith interface with the 12-node lattice visualization.

## Troubleshooting

### Common Issues

#### Issue: "rustc version too old"

**Solution:**
```bash
rustup update stable
rustup default stable
```

#### Issue: "Python version mismatch"

**Solution:**
```bash
# Specify Python version explicitly
python3.12 -m venv venv
```

#### Issue: "CUDA not found" (NVIDIA GPU)

**Solution:**
1. Verify CUDA installation: `nvcc --version`
2. Check PATH includes CUDA bin directory
3. Reinstall PyTorch with correct CUDA version:
   ```bash
   pip install torch --index-url https://download.pytorch.org/whl/cu118
   ```

#### Issue: "mamba_ssm build fails"

**Solution:**
```bash
# Install build dependencies
# Ubuntu/Debian:
sudo apt install ninja-build

# macOS:
brew install ninja

# Retry installation
pip install mamba-ssm --no-cache-dir
```

#### Issue: "Cargo build fails with linker errors"

**Solution:**

**Windows:**
- Install Visual Studio Build Tools
- Install Windows SDK

**Linux:**
```bash
sudo apt install build-essential pkg-config libssl-dev
```

**macOS:**
```bash
xcode-select --install
```

#### Issue: "Node not found" (frontend build)

**Solution:**
```bash
# Reinstall Node.js
# Use nvm (Node Version Manager)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18
```

### Performance Issues

#### Slow Build Times

```bash
# Use more CPU cores for compilation
export CARGO_BUILD_JOBS=8
cargo build --release
```

#### High Memory Usage

```bash
# Reduce parallel jobs
cargo build --release -j 2
```

### Getting Help

1. **Check Documentation**:
   - [README.md](README.md) - Project overview
   - [structure.md](structure.md) - Architecture details
   - [CONTRIBUTING.md](CONTRIBUTING.md) - Development guidelines

2. **Search Issues**: Check [GitHub Issues](https://github.com/AXI0MH1VE/Lexi/issues)

3. **Open an Issue**: Create a new issue with:
   - System information (OS, versions)
   - Full error message
   - Steps to reproduce

## Next Steps

After successful installation:

1. Read the [README.md](README.md) for system overview
2. Review [structure.md](structure.md) for architecture details
3. Check [CONTRIBUTING.md](CONTRIBUTING.md) if you want to contribute
4. Explore the codebase and node implementations
5. Run the test suite to verify functionality

## Uninstallation

To remove Lexi:

```bash
# Remove repository
cd ..
rm -rf Lexi

# Remove Python virtual environment (if outside repo)
rm -rf venv

# Rust components are self-contained in the repository
```

---

**Note**: This system is under active development. Installation procedures may change. Always refer to the latest documentation in the repository.

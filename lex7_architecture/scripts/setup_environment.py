#!/usr/bin/env python3
"""
LEX-7 Architecture Environment Setup Script
Sets up Python/PyTorch environment with Mamba-SSM dependencies
"""

import subprocess
import sys
import platform
import os
import yaml
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return None

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required, got {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_pytorch_installation():
    """Check PyTorch installation and GPU availability"""
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__} installed")
        
        if torch.cuda.is_available():
            print(f"✅ CUDA available: {torch.cuda.get_device_name(0)}")
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            print("✅ Apple Silicon MPS available")
        else:
            print("ℹ️  Using CPU mode")
        
        return True
    except ImportError:
        print("❌ PyTorch not found")
        return False

def check_mamba_ssm():
    """Check Mamba-SSM installation"""
    try:
        import mamba_ssm
        print(f"✅ Mamba-SSM {mamba_ssm.__version__} installed")
        return True
    except ImportError:
        print("❌ Mamba-SSM not found - will need to install")
        return False

def setup_virtual_environment():
    """Create and activate virtual environment"""
    venv_path = Path("venv")
    
    if not venv_path.exists():
        run_command(f"{sys.executable} -m venv venv", "Creating virtual environment")
    
    # Get appropriate activate script
    if platform.system() == "Windows":
        activate_script = venv_path / "Scripts" / "activate.bat"
        python_path = venv_path / "Scripts" / "python.exe"
    else:
        activate_script = venv_path / "bin" / "activate"
        python_path = venv_path / "bin" / "python"
    
    return python_path

def install_dependencies():
    """Install required dependencies"""
    requirements = Path("requirements.txt")
    if not requirements.exists():
        print("❌ requirements.txt not found")
        return False
    
    # Install dependencies
    result = run_command(
        f"{sys.executable} -m pip install -r {requirements}",
        "Installing Python dependencies"
    )
    
    return result is not None

def create_config_template():
    """Create additional configuration files"""
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    # Create default node configuration template
    node_config = {
        "node_id": "lex_node_001",
        "node_type": "core",
        "state_vector_path": "data/state/node_state.pt",
        "sovereign_directives_path": "data/axioms/",
        "communication": {
            "protocol": "bark_zenoh",
            "discovery_enabled": True,
            "message_handling": "asynchronous"
        },
        "error_model": {
            "method": "kalman_filter",
            "parameters": {
                "convergence_threshold": 0.01,
                "max_iterations": 100
            }
        }
    }
    
    config_path = config_dir / "node_config.yaml"
    with open(config_path, 'w') as f:
        yaml.dump(node_config, f, default_flow_style=False)
    
    print(f"✅ Created node configuration template: {config_path}")
    
    return True

def main():
    """Main setup function"""
    print("🚀 Starting LEX-7 Architecture Environment Setup")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check PyTorch
    if not check_pytorch_installation():
        print("💡 Installing PyTorch...")
        install_pytorch = input("Install PyTorch? (y/n): ").lower().strip()
        if install_pytorch == 'y':
            run_command(
                f"{sys.executable} -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu",
                "Installing PyTorch"
            )
    
    # Check Mamba-SSM
    if not check_mamba_ssm():
        print("💡 Mamba-SSM will be installed with other dependencies")
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Create configuration
    create_config_template()
    
    # Final check
    print("\n" + "=" * 60)
    print("🔍 Final System Check...")
    
    final_checks = [
        check_python_version,
        check_pytorch_installation,
        check_mamba_ssm
    ]
    
    all_passed = True
    for check in final_checks:
        if not check():
            all_passed = False
    
    if all_passed:
        print("\n🎉 LEX-7 Environment Setup Complete!")
        print("Ready to begin Lex-Mamba Node implementation")
        return True
    else:
        print("\n⚠️  Setup completed with warnings. Check output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

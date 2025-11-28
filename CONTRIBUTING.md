# Contributing to Lexi - Axiom Crucible

Thank you for your interest in contributing to Lexi! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

This project operates under principles of respect, collaboration, and technical excellence. All contributors are expected to:

- Maintain professional and constructive communication
- Focus on deterministic outcomes and reproducible results
- Respect the architectural principles of the Axiom Crucible system
- Provide clear, well-documented code changes
- Help others learn and grow

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Python 3.12+** installed
- **Rust 1.70+** with cargo
- **Node.js 18+** for frontend development
- **Git** for version control
- Familiarity with async/await patterns in Rust
- Understanding of deterministic state machines

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Lexi.git
   cd Lexi
   ```
3. Add the upstream remote:
   ```bash
   git remote add upstream https://github.com/AXI0MH1VE/Lexi.git
   ```

## Development Setup

### Windows Setup

```batch
# Set up Python virtual environment
setup_venv.bat

# Install Python dependencies
install_deps.bat

# Install PyTorch (if using GPU acceleration)
install_torch.bat

# Build Rust components
cargo build
```

### Unix/Linux/macOS Setup

```bash
# Run optimization script
./optimize.sh

# Build Rust components
cargo build

# Set up frontend (if working on UI)
cd glass-monolith-ui
npm install
```

### Running Tests

```bash
# Run all Rust tests
cargo test

# Run specific test suite
cargo test inter_node_communication

# Run with output
cargo test -- --nocapture

# Run Python tests (if applicable)
python -m pytest tests/
```

## Project Structure

Understand the architecture before contributing:

```
Lexi/
├── nodes/              # 12 specialized node implementations
│   ├── lex-mon/       # Central coordinator
│   ├── lex-vit/       # Vitality monitoring
│   └── ...
├── shared/            # Cross-node libraries
│   ├── communication/ # BARK Protocol
│   ├── state/         # Mamba-SSM state management
│   └── models/        # Mamba-2 implementations
├── kernel/            # Tauri core runtime
├── glass-monolith-ui/ # React + Three.js UI
└── tests/             # Integration tests
```

## Coding Standards

### Rust Code Style

- Follow standard Rust formatting (`cargo fmt`)
- Use `cargo clippy` to catch common mistakes
- Prefer explicit types over type inference in public APIs
- Document all public functions and modules
- Use `async/await` for all I/O operations

**Example:**

```rust
/// Processes a BARK Protocol directive and returns a response.
///
/// # Arguments
/// * `directive` - The incoming directive to process
///
/// # Returns
/// A Result containing the response or an error
pub async fn process_directive(
    directive: &Directive,
) -> Result<Response, ProcessError> {
    // Implementation
}
```

### Python Code Style

- Follow PEP 8 guidelines
- Use type hints for all function signatures
- Document functions with docstrings
- Keep functions focused and single-purpose

**Example:**

```python
def analyze_state_vector(
    state: np.ndarray,
    threshold: float = 0.95
) -> Dict[str, Any]:
    """
    Analyze a Mamba-SSM state vector for convergence.
    
    Args:
        state: The state vector to analyze
        threshold: Convergence threshold (default: 0.95)
    
    Returns:
        Dictionary containing analysis results
    """
    # Implementation
```

### JavaScript/TypeScript Style

- Use TypeScript for all new code
- Follow Airbnb style guide
- Use functional components with hooks
- Document complex functions with JSDoc

## Commit Guidelines

We follow conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, no logic change)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks
- **perf**: Performance improvements

### Examples

```bash
# Good commits
feat(nodes): add LEX-CRT content creation node
fix(bark): correct signature verification for Ed25519
docs(readme): update installation instructions for macOS
refactor(state): optimize Mamba-SSM convergence detection

# Bad commits
fixed stuff
update
WIP
```

### Scope Guidelines

- **nodes**: Node implementations (LEX-MON, LEX-VIT, etc.)
- **bark**: BARK Protocol communication
- **state**: Mamba-SSM state management
- **ui**: Glass Monolith UI components
- **kernel**: Tauri core runtime
- **tests**: Test suite changes
- **docs**: Documentation

## Pull Request Process

### Before Submitting

1. **Test your changes**: Ensure all tests pass
2. **Update documentation**: Add/update docs for new features
3. **Follow style guidelines**: Run formatters and linters
4. **Write clear commits**: Follow commit guidelines
5. **Update CHANGELOG** (if applicable)

### Submitting a PR

1. Push your changes to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Create a pull request on GitHub with:
   - **Clear title**: Following conventional commits format
   - **Description**: What changes were made and why
   - **Testing**: How you tested the changes
   - **Related issues**: Link any related issues

3. Wait for review and address feedback

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe how you tested these changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] Commit messages follow guidelines
```

## Testing

### Unit Tests

Write unit tests for all new functionality:

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_directive_processing() {
        // Test implementation
    }
}
```

### Integration Tests

Place integration tests in the `tests/` directory:

```rust
// tests/inter_node_communication_test.rs
#[tokio::test]
async fn test_lex_mon_routing() {
    // Test implementation
}
```

### Test Coverage

- Aim for >80% code coverage
- Focus on critical paths and edge cases
- Test deterministic behavior thoroughly
- Verify signature validation in BARK Protocol

## Documentation

### Code Documentation

- Document all public APIs
- Include examples in documentation
- Explain complex algorithms
- Document assumptions and constraints

### Architecture Documentation

When adding significant features:

1. Update `structure.md` with architectural changes
2. Add diagrams if helpful (Mermaid format preferred)
3. Document integration points
4. Update `IMPLEMENTATION_PLAN.md` progress

### API Documentation

For BARK Protocol or node interface changes:

1. Update `API.md` with new endpoints/directives
2. Include request/response examples
3. Document error cases
4. Specify version compatibility

## Node Development Guidelines

### Creating a New Node

When implementing a new LEX node:

1. **Create node directory**: `nodes/lex-XXX/`
2. **Implement core trait**: Extend `Node` trait
3. **Define directives**: Specify supported actions
4. **State management**: Integrate Mamba-SSM
5. **Add tests**: Unit and integration tests
6. **Document**: Add node documentation

### Node Template

```rust
use shared::communication::bark::*;
use shared::state::mamba_ssm::*;

pub struct LexXXX {
    state_manager: StateManager,
    // Node-specific fields
}

impl LexXXX {
    pub fn new() -> Self {
        Self {
            state_manager: StateManager::new("lex-xxx"),
        }
    }

    pub async fn process_directive(
        &mut self,
        directive: &Directive,
    ) -> Result<Response, ProcessError> {
        // Implementation
    }
}
```

## BARK Protocol Changes

When modifying the BARK Protocol:

1. **Version bump**: Update protocol version if incompatible
2. **Maintain compatibility**: Support older versions when possible
3. **Update schema**: Document message format changes
4. **Test signatures**: Verify Ed25519 signing/verification
5. **Update docs**: Reflect changes in API.md

## Questions and Support

For questions:

- **Issues**: Open a GitHub issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for general questions
- **Documentation**: Check existing docs first (structure.md, API.md)

## Recognition

Contributors will be recognized in:

- Project README
- Release notes
- Git commit history

Thank you for contributing to Lexi and advancing deterministic AI systems!

---

**Note**: This is an experimental research project. Contributions should maintain the deterministic, zero-entropy principles that define the Axiom Crucible architecture.

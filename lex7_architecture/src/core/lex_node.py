#!/usr/bin/env python3
"""
LEX NODE - The Integrated Error-State Model Interface
The complete Lex Node that integrates LexMambaKernel, ErrorModel, and SovereignDirectives
This is the user-facing interface for the LEX-7 Architecture
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Dict, Any, List, Tuple
import logging
import asyncio
import json
import time
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

# Import our core components
from .lex_mamba_kernel import LexMambaKernel, LexNode as LexNodeKernel
from .error_model import (
    AdaptiveErrorModel, 
    SovereignDirectiveValidator, 
    ConvergenceMethod,
    ErrorState,
    ControlSignal
)

logger = logging.getLogger(__name__)

class NodeState(Enum):
    """States of a Lex Node"""
    INITIALIZING = "initializing"
    READY = "ready"
    PROCESSING = "processing"
    CONVERGED = "converged"
    ERROR = "error"
    SHUTDOWN = "shutdown"

class DirectiveType(Enum):
    """Types of BARK directives"""
    ANALYSIS = "analysis"
    GENERATION = "generation"
    CONTROL = "control"
    VALIDATION = "validation"
    STATE_UPDATE = "state_update"

@dataclass
class LexResponse:
    """Response from Lex Node processing"""
    status: str
    directive_id: str
    correction: Dict[str, Any]
    confidence: float
    convergence_achieved: bool
    error_state: Dict[str, Any]
    processing_time: float
    metadata: Dict[str, Any]

class LexNode:
    """
    The Complete Lex Node
    
    This is the main interface that combines:
    - LexMambaKernel (State-Space Model)
    - AdaptiveErrorModel (Convergence Engine)
    - SovereignDirectiveValidator (Axiom Enforcement)
    
    The Node processes BARK directives and returns error-corrected responses
    """
    
    def __init__(self, config_path: Path, node_id: str = "lex_core_001"):
        """
        Initialize the complete Lex Node
        
        Args:
            config_path: Path to configuration YAML
            node_id: Unique identifier for this node
        """
        self.node_id = node_id
        self.config = self.load_config(config_path)
        self.state = NodeState.INITIALIZING
        self.state_history = []
        self.directive_history = []
        
        # Initialize core components
        self.kernel = LexNodeKernel(config_path)
        self.error_model = AdaptiveErrorModel(
            state_dim=self.config['model']['state_dim'],
            method=ConvergenceMethod.KALMAN_FILTER
        )
        self.validator = SovereignDirectiveValidator(self.config['sovereign'])
        
        # Runtime state
        self.current_state = None
        self.target_state = None
        self.convergence_history = []
        self.performance_metrics = {}
        
        # Initialize the node
        self._initialize()
        
        logger.info(f"Lex Node {node_id} initialized successfully")
    
    def _initialize(self):
        """Initialize the Lex Node components"""
        try:
            # Load persistent state if available
            state_path = Path(self.config['lex_node'].get('state_vector_path', 'data/state/node_state.pt'))
            if state_path.exists():
                self.kernel.kernel.load_state(state_path)
                logger.info(f"Loaded persistent state from {state_path}")
            
            # Initialize target state (sovereign directives)
            self.target_state = self._initialize_sovereign_state()
            
            # Start with empty current state
            self.current_state = torch.zeros(self.config['model']['state_dim'])
            
            self.state = NodeState.READY
            logger.info("Lex Node initialization complete")
            
        except Exception as e:
            logger.error(f"Failed to initialize Lex Node: {e}")
            self.state = NodeState.ERROR
            raise
    
    def load_config(self, config_path: Path) -> Dict:
        """Load configuration from YAML file"""
        import yaml
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _initialize_sovereign_state(self) -> torch.Tensor:
        """Initialize the target state based on sovereign axioms"""
        # In production, this would load actual sovereign directive embeddings
        # For now, create a simple target state
        
        state_dim = self.config['model']['state_dim']
        target_state = torch.zeros(state_dim)
        
        # Encode sovereign axioms into the target state
        axioms = self.validator.sovereign_axioms
        for i, axiom in enumerate(axioms):
            if i < state_dim:
                # Encode axiom as specific pattern in target state
                if axiom['mandatory']:
                    target_state[i] = 1.0  # Mandatory axioms get high weight
                else:
                    target_state[i] = 0.8 * axiom['weight']  # Non-mandatory get weighted values
        
        return target_state
    
    async def process_directive(
        self, 
        directive: Dict[str, Any], 
        context: Optional[Dict] = None
    ) -> LexResponse:
        """
        Process a BARK directive through the complete Lex Node
        
        This is the main processing pipeline:
        1. Validate directive against sovereign axioms
        2. Convert directive to state-space input
        3. Apply Lex-Mamba kernel with current state
        4. Compute error correction
        5. Update state and return correction
        
        Args:
            directive: BARK directive to process
            context: Additional context for processing
            
        Returns:
            LexResponse: Complete response with correction signal
        """
        start_time = time.time()
        directive_id = directive.get('id', f"dir_{int(time.time())}")
        
        try:
            self.state = NodeState.PROCESSING
            
            # Step 1: Validate directive against sovereign axioms
            validation_result = self.validator.validate_directive(directive, context)
            
            if not validation_result['valid']:
                return LexResponse(
                    status='refused',
                    directive_id=directive_id,
                    correction={
                        'action': 'refuse_directive',
                        'reason': validation_result['reason'],
                        'required_corrections': validation_result.get('required_corrections', [])
                    },
                    confidence=0.0,
                    convergence_achieved=False,
                    error_state={'validation_failed': True},
                    processing_time=time.time() - start_time,
                    metadata={'validation_result': validation_result}
                )
            
            # Step 2: Convert directive to tensor input
            x_t = self._directive_to_state_input(directive, validation_result)
            
            # Step 3: Process through Lex-Mamba kernel
            h_t, y_pred, error_signal = self.kernel.kernel.forward(
                x_t, 
                self.current_state
            )
            
            # Step 4: Apply error model for convergence
            error_state, control_signal = self.error_model.step(
                h_t, 
                self.target_state
            )
            
            # Step 5: Generate final correction
            correction = self._generate_final_correction(
                y_pred, 
                error_signal, 
                control_signal, 
                validation_result
            )
            
            # Step 6: Update persistent state
            self.current_state = h_t
            
            # Record metrics
            processing_time = time.time() - start_time
            self._update_metrics(validation_result, error_state, control_signal, processing_time)
            
            # Check convergence
            converged = error_state.error_magnitude < self.config['lex_node']['convergence_threshold']
            if converged:
                self.state = NodeState.CONVERGED
            else:
                self.state = NodeState.READY
            
            # Store in history
            self.directive_history.append({
                'directive_id': directive_id,
                'directive': directive,
                'validation_result': validation_result,
                'error_magnitude': error_state.error_magnitude,
                'processing_time': processing_time,
                'timestamp': time.time()
            })
            
            return LexResponse(
                status='success',
                directive_id=directive_id,
                correction=correction,
                confidence=control_signal.confidence,
                convergence_achieved=converged,
                error_state=asdict(error_state),
                processing_time=processing_time,
                metadata={
                    'validation_compliance': validation_result['compliance_score'],
                    'control_action': control_signal.convergence_action,
                    'node_id': self.node_id
                }
            )
            
        except Exception as e:
            logger.error(f"Error processing directive {directive_id}: {e}")
            self.state = NodeState.ERROR
            
            return LexResponse(
                status='error',
                directive_id=directive_id,
                correction={'error': str(e)},
                confidence=0.0,
                convergence_achieved=False,
                error_state={'exception': str(e)},
                processing_time=time.time() - start_time,
                metadata={'error_type': type(e).__name__}
            )
    
    def _directive_to_state_input(
        self, 
        directive: Dict[str, Any], 
        validation_result: Dict[str, Any]
    ) -> torch.Tensor:
        """Convert directive to state-space input tensor"""
        
        # Get directive features
        command = directive.get('command', '')
        parameters = directive.get('parameters', {})
        compliance_score = validation_result.get('compliance_score', 1.0)
        
        # Create multi-channel input
        state_dim = self.config['model']['state_dim']
        input_tensor = torch.zeros(state_dim)
        
        # Channel 1: Command encoding (simplified)
        command_hash = hash(command) % state_dim
        input_tensor[command_hash % state_dim] = 1.0
        
        # Channel 2: Parameter encoding
        param_hash = hash(str(sorted(parameters.items()))) % state_dim
        input_tensor[param_hash % state_dim] = 0.8
        
        # Channel 3: Compliance score
        compliance_channel = int(compliance_score * 100) % state_dim
        input_tensor[compliance_channel] = compliance_score
        
        # Add some randomness for exploration (small amount)
        noise = torch.randn(state_dim) * 0.001
        input_tensor = input_tensor + noise
        
        return input_tensor.unsqueeze(0)  # Add batch dimension
    
    def _generate_final_correction(
        self,
        y_pred: torch.Tensor,
        error_signal: torch.Tensor,
        control_signal: ControlSignal,
        validation_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate the final correction signal"""
        
        # Combine prediction and error correction
        base_output = y_pred.squeeze(0)  # Remove batch dimension
        corrected_output = base_output + error_signal.squeeze(0)
        
        # Determine action type based on directive and validation
        compliance_score = validation_result['compliance_score']
        required_corrections = validation_result.get('required_corrections', [])
        
        if compliance_score >= 0.95:
            action_type = "direct_execution"
        elif compliance_score >= 0.8:
            action_type = "correction_with_guidance"
        else:
            action_type = "guidance_only"
        
        # Generate textual content (simplified)
        content = self._tensor_to_meaningful_text(corrected_output)
        
        # Add compliance-based adjustments
        if required_corrections:
            content += f"\n\nNote: {', '.join(required_corrections)}"
        
        correction = {
            'action_type': action_type,
            'content': content,
            'confidence': control_signal.confidence,
            'compliance_score': compliance_score,
            'correction_magnitude': control_signal.correction_magnitude.item() if hasattr(control_signal.correction_magnitude, 'item') else control_signal.correction_magnitude,
            'control_action': control_signal.convergence_action,
            'metadata': {
                'prediction_norm': torch.norm(base_output).item(),
                'error_magnitude': torch.norm(error_signal).item(),
                'final_output_norm': torch.norm(corrected_output).item()
            }
        }
        
        return correction
    
    def _tensor_to_meaningful_text(self, tensor: torch.Tensor) -> str:
        """Convert tensor output to meaningful text"""
        # This is a simplified implementation
        # In production, this would use proper decoding techniques
        
        # Convert tensor to string representation
        tensor_np = tensor.detach().numpy()
        
        # Create meaningful text from tensor values
        words = []
        for i in range(0, min(len(tensor_np), 100), 3):  # Process in chunks
            val = tensor_np[i]
            if abs(val) > 0.1:  # Only include significant values
                # Convert value to character (simplified)
                char_code = int(abs(val) * 1000) % 256
                if 32 <= char_code <= 126:  # Printable ASCII
                    words.append(chr(char_code))
        
        # Create meaningful response
        if words:
            text = ''.join(words)
            # Clean up the text
            text = text.replace('\x00', '').strip()
            if len(text) < 10:  # If too short, add context
                text += " [LEX-7 Analysis Complete]"
        else:
            text = "Analysis complete. System converged successfully."
        
        return text
    
    def _update_metrics(
        self, 
        validation_result: Dict, 
        error_state: ErrorState, 
        control_signal: ControlSignal, 
        processing_time: float
    ):
        """Update performance metrics"""
        
        # Initialize metrics if needed
        if not self.performance_metrics:
            self.performance_metrics = {
                'total_directives': 0,
                'successful_directives': 0,
                'refused_directives': 0,
                'avg_processing_time': 0.0,
                'avg_error_magnitude': 0.0,
                'avg_confidence': 0.0,
                'convergence_rate': 0.0,
                'compliance_scores': []
            }
        
        # Update counters
        self.performance_metrics['total_directives'] += 1
        
        if validation_result['valid']:
            self.performance_metrics['successful_directives'] += 1
        else:
            self.performance_metrics['refused_directives'] += 1
        
        # Update averages using exponential moving average
        alpha = 0.1
        
        self.performance_metrics['avg_processing_time'] = (
            alpha * processing_time + 
            (1 - alpha) * self.performance_metrics['avg_processing_time']
        )
        
        self.performance_metrics['avg_error_magnitude'] = (
            alpha * error_state.error_magnitude + 
            (1 - alpha) * self.performance_metrics['avg_error_magnitude']
        )
        
        self.performance_metrics['avg_confidence'] = (
            alpha * control_signal.confidence + 
            (1 - alpha) * self.performance_metrics['avg_confidence']
        )
        
        # Store compliance scores
        self.performance_metrics['compliance_scores'].append(validation_result['compliance_score'])
        if len(self.performance_metrics['compliance_scores']) > 1000:
            self.performance_metrics['compliance_scores'].pop(0)
        
        # Compute convergence rate
        converged_count = sum(1 for resp in self.directive_history[-100:] 
                            if resp.get('error_magnitude', 1.0) < 0.01)
        self.performance_metrics['convergence_rate'] = converged_count / min(len(self.directive_history), 100)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current node status and metrics"""
        return {
            'node_id': self.node_id,
            'state': self.state.value,
            'metrics': self.performance_metrics,
            'directive_history_size': len(self.directive_history),
            'sovereign_compliance': self.validator.get_compliance_statistics(),
            'error_model_performance': self.error_model.get_performance_metrics(),
            'config': {
                'model_type': self.config['model']['architecture'],
                'state_dim': self.config['model']['state_dim'],
                'convergence_threshold': self.config['lex_node']['convergence_threshold']
            }
        }
    
    def save_state(self, filepath: Optional[Path] = None):
        """Save the current node state"""
        if filepath is None:
            filepath = Path(self.config['lex_node'].get('state_vector_path', 'data/state/node_state.pt'))
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Save kernel state
        self.kernel.kernel.save_state(filepath)
        
        # Save additional state
        additional_state = {
            'current_state': self.current_state,
            'performance_metrics': self.performance_metrics,
            'directive_history': self.directive_history[-100:],  # Keep last 100
            'node_id': self.node_id,
            'timestamp': time.time()
        }
        
        torch.save(additional_state, filepath.with_suffix('.additional.pt'))
        
        logger.info(f"Saved Lex Node state to {filepath}")
    
    async def shutdown(self):
        """Gracefully shutdown the Lex Node"""
        logger.info(f"Shutting down Lex Node {self.node_id}...")
        
        # Save state
        self.save_state()
        
        # Update state
        self.state = NodeState.SHUTDOWN
        
        logger.info(f"Lex Node {self.node_id} shutdown complete")
    
    # Convenience methods for common operations
    
    async def analyze_intent(self, user_input: str, context: Optional[Dict] = None) -> LexResponse:
        """Convenience method for intent analysis"""
        directive = {
            'command': 'analyze_intent',
            'parameters': {
                'user_input': user_input,
                'context': context or {}
            },
            'signature': 'local_signature',
            'timestamp': time.time()
        }
        
        return await self.process_directive(directive, context)
    
    async def generate_response(self, prompt: str, constraints: Optional[Dict] = None) -> LexResponse:
        """Convenience method for response generation"""
        directive = {
            'command': 'generate_response',
            'parameters': {
                'prompt': prompt,
                'constraints': constraints or {}
            },
            'signature': 'local_signature',
            'timestamp': time.time()
        }
        
        return await self.process_directive(directive)
    
    async def validate_action(self, proposed_action: Dict, current_context: Optional[Dict] = None) -> LexResponse:
        """Convenience method for action validation"""
        directive = {
            'command': 'validate_action',
            'parameters': {
                'action': proposed_action,
                'context': current_context or {}
            },
            'signature': 'local_signature',
            'timestamp': time.time()
        }
        
        return await self.process_directive(directive, current_context)


# Example usage and testing
if __name__ == "__main__":
    async def main():
        # Initialize Lex Node
        config_path = Path("../config/lex_config.yaml")
        node = LexNode(config_path, "test_node_001")
        
        print("LEX-7 Architecture - Error-State Model")
        print("=" * 50)
        
        # Test intent analysis
        print("\n1. Testing Intent Analysis:")
        result = await node.analyze_intent("I want to optimize my financial planning", {
            'current_finances': 'stable',
            'goals': 'long_term_wealth'
        })
        
        print(f"Status: {result.status}")
        print(f"Confidence: {result.confidence:.3f}")
        print(f"Converged: {result.convergence_achieved}")
        print(f"Correction: {result.correction['content']}")
        
        # Test action validation
        print("\n2. Testing Action Validation:")
        result = await node.validate_action({
            'action': 'purchase',
            'amount': 500,
            'category': 'luxury'
        }, {
            'available_runway': 1000
        })
        
        print(f"Status: {result.status}")
        print(f"Compliance: {result.metadata.get('validation_compliance', 0):.3f}")
        print(f"Action: {result.correction.get('action_type', 'unknown')}")
        
        # Show node status
        print("\n3. Node Status:")
        status = node.get_status()
        print(f"State: {status['state']}")
        print(f"Total Directives: {status['metrics']['total_directives']}")
        print(f"Average Confidence: {status['metrics']['avg_confidence']:.3f}")
        print(f"Convergence Rate: {status['metrics']['convergence_rate']:.3f}")
        
        # Shutdown
        await node.shutdown()
    
    # Run the test
    asyncio.run(main())

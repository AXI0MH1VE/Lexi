import torch
import torch.nn as nn
import torch.nn.functional as F
import yaml
import logging

try:
    from mamba_ssm import Mamba  # type: ignore
except ImportError:
    class Mamba(nn.Module):
        """
        Minimal CPU-friendly stub when mamba-ssm wheels are unavailable (e.g., Windows).
        Preserves the interface used by this LexNode: forward(x, state) -> (output, new_state).
        """

        def __init__(self, d_model: int, d_state: int = 16, d_conv: int = 4, expand: int = 2):
            super().__init__()
            self.embed = nn.Embedding(256, d_model)
            self.state_linear = nn.Linear(d_model, d_model)

        def forward(self, x: torch.Tensor, state: torch.Tensor):
            # x: (batch, seq); state: (d_model,)
            emb = self.embed(x).mean(dim=1)  # (batch, d_model)
            new_state = torch.tanh(self.state_linear(emb) + state)
            # Return shape compatible with caller expectations: (batch, d_model) output + 1D state
            return new_state, new_state.squeeze(0)

class LexNode:
    """
    LEX-MAMBA Node: Error-State Lattice Implementation
    Core equation: h_t = A * h_{t-1} + B * x_t ; y_t = C * h_t
    """

    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.state_vector = torch.zeros(self.config['model']['state_vector_size'], device=self.device)
        self.sovereign_directive = self.config['sovereign_directive']

        # Initialize Mamba model
        self.mamba_model = Mamba(
            d_model=self.config['model']['state_vector_size'],
            d_state=16,
            d_conv=4,
            expand=2,
        ).to(self.device)

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('LexNode')

    def ingest_directive(self, bark_directive: str) -> str:
        """
        Ingest a BARK directive and compute state correction.
        Returns the corrective action to minimize error.
        """
        # Tokenize input (simplified)
        input_tokens = torch.tensor([ord(c) for c in bark_directive], dtype=torch.long, device=self.device).unsqueeze(0)

        # Mamba forward pass
        with torch.no_grad():
            output, self.state_vector = self.mamba_model(input_tokens, self.state_vector)

        # Calculate error (divergence from sovereign directive)
        divergence = self._calculate_divergence(output, self.sovereign_directive)

        if divergence > self.config['runtime']['error_threshold']:
            # Force correction
            corrective_action = self._correct_trajectory(output)
            self.logger.info(f"Error detected (divergence: {divergence:.4f}). Correcting trajectory.")
            return corrective_action
        else:
            # Accept the output
            return self._generate_output(output)

    def _calculate_divergence(self, output: torch.Tensor, reference: str) -> float:
        """
        Calculate entropy divergence from sovereign directive.
        Simplified: cosine similarity as proxy for alignment.
        """
        out_vec = output.flatten()
        target_len = out_vec.numel()

        ref_codes = [ord(c) for c in reference[:target_len]]
        ref_embedding = torch.zeros(target_len, device=self.device)
        ref_embedding[: len(ref_codes)] = torch.tensor(ref_codes, dtype=torch.float, device=self.device)

        # Align lengths
        if out_vec.numel() < target_len:
            pad = torch.zeros(target_len - out_vec.numel(), device=self.device)
            out_vec = torch.cat([out_vec, pad])
        else:
            out_vec = out_vec[:target_len]

        similarity = F.cosine_similarity(out_vec, ref_embedding, dim=0)
        return 1.0 - similarity.item()

    def _correct_trajectory(self, output: torch.Tensor) -> str:
        """
        Generate corrective action to reduce divergence.
        """
        return f"Error: Directive violation detected. Corrective Action: Align with {self.sovereign_directive[:50]}..."

    def _generate_output(self, output: torch.Tensor) -> str:
        """
        Generate final output from state.
        """
        # Simplified: convert tensor back to string
        tokens = output.squeeze().cpu().numpy()
        return ''.join([chr(int(token) % 256) for token in tokens])

    def persist_state(self, path: str):
        """
        Persist the state vector to disk.
        """
        torch.save(self.state_vector, path)
        self.logger.info(f"State persisted to {path}")

    def load_state(self, path: str):
        """
        Load state vector from disk.
        """
        self.state_vector = torch.load(path, map_location=self.device)
        self.logger.info(f"State loaded from {path}")

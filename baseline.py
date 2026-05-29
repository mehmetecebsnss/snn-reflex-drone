"""
ANN baseline model for comparison
"""
import torch
import torch.nn as nn


class ANNBaseline(nn.Module):
    """
    Simple feedforward neural network baseline
    Architecture: 3 -> 32 -> 3
    """
    
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(3, 32),
            nn.ReLU(),
            nn.Linear(32, 3)
        )
    
    def forward(self, x):
        """
        Forward pass
        
        Args:
            x: [batch, 3] sensor inputs
        
        Returns:
            logits: [batch, 3] action logits
        """
        return self.net(x)

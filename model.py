"""
Spiking Neural Network model for reflex control
"""
import torch
import torch.nn as nn
import snntorch as snn
from config import INPUT_SIZE, HIDDEN_SIZE, OUTPUT_SIZE


class SNNReflexNet(nn.Module):
    """
    Simple SNN with one hidden layer
    Architecture: 3 -> 32 -> 3
    """
    
    def __init__(self):
        super().__init__()
        
        # Layers
        self.fc1 = nn.Linear(INPUT_SIZE, HIDDEN_SIZE)
        self.lif1 = snn.Leaky(beta=0.9)
        
        self.fc2 = nn.Linear(HIDDEN_SIZE, OUTPUT_SIZE)
        self.lif2 = snn.Leaky(beta=0.9)
    
    def forward(self, x):
        """
        Forward pass through SNN
        
        Args:
            x: [time_steps, batch, input_size] spike input
        
        Returns:
            spk2_rec: [time_steps, batch, output_size] output spikes
            mem2_rec: [time_steps, batch, output_size] membrane potentials
        """
        # Initialize membrane potentials
        mem1 = self.lif1.init_leaky()
        mem2 = self.lif2.init_leaky()
        
        spk2_rec = []
        mem2_rec = []
        
        # Process each time step
        for t in range(x.size(0)):
            # Hidden layer
            cur1 = self.fc1(x[t])
            spk1, mem1 = self.lif1(cur1, mem1)
            
            # Output layer
            cur2 = self.fc2(spk1)
            spk2, mem2 = self.lif2(cur2, mem2)
            
            spk2_rec.append(spk2)
            mem2_rec.append(mem2)
        
        spk2_rec = torch.stack(spk2_rec)  # [T, B, 3]
        mem2_rec = torch.stack(mem2_rec)
        
        return spk2_rec, mem2_rec

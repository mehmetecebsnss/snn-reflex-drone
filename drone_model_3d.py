"""
Spiking Neural Network model for 3D drone control
Larger architecture for more complex 3D navigation
"""
import torch
import torch.nn as nn
import snntorch as snn


class SNNDroneNet3D(nn.Module):
    """
    SNN for 3D drone control with obstacle avoidance
    
    Architecture: 17 -> 128 -> 64 -> 4
    - Input: 17 (8 distances + 3 vel + 3 ang_vel + 3 orientation)
    - Hidden1: 128 neurons (LIF)
    - Hidden2: 64 neurons (LIF)
    - Output: 4 (thrust, roll_rate, pitch_rate, yaw_rate)
    """
    
    def __init__(self, input_size=17, hidden1_size=128, hidden2_size=64, output_size=4):
        super().__init__()
        
        self.input_size = input_size
        self.hidden1_size = hidden1_size
        self.hidden2_size = hidden2_size
        self.output_size = output_size
        
        # Layer 1: Input -> Hidden1
        self.fc1 = nn.Linear(input_size, hidden1_size)
        self.lif1 = snn.Leaky(beta=0.9)
        
        # Layer 2: Hidden1 -> Hidden2
        self.fc2 = nn.Linear(hidden1_size, hidden2_size)
        self.lif2 = snn.Leaky(beta=0.9)
        
        # Layer 3: Hidden2 -> Output
        self.fc3 = nn.Linear(hidden2_size, output_size)
        self.lif3 = snn.Leaky(beta=0.9)
    
    def forward(self, x):
        """
        Forward pass through SNN
        
        Args:
            x: [time_steps, batch, input_size] spike input
        
        Returns:
            spk3_rec: [time_steps, batch, output_size] output spikes
            mem3_rec: [time_steps, batch, output_size] membrane potentials
        """
        # Initialize membrane potentials
        mem1 = self.lif1.init_leaky()
        mem2 = self.lif2.init_leaky()
        mem3 = self.lif3.init_leaky()
        
        spk3_rec = []
        mem3_rec = []
        
        # Process each time step
        for t in range(x.size(0)):
            # Layer 1
            cur1 = self.fc1(x[t])
            spk1, mem1 = self.lif1(cur1, mem1)
            
            # Layer 2
            cur2 = self.fc2(spk1)
            spk2, mem2 = self.lif2(cur2, mem2)
            
            # Layer 3 (output)
            cur3 = self.fc3(spk2)
            spk3, mem3 = self.lif3(cur3, mem3)
            
            spk3_rec.append(spk3)
            mem3_rec.append(mem3)
        
        spk3_rec = torch.stack(spk3_rec)  # [T, B, 4]
        mem3_rec = torch.stack(mem3_rec)
        
        return spk3_rec, mem3_rec
    
    def predict(self, observation, time_steps=30, device='cpu'):
        """
        Predict action from observation (for inference)
        
        Args:
            observation: [input_size] numpy array
            time_steps: number of time steps to simulate
            device: 'cpu' or 'cuda'
        
        Returns:
            action: [output_size] numpy array, values in [-1, 1]
        """
        import numpy as np
        
        # Convert to tensor
        obs_tensor = torch.FloatTensor(observation).unsqueeze(0).to(device)  # [1, input_size]
        
        # Encode to spikes (rate coding)
        spike_input = self._encode_rate(obs_tensor, time_steps)  # [T, 1, input_size]
        
        # Forward pass
        with torch.no_grad():
            _, mem_rec = self.forward(spike_input)
        
        # Decode: use final membrane potential
        action_logits = mem_rec[-1, 0, :]  # [output_size]
        
        # Apply tanh to get [-1, 1] range
        action = torch.tanh(action_logits)
        
        return action.cpu().numpy()
    
    def _encode_rate(self, x, time_steps):
        """
        Rate coding: higher values -> more spikes
        
        Args:
            x: [batch, input_size] values in [0, 1]
            time_steps: number of time steps
        
        Returns:
            spikes: [time_steps, batch, input_size] binary spikes
        """
        batch_size = x.size(0)
        input_size = x.size(1)
        
        # Ensure values are in [0, 1]
        x = torch.clamp(x, 0, 1)
        
        # Generate spikes based on probability
        spike_prob = x.unsqueeze(0).expand(time_steps, -1, -1)  # [T, B, input_size]
        spikes = torch.rand_like(spike_prob) < spike_prob
        
        return spikes.float()
    
    def count_parameters(self):
        """Count total trainable parameters"""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


class ANNDroneNet3D(nn.Module):
    """
    Standard ANN baseline for comparison
    Same architecture as SNN but without spiking dynamics
    """
    
    def __init__(self, input_size=17, hidden1_size=128, hidden2_size=64, output_size=4):
        super().__init__()
        
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden1_size),
            nn.ReLU(),
            nn.Linear(hidden1_size, hidden2_size),
            nn.ReLU(),
            nn.Linear(hidden2_size, output_size),
            nn.Tanh()  # Output in [-1, 1]
        )
    
    def forward(self, x):
        """
        Forward pass
        
        Args:
            x: [batch, input_size]
        
        Returns:
            action: [batch, output_size] in [-1, 1]
        """
        return self.network(x)
    
    def predict(self, observation, device='cpu'):
        """
        Predict action from observation
        
        Args:
            observation: [input_size] numpy array
            device: 'cpu' or 'cuda'
        
        Returns:
            action: [output_size] numpy array in [-1, 1]
        """
        import numpy as np
        
        obs_tensor = torch.FloatTensor(observation).unsqueeze(0).to(device)
        
        with torch.no_grad():
            action = self.forward(obs_tensor)
        
        return action.cpu().numpy()[0]
    
    def count_parameters(self):
        """Count total trainable parameters"""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


if __name__ == "__main__":
    # Test the models
    print("=== Testing SNN Drone Model 3D ===")
    snn_model = SNNDroneNet3D()
    print(f"SNN Parameters: {snn_model.count_parameters():,}")
    
    # Test forward pass
    batch_size = 4
    time_steps = 30
    input_size = 17
    
    dummy_input = torch.rand(time_steps, batch_size, input_size)
    spk_out, mem_out = snn_model(dummy_input)
    print(f"SNN Output shape: {mem_out.shape}")
    
    # Test prediction
    dummy_obs = torch.rand(input_size).numpy()
    action = snn_model.predict(dummy_obs)
    print(f"SNN Action: {action}")
    
    print("\n=== Testing ANN Drone Model 3D ===")
    ann_model = ANNDroneNet3D()
    print(f"ANN Parameters: {ann_model.count_parameters():,}")
    
    # Test forward pass
    dummy_input_ann = torch.rand(batch_size, input_size)
    action_out = ann_model(dummy_input_ann)
    print(f"ANN Output shape: {action_out.shape}")
    
    # Test prediction
    action_ann = ann_model.predict(dummy_obs)
    print(f"ANN Action: {action_ann}")

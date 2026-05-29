"""
Training script for SNN Drone 3D
Supervised learning from expert demonstrations
"""
import torch
import torch.nn as nn
import numpy as np
from torch.utils.data import TensorDataset, DataLoader
import os

from drone_env_3d import DroneEnv3D
from drone_model_3d import SNNDroneNet3D
from drone_teacher_3d import DroneTeacher3D, collect_expert_data


# Configuration
CONFIG = {
    'time_steps': 30,
    'train_samples': 50000,
    'val_samples': 10000,
    'batch_size': 128,
    'epochs': 50,
    'lr': 1e-3,
    'device': 'cpu',
    'save_path': 'checkpoints/snn_drone_3d.pt',
    'log_path': 'logs/train_drone_3d_log.txt',
    'simple_teacher': False  # Use full teacher policy
}


def encode_rate(x, time_steps):
    """
    Rate coding: convert observations to spike trains
    
    Args:
        x: [batch, input_size] values in [0, 1]
        time_steps: number of time steps
    
    Returns:
        spikes: [time_steps, batch, input_size]
    """
    batch_size = x.size(0)
    input_size = x.size(1)
    
    # Ensure values are in [0, 1]
    x = torch.clamp(x, 0, 1)
    
    # Generate spikes
    spike_prob = x.unsqueeze(0).expand(time_steps, -1, -1)
    spikes = torch.rand_like(spike_prob) < spike_prob
    
    return spikes.float()


def train_epoch(model, dataloader, optimizer, criterion, time_steps, device):
    """Train for one epoch"""
    model.train()
    total_loss = 0.0
    
    for batch_idx, (obs, actions) in enumerate(dataloader):
        obs = obs.to(device)
        actions = actions.to(device)
        
        # Encode observations to spikes
        spike_input = encode_rate(obs, time_steps)  # [T, B, 17]
        
        # Forward pass
        _, mem_rec = model(spike_input)
        
        # Use final membrane potential as output
        output = mem_rec[-1]  # [B, 4]
        
        # Apply tanh to match action range [-1, 1]
        output = torch.tanh(output)
        
        # Calculate loss
        loss = criterion(output, actions)
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
    
    return total_loss / len(dataloader)


def validate(model, dataloader, criterion, time_steps, device):
    """Validate the model"""
    model.eval()
    total_loss = 0.0
    
    with torch.no_grad():
        for obs, actions in dataloader:
            obs = obs.to(device)
            actions = actions.to(device)
            
            spike_input = encode_rate(obs, time_steps)
            _, mem_rec = model(spike_input)
            output = torch.tanh(mem_rec[-1])
            
            loss = criterion(output, actions)
            total_loss += loss.item()
    
    return total_loss / len(dataloader)


def main():
    print("=== SNN Drone 3D Training ===\n")
    
    # Create directories
    os.makedirs('checkpoints', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    device = torch.device(CONFIG['device'])
    print(f"Using device: {device}\n")
    
    # === 1. Collect Expert Data ===
    print("Step 1: Collecting expert demonstrations...")
    env = DroneEnv3D(gui=False, max_steps=500)
    teacher = DroneTeacher3D()
    
    # Collect training data
    train_obs, train_actions = collect_expert_data(
        env, teacher, 
        num_samples=CONFIG['train_samples'],
        simple=CONFIG['simple_teacher']
    )
    
    # Collect validation data
    val_obs, val_actions = collect_expert_data(
        env, teacher,
        num_samples=CONFIG['val_samples'],
        simple=CONFIG['simple_teacher']
    )
    
    env.close()
    
    print(f"\nTraining data: {train_obs.shape}")
    print(f"Validation data: {val_obs.shape}\n")
    
    # === 2. Create DataLoaders ===
    print("Step 2: Creating data loaders...")
    train_dataset = TensorDataset(
        torch.FloatTensor(train_obs),
        torch.FloatTensor(train_actions)
    )
    val_dataset = TensorDataset(
        torch.FloatTensor(val_obs),
        torch.FloatTensor(val_actions)
    )
    
    train_loader = DataLoader(train_dataset, batch_size=CONFIG['batch_size'], shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=CONFIG['batch_size'], shuffle=False)
    
    print(f"Train batches: {len(train_loader)}")
    print(f"Val batches: {len(val_loader)}\n")
    
    # === 3. Create Model ===
    print("Step 3: Creating SNN model...")
    model = SNNDroneNet3D(
        input_size=17,
        hidden1_size=128,
        hidden2_size=64,
        output_size=4
    ).to(device)
    
    print(f"Model parameters: {model.count_parameters():,}\n")
    
    # === 4. Training Setup ===
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=CONFIG['lr'])
    
    # === 5. Training Loop ===
    print("Step 4: Training...\n")
    best_val_loss = float('inf')
    
    with open(CONFIG['log_path'], 'w') as log_file:
        for epoch in range(CONFIG['epochs']):
            train_loss = train_epoch(
                model, train_loader, optimizer, criterion,
                CONFIG['time_steps'], device
            )
            
            val_loss = validate(
                model, val_loader, criterion,
                CONFIG['time_steps'], device
            )
            
            # Log
            log_msg = f"Epoch {epoch+1}/{CONFIG['epochs']} | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f}"
            print(log_msg)
            log_file.write(log_msg + '\n')
            log_file.flush()
            
            # Save best model
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                torch.save(model.state_dict(), CONFIG['save_path'])
                print(f"  → Model saved (val_loss: {val_loss:.4f})")
    
    print(f"\n=== Training Complete ===")
    print(f"Best validation loss: {best_val_loss:.4f}")
    print(f"Model saved to: {CONFIG['save_path']}")
    print(f"Log saved to: {CONFIG['log_path']}")


if __name__ == "__main__":
    main()

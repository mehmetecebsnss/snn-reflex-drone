"""
Training script for SNN reflex model
"""
import os
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm

from config import BATCH_SIZE, EPOCHS, LR, DEVICE, TRAIN_SAMPLES, VAL_SAMPLES
from env import ObstacleEnv
from teacher import teacher_policy
from encoder import rate_encode
from model import SNNReflexNet


class ReflexDataset(Dataset):
    """Dataset of sensor states and teacher labels"""
    
    def __init__(self, n_samples=10000):
        self.states = []
        self.labels = []
        env = ObstacleEnv()
        
        print(f"Generating {n_samples} samples...")
        
        while len(self.states) < n_samples:
            state = env.reset()
            
            # Collect samples from this episode
            for _ in range(50):
                label = teacher_policy(state)
                self.states.append(state.copy())
                self.labels.append(label)
                
                # Add some exploration noise
                action = np.random.choice([0, 1, 2]) if np.random.rand() < 0.2 else label
                state, _, done = env.step(action)
                
                if done:
                    break
        
        # Trim to exact size
        self.states = np.array(self.states[:n_samples], dtype=np.float32)
        self.labels = np.array(self.labels[:n_samples], dtype=np.int64)
        
        print(f"Dataset created: {len(self.states)} samples")
        print(f"Label distribution: {np.bincount(self.labels)}")
    
    def __len__(self):
        return len(self.states)
    
    def __getitem__(self, idx):
        return self.states[idx], self.labels[idx]


def evaluate(model, loader, device):
    """Evaluate model accuracy on dataset"""
    model.eval()
    total = 0
    correct = 0
    
    with torch.no_grad():
        for states, labels in loader:
            states = states.to(device)
            labels = labels.to(device)
            
            # Encode to spikes
            spikes = rate_encode(states)
            
            # Forward pass
            _, mem = model(spikes)
            
            # Use sum of membrane potentials as logits
            logits = mem.sum(dim=0)
            preds = logits.argmax(dim=1)
            
            correct += (preds == labels).sum().item()
            total += labels.size(0)
    
    return correct / total


def main():
    print("=== SNN Reflex Training ===\n")
    
    # Create datasets
    print("Creating training dataset...")
    train_ds = ReflexDataset(n_samples=TRAIN_SAMPLES)
    
    print("\nCreating validation dataset...")
    val_ds = ReflexDataset(n_samples=VAL_SAMPLES)
    
    # Create dataloaders
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE)
    
    # Create model
    print(f"\nInitializing SNN model on {DEVICE}...")
    model = SNNReflexNet().to(DEVICE)
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    criterion = nn.CrossEntropyLoss()
    
    # Create checkpoint directory
    os.makedirs("checkpoints", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Training loop
    print(f"\nStarting training for {EPOCHS} epochs...\n")
    
    best_val_acc = 0.0
    log_file = open("logs/train_log.txt", "w")
    
    for epoch in range(EPOCHS):
        model.train()
        running_loss = 0.0
        
        for states, labels in tqdm(train_loader, desc=f"Epoch {epoch+1}/{EPOCHS}"):
            states = states.to(DEVICE)
            labels = labels.to(DEVICE)
            
            # Encode to spikes
            spikes = rate_encode(states)
            
            # Forward pass
            _, mem = model(spikes)
            
            # Use sum of membrane potentials as logits
            logits = mem.sum(dim=0)
            
            # Compute loss
            loss = criterion(logits, labels)
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
        
        # Evaluate
        val_acc = evaluate(model, val_loader, DEVICE)
        avg_loss = running_loss / len(train_loader)
        
        log_msg = f"Epoch {epoch+1} | Loss: {avg_loss:.4f} | Val Acc: {val_acc:.4f}"
        print(log_msg)
        log_file.write(log_msg + "\n")
        log_file.flush()
        
        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), "checkpoints/snn_reflex.pt")
            print(f"  → Best model saved (acc: {val_acc:.4f})")
    
    log_file.close()
    print(f"\nTraining complete! Best validation accuracy: {best_val_acc:.4f}")
    print("Model saved to: checkpoints/snn_reflex.pt")


if __name__ == "__main__":
    main()

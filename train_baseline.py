"""
Training script for ANN baseline model
"""
import os
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm

from config import BATCH_SIZE, EPOCHS, LR, DEVICE, TRAIN_SAMPLES, VAL_SAMPLES
from train import ReflexDataset
from baseline import ANNBaseline


def evaluate(model, loader, device):
    """Evaluate model accuracy on dataset"""
    model.eval()
    total = 0
    correct = 0
    
    with torch.no_grad():
        for states, labels in loader:
            states = states.to(device)
            labels = labels.to(device)
            
            # Forward pass
            logits = model(states)
            preds = logits.argmax(dim=1)
            
            correct += (preds == labels).sum().item()
            total += labels.size(0)
    
    return correct / total


def main():
    print("=== ANN Baseline Training ===\n")
    
    # Create datasets
    print("Creating training dataset...")
    train_ds = ReflexDataset(n_samples=TRAIN_SAMPLES)
    
    print("\nCreating validation dataset...")
    val_ds = ReflexDataset(n_samples=VAL_SAMPLES)
    
    # Create dataloaders
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE)
    
    # Create model
    print(f"\nInitializing ANN model on {DEVICE}...")
    model = ANNBaseline().to(DEVICE)
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    criterion = nn.CrossEntropyLoss()
    
    # Create checkpoint directory
    os.makedirs("checkpoints", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Training loop
    print(f"\nStarting training for {EPOCHS} epochs...\n")
    
    best_val_acc = 0.0
    log_file = open("logs/baseline_log.txt", "w")
    
    for epoch in range(EPOCHS):
        model.train()
        running_loss = 0.0
        
        for states, labels in tqdm(train_loader, desc=f"Epoch {epoch+1}/{EPOCHS}"):
            states = states.to(DEVICE)
            labels = labels.to(DEVICE)
            
            # Forward pass
            logits = model(states)
            
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
            torch.save(model.state_dict(), "checkpoints/ann_baseline.pt")
            print(f"  → Best model saved (acc: {val_acc:.4f})")
    
    log_file.close()
    print(f"\nTraining complete! Best validation accuracy: {best_val_acc:.4f}")
    print("Model saved to: checkpoints/ann_baseline.pt")


if __name__ == "__main__":
    main()

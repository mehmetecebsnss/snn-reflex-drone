"""
Benchmark script to compare SNN vs ANN baseline
"""
import time
import torch
import numpy as np
import psutil
import os
from torch.utils.data import DataLoader

from config import BATCH_SIZE, DEVICE, VAL_SAMPLES
from env import ObstacleEnv
from encoder import rate_encode
from model import SNNReflexNet
from baseline import ANNBaseline
from train import ReflexDataset


def benchmark_inference_speed(model, is_snn, n_iterations=1000):
    """Measure inference time"""
    model.eval()
    
    # Dummy input
    dummy_state = torch.randn(1, 3, device=DEVICE)
    
    # Warmup
    with torch.no_grad():
        for _ in range(10):
            if is_snn:
                spikes = rate_encode(dummy_state)
                _, mem = model(spikes)
            else:
                _ = model(dummy_state)
    
    # Measure
    times = []
    with torch.no_grad():
        for _ in range(n_iterations):
            start = time.perf_counter()
            
            if is_snn:
                spikes = rate_encode(dummy_state)
                _, mem = model(spikes)
            else:
                _ = model(dummy_state)
            
            end = time.perf_counter()
            times.append((end - start) * 1000)  # Convert to ms
    
    return np.mean(times), np.std(times)


def benchmark_simulation(model, is_snn, n_episodes=100):
    """Measure performance in simulation"""
    model.eval()
    env = ObstacleEnv()
    
    episode_lengths = []
    
    for ep in range(n_episodes):
        state = env.reset()
        steps = 0
        done = False
        
        while not done and steps < 1000:
            with torch.no_grad():
                states = torch.tensor(state, dtype=torch.float32, device=DEVICE).unsqueeze(0)
                
                if is_snn:
                    spikes = rate_encode(states)
                    _, mem = model(spikes)
                    logits = mem.sum(dim=0)
                else:
                    logits = model(states)
                
                action = logits.argmax(dim=1).item()
            
            state, _, done = env.step(action)
            steps += 1
        
        episode_lengths.append(steps)
    
    return np.mean(episode_lengths), np.std(episode_lengths), episode_lengths


def benchmark_accuracy(model, is_snn, loader):
    """Measure classification accuracy"""
    model.eval()
    total = 0
    correct = 0
    
    with torch.no_grad():
        for states, labels in loader:
            states = states.to(DEVICE)
            labels = labels.to(DEVICE)
            
            if is_snn:
                spikes = rate_encode(states)
                _, mem = model(spikes)
                logits = mem.sum(dim=0)
            else:
                logits = model(states)
            
            preds = logits.argmax(dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)
    
    return correct / total


def count_parameters(model):
    """Count trainable parameters"""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def main():
    print("=" * 60)
    print("SNN vs ANN BENCHMARK")
    print("=" * 60)
    print()
    
    # Load validation dataset
    print("Loading validation dataset...")
    val_ds = ReflexDataset(n_samples=VAL_SAMPLES)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE)
    print()
    
    # Load models
    print("Loading models...")
    
    snn_model = SNNReflexNet().to(DEVICE)
    ann_model = ANNBaseline().to(DEVICE)
    
    try:
        snn_model.load_state_dict(torch.load("checkpoints/snn_reflex.pt", map_location=DEVICE))
        print("✓ SNN model loaded")
    except FileNotFoundError:
        print("✗ SNN model not found. Run train.py first.")
        return
    
    try:
        ann_model.load_state_dict(torch.load("checkpoints/ann_baseline.pt", map_location=DEVICE))
        print("✓ ANN model loaded")
    except FileNotFoundError:
        print("✗ ANN model not found. Run train_baseline.py first.")
        return
    
    print()
    
    # Model size comparison
    print("-" * 60)
    print("MODEL SIZE")
    print("-" * 60)
    snn_params = count_parameters(snn_model)
    ann_params = count_parameters(ann_model)
    print(f"SNN parameters: {snn_params:,}")
    print(f"ANN parameters: {ann_params:,}")
    print()
    
    # Accuracy comparison
    print("-" * 60)
    print("CLASSIFICATION ACCURACY")
    print("-" * 60)
    print("Evaluating SNN...")
    snn_acc = benchmark_accuracy(snn_model, True, val_loader)
    print(f"SNN accuracy: {snn_acc:.4f} ({snn_acc*100:.2f}%)")
    
    print("Evaluating ANN...")
    ann_acc = benchmark_accuracy(ann_model, False, val_loader)
    print(f"ANN accuracy: {ann_acc:.4f} ({ann_acc*100:.2f}%)")
    print()
    
    # Inference speed comparison
    print("-" * 60)
    print("INFERENCE SPEED (1000 iterations)")
    print("-" * 60)
    print("Measuring SNN...")
    snn_mean, snn_std = benchmark_inference_speed(snn_model, True)
    print(f"SNN: {snn_mean:.3f} ± {snn_std:.3f} ms")
    
    print("Measuring ANN...")
    ann_mean, ann_std = benchmark_inference_speed(ann_model, False)
    print(f"ANN: {ann_mean:.3f} ± {ann_std:.3f} ms")
    print(f"Speedup: {snn_mean/ann_mean:.2f}x (ANN is faster)" if ann_mean < snn_mean else f"Speedup: {ann_mean/snn_mean:.2f}x (SNN is faster)")
    print()
    
    # Simulation performance
    print("-" * 60)
    print("SIMULATION PERFORMANCE (100 episodes)")
    print("-" * 60)
    print("Testing SNN...")
    snn_avg, snn_std_sim, snn_lengths = benchmark_simulation(snn_model, True, n_episodes=100)
    print(f"SNN survival: {snn_avg:.1f} ± {snn_std_sim:.1f} steps")
    
    print("Testing ANN...")
    ann_avg, ann_std_sim, ann_lengths = benchmark_simulation(ann_model, False, n_episodes=100)
    print(f"ANN survival: {ann_avg:.1f} ± {ann_std_sim:.1f} steps")
    print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Accuracy:   SNN {snn_acc:.2%} vs ANN {ann_acc:.2%}")
    print(f"Speed:      SNN {snn_mean:.2f}ms vs ANN {ann_mean:.2f}ms")
    print(f"Survival:   SNN {snn_avg:.1f} vs ANN {ann_avg:.1f} steps")
    print()
    
    # Save results
    results = {
        'snn_accuracy': snn_acc,
        'ann_accuracy': ann_acc,
        'snn_inference_ms': snn_mean,
        'ann_inference_ms': ann_mean,
        'snn_survival': snn_avg,
        'ann_survival': ann_avg,
        'snn_params': snn_params,
        'ann_params': ann_params
    }
    
    np.savez('logs/benchmark_results.npz', **results)
    print("Results saved to: logs/benchmark_results.npz")


if __name__ == "__main__":
    main()

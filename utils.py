"""
Utility functions for the SNN reflex project
"""
import numpy as np
import matplotlib.pyplot as plt


def plot_training_log(log_file="logs/train_log.txt"):
    """Plot training loss and accuracy from log file"""
    epochs = []
    losses = []
    accs = []
    
    with open(log_file, 'r') as f:
        for line in f:
            if 'Epoch' in line:
                parts = line.split('|')
                epoch = int(parts[0].split()[1])
                loss = float(parts[1].split(':')[1].strip())
                acc = float(parts[2].split(':')[1].strip())
                
                epochs.append(epoch)
                losses.append(loss)
                accs.append(acc)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    ax1.plot(epochs, losses)
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.set_title('Training Loss')
    ax1.grid(True)
    
    ax2.plot(epochs, accs)
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Accuracy')
    ax2.set_title('Validation Accuracy')
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig('logs/training_plot.png', dpi=150)
    print("Plot saved to: logs/training_plot.png")
    plt.show()


def analyze_sensor_data(data_file="data/train_samples.npz"):
    """Analyze sensor data distribution"""
    data = np.load(data_file)
    states = data['states']
    labels = data['labels']
    
    print("Dataset Statistics:")
    print(f"Total samples: {len(states)}")
    print(f"Label distribution: {np.bincount(labels)}")
    print(f"  Left:     {np.sum(labels == 0)} ({np.sum(labels == 0)/len(labels)*100:.1f}%)")
    print(f"  Straight: {np.sum(labels == 1)} ({np.sum(labels == 1)/len(labels)*100:.1f}%)")
    print(f"  Right:    {np.sum(labels == 2)} ({np.sum(labels == 2)/len(labels)*100:.1f}%)")
    print()
    
    print("Sensor Statistics:")
    print(f"Left sensor:  mean={states[:,0].mean():.3f}, std={states[:,0].std():.3f}")
    print(f"Front sensor: mean={states[:,1].mean():.3f}, std={states[:,1].std():.3f}")
    print(f"Right sensor: mean={states[:,2].mean():.3f}, std={states[:,2].std():.3f}")
    
    # Plot distributions
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Sensor distributions
    axes[0, 0].hist(states[:, 0], bins=50, alpha=0.7, label='Left')
    axes[0, 0].hist(states[:, 1], bins=50, alpha=0.7, label='Front')
    axes[0, 0].hist(states[:, 2], bins=50, alpha=0.7, label='Right')
    axes[0, 0].set_xlabel('Normalized Distance')
    axes[0, 0].set_ylabel('Count')
    axes[0, 0].set_title('Sensor Value Distribution')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Label distribution
    label_names = ['Left', 'Straight', 'Right']
    label_counts = np.bincount(labels)
    axes[0, 1].bar(label_names, label_counts)
    axes[0, 1].set_ylabel('Count')
    axes[0, 1].set_title('Action Label Distribution')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Sensor values by action
    for action in range(3):
        mask = labels == action
        axes[1, 0].scatter(states[mask, 0], states[mask, 1], 
                          alpha=0.3, s=1, label=label_names[action])
    axes[1, 0].set_xlabel('Left Sensor')
    axes[1, 0].set_ylabel('Front Sensor')
    axes[1, 0].set_title('Left vs Front by Action')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    for action in range(3):
        mask = labels == action
        axes[1, 1].scatter(states[mask, 2], states[mask, 1], 
                          alpha=0.3, s=1, label=label_names[action])
    axes[1, 1].set_xlabel('Right Sensor')
    axes[1, 1].set_ylabel('Front Sensor')
    axes[1, 1].set_title('Right vs Front by Action')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('logs/sensor_analysis.png', dpi=150)
    print("\nPlot saved to: logs/sensor_analysis.png")
    plt.show()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'plot':
            plot_training_log()
        elif sys.argv[1] == 'analyze':
            analyze_sensor_data()
    else:
        print("Usage:")
        print("  python utils.py plot     - Plot training curves")
        print("  python utils.py analyze  - Analyze sensor data")

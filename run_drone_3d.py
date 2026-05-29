"""
Live demo of trained SNN controlling 3D drone
"""
import torch
import numpy as np
import time

from drone_env_3d import DroneEnv3D
from drone_model_3d import SNNDroneNet3D


def run_demo(model_path='checkpoints/snn_drone_3d.pt', num_episodes=5, max_steps=1000):
    """
    Run live demo of trained SNN drone
    
    Args:
        model_path: path to trained model
        num_episodes: number of episodes to run
        max_steps: max steps per episode
    """
    print("=== SNN Drone 3D Live Demo ===\n")
    
    # Load model
    print("Loading trained model...")
    device = torch.device('cpu')
    model = SNNDroneNet3D().to(device)
    
    try:
        model.load_state_dict(torch.load(model_path, map_location=device))
        print("Model loaded successfully!\n")
    except FileNotFoundError:
        print(f"Error: Model not found at {model_path}")
        print("Please train the model first using: python train_drone_3d.py")
        return
    
    model.eval()
    
    # Create environment
    print("Creating 3D drone environment...")
    env = DroneEnv3D(gui=True, max_steps=max_steps)
    print("Environment ready!\n")
    
    print("Controls:")
    print("  Close window to exit")
    print("\nRunning simulation...\n")
    
    # Run episodes
    episode_rewards = []
    episode_steps = []
    
    for episode in range(num_episodes):
        obs = env.reset()
        total_reward = 0
        step = 0
        
        print(f"Episode {episode + 1}/{num_episodes}")
        
        while step < max_steps:
            # Get action from SNN
            action = model.predict(obs, time_steps=30, device=device)
            
            # Step environment
            obs, reward, done, info = env.step(action)
            total_reward += reward
            step += 1
            
            # Small delay for visualization
            time.sleep(0.01)
            
            if done:
                print(f"  Episode ended at step {step}")
                print(f"  Total reward: {total_reward:.2f}")
                if 'collision' in info:
                    print(f"  Reason: Collision")
                elif 'out_of_bounds' in info:
                    print(f"  Reason: Out of bounds")
                elif 'timeout' in info:
                    print(f"  Reason: Timeout (success!)")
                print()
                break
        
        episode_rewards.append(total_reward)
        episode_steps.append(step)
    
    env.close()
    
    # Summary
    print("\n=== Demo Summary ===")
    print(f"Episodes: {num_episodes}")
    print(f"Average steps: {np.mean(episode_steps):.1f} ± {np.std(episode_steps):.1f}")
    print(f"Average reward: {np.mean(episode_rewards):.1f} ± {np.std(episode_rewards):.1f}")
    print(f"Max steps: {np.max(episode_steps)}")
    print(f"Min steps: {np.min(episode_steps)}")


def compare_with_expert(model_path='checkpoints/snn_drone_3d.pt', num_episodes=10):
    """
    Compare SNN performance with expert teacher
    """
    from drone_teacher_3d import DroneTeacher3D
    
    print("=== SNN vs Expert Comparison ===\n")
    
    device = torch.device('cpu')
    
    # Load SNN
    snn_model = SNNDroneNet3D().to(device)
    snn_model.load_state_dict(torch.load(model_path, map_location=device))
    snn_model.eval()
    
    # Create teacher
    teacher = DroneTeacher3D()
    
    # Test both
    env = DroneEnv3D(gui=False, max_steps=1000)
    
    print("Testing SNN...")
    snn_steps = []
    snn_rewards = []
    
    for ep in range(num_episodes):
        obs = env.reset()
        total_reward = 0
        step = 0
        
        while step < 1000:
            action = snn_model.predict(obs, device=device)
            obs, reward, done, info = env.step(action)
            total_reward += reward
            step += 1
            
            if done:
                break
        
        snn_steps.append(step)
        snn_rewards.append(total_reward)
    
    print("Testing Expert...")
    expert_steps = []
    expert_rewards = []
    
    for ep in range(num_episodes):
        obs = env.reset()
        total_reward = 0
        step = 0
        
        while step < 1000:
            action = teacher.get_action(obs)
            obs, reward, done, info = env.step(action)
            total_reward += reward
            step += 1
            
            if done:
                break
        
        expert_steps.append(step)
        expert_rewards.append(total_reward)
    
    env.close()
    
    # Results
    print("\n=== Results ===")
    print(f"\nSNN:")
    print(f"  Avg steps: {np.mean(snn_steps):.1f} ± {np.std(snn_steps):.1f}")
    print(f"  Avg reward: {np.mean(snn_rewards):.1f} ± {np.std(snn_rewards):.1f}")
    
    print(f"\nExpert:")
    print(f"  Avg steps: {np.mean(expert_steps):.1f} ± {np.std(expert_steps):.1f}")
    print(f"  Avg reward: {np.mean(expert_rewards):.1f} ± {np.std(expert_rewards):.1f}")
    
    print(f"\nSNN Performance: {np.mean(snn_steps) / np.mean(expert_steps) * 100:.1f}% of expert")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--compare':
        compare_with_expert()
    else:
        run_demo()

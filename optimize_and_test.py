"""
Comprehensive testing and optimization for 3D Drone models
Tests existing models and suggests improvements
"""
import torch
import numpy as np
from drone_env_3d import DroneEnv3D
from drone_model_3d import SNNDroneNet3D, ANNDroneNet3D
from drone_teacher_3d import DroneTeacher3D


def test_model_extensively(model_name, model, env, num_episodes=20):
    """
    Extensive testing of a model
    
    Returns detailed statistics
    """
    print(f"\n{'='*60}")
    print(f"Testing {model_name}")
    print(f"{'='*60}")
    
    steps_list = []
    rewards_list = []
    collision_count = 0
    timeout_count = 0
    oob_count = 0
    
    for ep in range(num_episodes):
        obs = env.reset()
        total_reward = 0
        step = 0
        max_steps = env.max_steps
        
        while step < max_steps:
            # Get action
            if model_name == "Expert":
                action = model.get_action(obs)
            elif "SNN" in model_name:
                action = model.predict(obs, device='cpu')
            elif "ANN" in model_name:
                action = model.predict(obs, device='cpu')
            
            obs, reward, done, info = env.step(action)
            total_reward += reward
            step += 1
            
            if done:
                if 'collision' in info:
                    collision_count += 1
                elif 'out_of_bounds' in info:
                    oob_count += 1
                elif 'timeout' in info:
                    timeout_count += 1
                break
        
        steps_list.append(step)
        rewards_list.append(total_reward)
        
        if (ep + 1) % 5 == 0:
            print(f"  Episode {ep+1}/{num_episodes}: {step} steps, reward: {total_reward:.1f}")
    
    # Statistics
    steps_array = np.array(steps_list)
    rewards_array = np.array(rewards_list)
    
    results = {
        'steps_mean': np.mean(steps_array),
        'steps_std': np.std(steps_array),
        'steps_min': np.min(steps_array),
        'steps_max': np.max(steps_array),
        'steps_median': np.median(steps_array),
        'reward_mean': np.mean(rewards_array),
        'reward_std': np.std(rewards_array),
        'collision_rate': collision_count / num_episodes * 100,
        'timeout_rate': timeout_count / num_episodes * 100,
        'oob_rate': oob_count / num_episodes * 100,
        'success_rate': timeout_count / num_episodes * 100,
    }
    
    print(f"\n{model_name} Results:")
    print(f"  Steps: {results['steps_mean']:.1f} ± {results['steps_std']:.1f}")
    print(f"  Range: [{results['steps_min']}, {results['steps_max']}]")
    print(f"  Median: {results['steps_median']:.1f}")
    print(f"  Reward: {results['reward_mean']:.1f} ± {results['reward_std']:.1f}")
    print(f"  Success Rate: {results['success_rate']:.1f}%")
    print(f"  Collision Rate: {results['collision_rate']:.1f}%")
    print(f"  Out of Bounds: {results['oob_rate']:.1f}%")
    
    return results


def compare_models(results_dict):
    """
    Compare all models and provide recommendations
    """
    print(f"\n{'='*60}")
    print("MODEL COMPARISON")
    print(f"{'='*60}\n")
    
    # Sort by performance
    rankings = sorted(results_dict.items(), 
                     key=lambda x: x[1]['steps_mean'], 
                     reverse=True)
    
    print("Performance Ranking (by survival steps):")
    for i, (model_name, results) in enumerate(rankings, 1):
        print(f"  {i}. {model_name}: {results['steps_mean']:.1f} steps "
              f"(success: {results['success_rate']:.1f}%)")
    
    # Best model
    best_model, best_results = rankings[0]
    print(f"\n🏆 Best Model: {best_model}")
    print(f"   Average: {best_results['steps_mean']:.1f} steps")
    print(f"   Success: {best_results['success_rate']:.1f}%")
    
    # Relative performance
    if len(rankings) > 1:
        print(f"\nRelative to {best_model}:")
        for model_name, results in rankings[1:]:
            ratio = (results['steps_mean'] / best_results['steps_mean']) * 100
            print(f"  {model_name}: {ratio:.1f}%")
    
    return best_model, best_results


def suggest_improvements(results_dict):
    """
    Analyze results and suggest improvements
    """
    print(f"\n{'='*60}")
    print("IMPROVEMENT SUGGESTIONS")
    print(f"{'='*60}\n")
    
    for model_name, results in results_dict.items():
        if "Expert" in model_name:
            continue
        
        print(f"{model_name}:")
        
        # Check success rate
        if results['success_rate'] < 20:
            print("  ⚠️  Very low success rate (<20%)")
            print("     → Need more training epochs")
            print("     → Consider simpler teacher policy")
        elif results['success_rate'] < 50:
            print("  ⚠️  Low success rate (<50%)")
            print("     → Increase training data")
            print("     → Tune hyperparameters")
        else:
            print("  ✓ Good success rate")
        
        # Check collision rate
        if results['collision_rate'] > 80:
            print("  ⚠️  High collision rate (>80%)")
            print("     → Improve obstacle avoidance")
            print("     → Adjust reward function")
        
        # Check variance
        if results['steps_std'] > results['steps_mean'] * 0.5:
            print("  ⚠️  High variance")
            print("     → Model is unstable")
            print("     → Need more training")
        else:
            print("  ✓ Stable performance")
        
        print()


def recommend_hyperparameters(results_dict):
    """
    Recommend hyperparameter changes based on results
    """
    print(f"\n{'='*60}")
    print("HYPERPARAMETER RECOMMENDATIONS")
    print(f"{'='*60}\n")
    
    # Check if models are performing poorly
    avg_success = np.mean([r['success_rate'] for r in results_dict.values() 
                          if 'Expert' not in list(results_dict.keys())[0]])
    
    if avg_success < 20:
        print("📋 Recommended Configuration (Aggressive):")
        print("""
CONFIG = {
    'time_steps': 40,           # Increased for better temporal dynamics
    'train_samples': 100000,    # Much more data
    'val_samples': 20000,
    'batch_size': 256,          # Larger batches
    'epochs': 100,              # Much longer training
    'lr': 5e-4,                 # Lower learning rate
    'hidden1_size': 256,        # Larger network
    'hidden2_size': 128,
    'simple_teacher': True,     # Use simpler teacher
}
        """)
    elif avg_success < 50:
        print("📋 Recommended Configuration (Moderate):")
        print("""
CONFIG = {
    'time_steps': 35,
    'train_samples': 75000,
    'val_samples': 15000,
    'batch_size': 128,
    'epochs': 75,
    'lr': 7e-4,
    'hidden1_size': 192,
    'hidden2_size': 96,
    'simple_teacher': False,
}
        """)
    else:
        print("📋 Recommended Configuration (Fine-tuning):")
        print("""
CONFIG = {
    'time_steps': 30,
    'train_samples': 50000,
    'val_samples': 10000,
    'batch_size': 128,
    'epochs': 50,
    'lr': 1e-3,
    'hidden1_size': 128,
    'hidden2_size': 64,
    'simple_teacher': False,
}
        """)
    
    print("\n💡 Additional Tips:")
    print("  1. Use curriculum learning (start with easier scenarios)")
    print("  2. Add data augmentation (noise to observations)")
    print("  3. Try different reward shaping")
    print("  4. Consider using dropout for regularization")


def main():
    """
    Main testing and optimization pipeline
    """
    print("="*60)
    print("3D DRONE MODEL OPTIMIZATION & TESTING")
    print("="*60)
    
    # Create environment
    print("\nCreating test environment...")
    env = DroneEnv3D(gui=False, max_steps=1000)
    
    results = {}
    
    # Test SNN
    print("\n1. Loading and testing SNN...")
    try:
        snn_model = SNNDroneNet3D().to('cpu')
        snn_model.load_state_dict(
            torch.load('checkpoints/snn_drone_3d.pt', map_location='cpu')
        )
        snn_model.eval()
        results['SNN'] = test_model_extensively('SNN', snn_model, env, num_episodes=20)
    except Exception as e:
        print(f"  ✗ Could not load SNN: {e}")
    
    # Test ANN
    print("\n2. Loading and testing ANN...")
    try:
        ann_model = ANNDroneNet3D().to('cpu')
        ann_model.load_state_dict(
            torch.load('checkpoints/ann_drone_3d.pt', map_location='cpu')
        )
        ann_model.eval()
        results['ANN'] = test_model_extensively('ANN', ann_model, env, num_episodes=20)
    except Exception as e:
        print(f"  ✗ Could not load ANN: {e}")
    
    # Test Expert
    print("\n3. Testing Expert...")
    teacher = DroneTeacher3D()
    results['Expert'] = test_model_extensively('Expert', teacher, env, num_episodes=20)
    
    env.close()
    
    # Analysis
    if len(results) > 0:
        best_model, best_results = compare_models(results)
        suggest_improvements(results)
        recommend_hyperparameters(results)
        
        # Save results
        print(f"\n{'='*60}")
        print("SAVING RESULTS")
        print(f"{'='*60}")
        
        import json
        with open('logs/optimization_results.json', 'w') as f:
            # Convert numpy types to Python types
            results_serializable = {}
            for model_name, model_results in results.items():
                results_serializable[model_name] = {
                    k: float(v) if isinstance(v, (np.floating, np.integer)) else v
                    for k, v in model_results.items()
                }
            json.dump(results_serializable, f, indent=2)
        
        print("✓ Results saved to: logs/optimization_results.json")
        
        # Final recommendation
        print(f"\n{'='*60}")
        print("FINAL RECOMMENDATION")
        print(f"{'='*60}\n")
        
        avg_success = np.mean([r['success_rate'] for k, r in results.items() if k != 'Expert'])
        
        if avg_success < 30:
            print("🔴 Models need significant improvement")
            print("   Recommendation: Retrain with aggressive configuration")
            print("   Command: python train_drone_3d_optimized.py --config aggressive")
        elif avg_success < 60:
            print("🟡 Models show promise but need tuning")
            print("   Recommendation: Retrain with moderate configuration")
            print("   Command: python train_drone_3d_optimized.py --config moderate")
        else:
            print("🟢 Models performing well!")
            print("   Recommendation: Fine-tune or proceed to next phase")
            print("   Next: ROS integration or neuromorphic chip porting")
    
    print(f"\n{'='*60}")
    print("TESTING COMPLETE!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

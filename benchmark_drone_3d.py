"""
Comprehensive benchmark for 3D Drone models
Tests: SNN vs ANN vs Expert across different scenarios
"""
import torch
import numpy as np
import time
import json
from datetime import datetime

from drone_env_3d import DroneEnv3D
from drone_model_3d import SNNDroneNet3D, ANNDroneNet3D
from drone_teacher_3d import DroneTeacher3D


class DroneBenchmark:
    """Comprehensive benchmark suite for drone models"""
    
    def __init__(self):
        self.device = torch.device('cpu')
        self.results = {}
    
    def load_models(self):
        """Load all models"""
        print("Loading models...")
        
        # SNN
        try:
            self.snn_model = SNNDroneNet3D().to(self.device)
            self.snn_model.load_state_dict(
                torch.load('checkpoints/snn_drone_3d.pt', map_location=self.device)
            )
            self.snn_model.eval()
            print("  ✓ SNN loaded")
        except:
            print("  ✗ SNN not found")
            self.snn_model = None
        
        # ANN
        try:
            self.ann_model = ANNDroneNet3D().to(self.device)
            self.ann_model.load_state_dict(
                torch.load('checkpoints/ann_drone_3d.pt', map_location=self.device)
            )
            self.ann_model.eval()
            print("  ✓ ANN loaded")
        except:
            print("  ✗ ANN not found")
            self.ann_model = None
        
        # Expert
        self.expert = DroneTeacher3D()
        print("  ✓ Expert loaded")
    
    def test_scenario(self, model_name, model, env, num_episodes=10):
        """Test a model in given environment"""
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
                # Get action based on model type
                if model_name == "Expert":
                    action = model.get_action(obs)
                elif model_name == "SNN":
                    action = model.predict(obs, device=self.device)
                elif model_name == "ANN":
                    action = model.predict(obs, device=self.device)
                
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
        
        return {
            'steps_mean': np.mean(steps_list),
            'steps_std': np.std(steps_list),
            'steps_min': np.min(steps_list),
            'steps_max': np.max(steps_list),
            'reward_mean': np.mean(rewards_list),
            'reward_std': np.std(rewards_list),
            'collision_rate': collision_count / num_episodes,
            'timeout_rate': timeout_count / num_episodes,
            'oob_rate': oob_count / num_episodes,
            'episodes': num_episodes
        }
    
    def test_inference_speed(self, model_name, model, num_iterations=1000):
        """Test inference speed"""
        dummy_obs = np.random.rand(17).astype(np.float32)
        
        times = []
        for _ in range(num_iterations):
            start = time.time()
            
            if model_name == "Expert":
                _ = model.get_action(dummy_obs)
            elif model_name == "SNN":
                _ = model.predict(dummy_obs, device=self.device)
            elif model_name == "ANN":
                _ = model.predict(dummy_obs, device=self.device)
            
            times.append(time.time() - start)
        
        return {
            'mean_ms': np.mean(times) * 1000,
            'std_ms': np.std(times) * 1000,
            'min_ms': np.min(times) * 1000,
            'max_ms': np.max(times) * 1000
        }
    
    def run_benchmark(self, scenarios, num_episodes=10):
        """Run full benchmark"""
        print("\n" + "="*60)
        print("DRONE 3D COMPREHENSIVE BENCHMARK")
        print("="*60 + "\n")
        
        self.load_models()
        
        models = []
        if self.snn_model:
            models.append(("SNN", self.snn_model))
        if self.ann_model:
            models.append(("ANN", self.ann_model))
        models.append(("Expert", self.expert))
        
        # Test each scenario
        for scenario_name, scenario_config in scenarios.items():
            print(f"\n{'='*60}")
            print(f"Scenario: {scenario_name}")
            print(f"{'='*60}")
            print(f"Config: {scenario_config}")
            
            self.results[scenario_name] = {}
            
            # Create environment
            env = DroneEnv3D(
                gui=False,
                max_steps=scenario_config['max_steps']
            )
            
            # Test each model
            for model_name, model in models:
                print(f"\nTesting {model_name}...")
                
                # Performance test
                perf_results = self.test_scenario(
                    model_name, model, env, num_episodes
                )
                
                # Inference speed test
                speed_results = self.test_inference_speed(model_name, model)
                
                # Combine results
                self.results[scenario_name][model_name] = {
                    'performance': perf_results,
                    'inference_speed': speed_results
                }
                
                print(f"  Steps: {perf_results['steps_mean']:.1f} ± {perf_results['steps_std']:.1f}")
                print(f"  Reward: {perf_results['reward_mean']:.1f} ± {perf_results['reward_std']:.1f}")
                print(f"  Success Rate: {perf_results['timeout_rate']*100:.1f}%")
                print(f"  Inference: {speed_results['mean_ms']:.2f} ms")
            
            env.close()
        
        # Model size comparison
        print(f"\n{'='*60}")
        print("Model Size Comparison")
        print(f"{'='*60}")
        
        if self.snn_model:
            snn_params = self.snn_model.count_parameters()
            print(f"SNN Parameters: {snn_params:,}")
        
        if self.ann_model:
            ann_params = self.ann_model.count_parameters()
            print(f"ANN Parameters: {ann_params:,}")
        
        print(f"Expert Parameters: 0 (rule-based)")
        
        # Save results
        self.save_results()
        
        # Print summary
        self.print_summary()
    
    def save_results(self):
        """Save results to JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"logs/benchmark_drone_3d_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n✓ Results saved to: {filename}")
    
    def print_summary(self):
        """Print summary comparison"""
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}\n")
        
        # Get standard scenario results
        if 'Standard (1000 steps)' in self.results:
            std_results = self.results['Standard (1000 steps)']
            
            print("Performance Ranking (by survival steps):")
            rankings = []
            for model_name, data in std_results.items():
                rankings.append((
                    model_name,
                    data['performance']['steps_mean']
                ))
            
            rankings.sort(key=lambda x: x[1], reverse=True)
            
            for i, (model_name, steps) in enumerate(rankings, 1):
                print(f"  {i}. {model_name}: {steps:.1f} steps")
            
            # Relative performance
            if len(rankings) > 1:
                best_steps = rankings[0][1]
                print(f"\nRelative to {rankings[0][0]}:")
                for model_name, steps in rankings[1:]:
                    ratio = (steps / best_steps) * 100
                    print(f"  {model_name}: {ratio:.1f}%")
            
            # Speed comparison
            print(f"\nInference Speed:")
            for model_name, data in std_results.items():
                speed = data['inference_speed']['mean_ms']
                print(f"  {model_name}: {speed:.2f} ms")


def main():
    """Run comprehensive benchmark"""
    
    # Define test scenarios
    scenarios = {
        'Standard (1000 steps)': {
            'max_steps': 1000,
            'description': 'Standard test with 1000 max steps'
        },
        'Long Episode (5000 steps)': {
            'max_steps': 5000,
            'description': 'Extended test with 5000 max steps'
        },
        'Short Episode (500 steps)': {
            'max_steps': 500,
            'description': 'Quick test with 500 max steps'
        }
    }
    
    # Run benchmark
    benchmark = DroneBenchmark()
    benchmark.run_benchmark(scenarios, num_episodes=10)
    
    print("\n" + "="*60)
    print("BENCHMARK COMPLETE!")
    print("="*60)


if __name__ == "__main__":
    main()

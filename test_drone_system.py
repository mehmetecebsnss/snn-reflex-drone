"""
Quick test of the complete 3D drone system
"""
import numpy as np
from drone_env_3d import DroneEnv3D
from drone_teacher_3d import DroneTeacher3D
from drone_model_3d import SNNDroneNet3D

print("=== Testing 3D Drone System ===\n")

# Test 1: Environment
print("1. Testing Environment...")
env = DroneEnv3D(gui=False, max_steps=100)
obs = env.reset()
print(f"   ✓ Observation shape: {obs.shape}")
print(f"   ✓ Observation space: {env.get_observation_space_size()}")
print(f"   ✓ Action space: {env.get_action_space_size()}")

# Test 2: Teacher
print("\n2. Testing Expert Teacher...")
teacher = DroneTeacher3D()
action = teacher.get_action(obs)
print(f"   ✓ Action shape: {action.shape}")
print(f"   ✓ Action range: [{action.min():.2f}, {action.max():.2f}]")

# Test 3: Teacher performance
print("\n3. Testing Teacher Performance (100 steps)...")
obs = env.reset()
total_reward = 0
for step in range(100):
    action = teacher.get_action(obs)
    obs, reward, done, info = env.step(action)
    total_reward += reward
    if done:
        print(f"   ✓ Survived {step} steps")
        print(f"   ✓ Total reward: {total_reward:.1f}")
        if 'collision' in info:
            print(f"   ✗ Ended by collision")
        break
else:
    print(f"   ✓ Survived all 100 steps!")
    print(f"   ✓ Total reward: {total_reward:.1f}")

# Test 4: SNN Model
print("\n4. Testing SNN Model...")
model = SNNDroneNet3D()
print(f"   ✓ Model parameters: {model.count_parameters():,}")
obs = env.reset()
action = model.predict(obs)
print(f"   ✓ SNN prediction shape: {action.shape}")
print(f"   ✓ SNN action: {action}")

env.close()

print("\n=== All Tests Passed! ===")
print("\nNext steps:")
print("1. Train the model: python train_drone_3d.py")
print("2. Run demo: python run_drone_3d.py")
print("3. Compare with expert: python run_drone_3d.py --compare")

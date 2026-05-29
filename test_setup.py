"""
Quick test script to verify installation and basic functionality
"""
import sys

def test_imports():
    """Test if all required packages are installed"""
    print("Testing imports...")
    
    try:
        import numpy as np
        print("✓ numpy")
    except ImportError:
        print("✗ numpy - Run: pip install numpy")
        return False
    
    try:
        import pygame
        print("✓ pygame")
    except ImportError:
        print("✗ pygame - Run: pip install pygame")
        return False
    
    try:
        import torch
        print("✓ torch")
    except ImportError:
        print("✗ torch - Run: pip install torch")
        return False
    
    try:
        import snntorch
        print("✓ snntorch")
    except ImportError:
        print("✗ snntorch - Run: pip install snntorch")
        return False
    
    try:
        import matplotlib
        print("✓ matplotlib")
    except ImportError:
        print("✗ matplotlib - Run: pip install matplotlib")
        return False
    
    try:
        import tqdm
        print("✓ tqdm")
    except ImportError:
        print("✗ tqdm - Run: pip install tqdm")
        return False
    
    return True


def test_modules():
    """Test if project modules can be imported"""
    print("\nTesting project modules...")
    
    try:
        import config
        print("✓ config.py")
    except ImportError as e:
        print(f"✗ config.py - {e}")
        return False
    
    try:
        import env
        print("✓ env.py")
    except ImportError as e:
        print(f"✗ env.py - {e}")
        return False
    
    try:
        import encoder
        print("✓ encoder.py")
    except ImportError as e:
        print(f"✗ encoder.py - {e}")
        return False
    
    try:
        import teacher
        print("✓ teacher.py")
    except ImportError as e:
        print(f"✗ teacher.py - {e}")
        return False
    
    try:
        import model
        print("✓ model.py")
    except ImportError as e:
        print(f"✗ model.py - {e}")
        return False
    
    try:
        import baseline
        print("✓ baseline.py")
    except ImportError as e:
        print(f"✗ baseline.py - {e}")
        return False
    
    return True


def test_environment():
    """Test if environment works"""
    print("\nTesting environment...")
    
    try:
        from env import ObstacleEnv
        env = ObstacleEnv()
        state = env.reset()
        print(f"✓ Environment created")
        print(f"  Initial state shape: {state.shape}")
        print(f"  Sensor values: {state}")
        
        # Test step
        next_state, reward, done = env.step(1)
        print(f"✓ Environment step works")
        print(f"  Reward: {reward}, Done: {done}")
        
        return True
    except Exception as e:
        print(f"✗ Environment test failed - {e}")
        return False


def test_teacher():
    """Test teacher policy"""
    print("\nTesting teacher policy...")
    
    try:
        import numpy as np
        from teacher import teacher_policy
        
        # Test cases
        test_states = [
            np.array([0.8, 0.1, 0.8]),  # Front blocked
            np.array([0.8, 0.8, 0.8]),  # All clear
            np.array([0.1, 0.8, 0.8]),  # Left blocked
            np.array([0.8, 0.8, 0.1]),  # Right blocked
        ]
        
        for i, state in enumerate(test_states):
            action = teacher_policy(state)
            action_name = ['LEFT', 'STRAIGHT', 'RIGHT'][action]
            print(f"✓ Test {i+1}: state={state} → {action_name}")
        
        return True
    except Exception as e:
        print(f"✗ Teacher policy test failed - {e}")
        return False


def test_models():
    """Test if models can be instantiated"""
    print("\nTesting models...")
    
    try:
        import torch
        from model import SNNReflexNet
        from baseline import ANNBaseline
        
        snn = SNNReflexNet()
        print(f"✓ SNN model created")
        
        ann = ANNBaseline()
        print(f"✓ ANN model created")
        
        # Test forward pass
        dummy_input = torch.randn(20, 1, 3)  # [time, batch, features]
        spk, mem = snn(dummy_input)
        print(f"✓ SNN forward pass works")
        print(f"  Output shape: {mem.shape}")
        
        dummy_input_ann = torch.randn(1, 3)
        output = ann(dummy_input_ann)
        print(f"✓ ANN forward pass works")
        print(f"  Output shape: {output.shape}")
        
        return True
    except Exception as e:
        print(f"✗ Model test failed - {e}")
        return False


def main():
    print("=" * 60)
    print("SNN-Reflex Setup Test")
    print("=" * 60)
    print()
    
    all_passed = True
    
    # Run tests
    if not test_imports():
        all_passed = False
        print("\n⚠️  Some packages are missing. Install them with:")
        print("   pip install -r requirements.txt")
    
    if not test_modules():
        all_passed = False
    
    if not test_environment():
        all_passed = False
    
    if not test_teacher():
        all_passed = False
    
    if not test_models():
        all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("\nYou're ready to start training:")
        print("  python train.py")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease fix the issues above before training.")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

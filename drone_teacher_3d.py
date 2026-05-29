"""
Expert teacher policy for 3D drone obstacle avoidance
Rule-based controller for generating training data
"""
import numpy as np


class DroneTeacher3D:
    """
    Rule-based expert for 3D drone navigation
    
    Strategy:
    1. Maintain altitude around 3-5m
    2. Avoid obstacles using distance sensors
    3. Move forward slowly while avoiding
    4. Use yaw to turn away from obstacles
    """
    
    def __init__(self):
        self.target_altitude = 4.0  # meters
        self.safe_distance = 2.0    # meters
        self.cruise_speed = 2.0     # m/s
    
    def get_action(self, observation: np.ndarray) -> np.ndarray:
        """
        Generate expert action based on observation
        
        Args:
            observation: [17] array
                [0:8]   - distances (front, back, left, right, up, down, front-left, front-right)
                [8:11]  - velocity (vx, vy, vz)
                [11:14] - angular velocity (wx, wy, wz)
                [14:17] - orientation (roll, pitch, yaw)
        
        Returns:
            action: [4] array [thrust, roll_rate, pitch_rate, yaw_rate] in [-1, 1]
        """
        # Parse observation
        distances = observation[0:8]
        velocity = observation[8:11]
        ang_velocity = observation[11:14]
        orientation = observation[14:17]  # roll, pitch, yaw
        
        # Denormalize distances
        distances_real = distances * 5.0  # max_sensor_dist = 5.0
        
        # Extract specific sensors
        front_dist = distances_real[0]
        back_dist = distances_real[1]
        left_dist = distances_real[2]
        right_dist = distances_real[3]
        up_dist = distances_real[4]
        down_dist = distances_real[5]
        front_left_dist = distances_real[6]
        front_right_dist = distances_real[7]
        
        vx, vy, vz = velocity
        roll, pitch, yaw = orientation
        
        # Initialize action
        thrust = 0.0
        roll_rate = 0.0
        pitch_rate = 0.0
        yaw_rate = 0.0
        
        # === 1. ALTITUDE CONTROL ===
        current_altitude = down_dist  # distance to ground
        altitude_error = self.target_altitude - current_altitude
        
        # Thrust control (PD controller)
        thrust = np.clip(0.5 + altitude_error * 0.2 - vz * 0.1, 0, 1)
        thrust = (thrust * 2) - 1  # Convert to [-1, 1]
        
        # === 2. OBSTACLE AVOIDANCE ===
        # Check if any obstacle is too close
        min_front_dist = min(front_dist, front_left_dist, front_right_dist)
        
        if min_front_dist < self.safe_distance:
            # DANGER! Need to avoid
            
            # Decide turn direction based on left/right clearance
            if left_dist > right_dist:
                # Turn left
                yaw_rate = 0.8
            else:
                # Turn right
                yaw_rate = -0.8
            
            # Slow down forward motion
            pitch_rate = 0.3  # Pitch back to slow down
            
        else:
            # Safe to move forward
            
            # Gentle forward motion
            if vx < self.cruise_speed:
                pitch_rate = -0.2  # Pitch forward slightly
            else:
                pitch_rate = 0.1  # Level out
            
            # Fine-tune yaw to center between obstacles
            if front_left_dist < front_right_dist and front_left_dist < 3.0:
                yaw_rate = -0.3  # Turn slightly right
            elif front_right_dist < front_left_dist and front_right_dist < 3.0:
                yaw_rate = 0.3   # Turn slightly left
            else:
                yaw_rate = 0.0
        
        # === 3. SIDE OBSTACLE AVOIDANCE ===
        if left_dist < 1.5:
            roll_rate = -0.5  # Roll right to move away
        elif right_dist < 1.5:
            roll_rate = 0.5   # Roll left to move away
        
        # === 4. STABILIZATION ===
        # Dampen excessive roll/pitch
        roll_rate -= roll * 0.5
        pitch_rate -= pitch * 0.5
        
        # Dampen angular velocities
        roll_rate -= ang_velocity[0] * 0.3
        pitch_rate -= ang_velocity[1] * 0.3
        yaw_rate -= ang_velocity[2] * 0.3
        
        # === 5. EMERGENCY MANEUVERS ===
        # If too close to ground
        if down_dist < 1.0:
            thrust = 1.0  # Full thrust up!
            pitch_rate = 0.0
            roll_rate = 0.0
        
        # If too close to ceiling
        if up_dist < 1.0:
            thrust = -0.5  # Reduce thrust
        
        # If back obstacle (shouldn't happen often)
        if back_dist < 1.0:
            pitch_rate = -0.5  # Pitch forward to move away
        
        # Clip all actions to [-1, 1]
        action = np.array([
            np.clip(thrust, -1, 1),
            np.clip(roll_rate, -1, 1),
            np.clip(pitch_rate, -1, 1),
            np.clip(yaw_rate, -1, 1)
        ], dtype=np.float32)
        
        return action
    
    def get_action_simple(self, observation: np.ndarray) -> np.ndarray:
        """
        Simplified expert action (for easier learning)
        Focus only on front obstacle avoidance and altitude
        """
        distances = observation[0:8]
        velocity = observation[8:11]
        orientation = observation[14:17]
        
        distances_real = distances * 5.0
        
        front_dist = distances_real[0]
        left_dist = distances_real[2]
        right_dist = distances_real[3]
        down_dist = distances_real[5]
        
        vz = velocity[2]
        
        # Altitude control
        altitude_error = self.target_altitude - down_dist
        thrust = np.clip(0.5 + altitude_error * 0.2 - vz * 0.1, 0, 1)
        thrust = (thrust * 2) - 1
        
        # Simple obstacle avoidance
        if front_dist < 2.0:
            if left_dist > right_dist:
                yaw_rate = 0.8
            else:
                yaw_rate = -0.8
            pitch_rate = 0.2
        else:
            yaw_rate = 0.0
            pitch_rate = -0.1
        
        roll_rate = 0.0
        
        action = np.array([thrust, roll_rate, pitch_rate, yaw_rate], dtype=np.float32)
        return np.clip(action, -1, 1)


def collect_expert_data(env, teacher, num_samples=10000, simple=False):
    """
    Collect expert demonstrations
    
    Args:
        env: DroneEnv3D instance
        teacher: DroneTeacher3D instance
        num_samples: number of samples to collect
        simple: use simple policy
    
    Returns:
        observations: [N, 17] array
        actions: [N, 4] array
    """
    observations = []
    actions = []
    
    obs = env.reset()
    episode_count = 0
    
    print(f"Collecting {num_samples} expert samples...")
    
    while len(observations) < num_samples:
        # Get expert action
        if simple:
            action = teacher.get_action_simple(obs)
        else:
            action = teacher.get_action(obs)
        
        # Store
        observations.append(obs)
        actions.append(action)
        
        # Step environment
        obs, reward, done, info = env.step(action)
        
        if done:
            episode_count += 1
            obs = env.reset()
            
            if len(observations) % 1000 == 0:
                print(f"Collected {len(observations)}/{num_samples} samples, Episodes: {episode_count}")
    
    observations = np.array(observations)
    actions = np.array(actions)
    
    print(f"Data collection complete! Episodes: {episode_count}")
    print(f"Observations shape: {observations.shape}")
    print(f"Actions shape: {actions.shape}")
    
    return observations, actions


if __name__ == "__main__":
    # Test teacher policy
    from drone_env_3d import DroneEnv3D
    
    print("Testing DroneTeacher3D...")
    env = DroneEnv3D(gui=True, max_steps=500)
    teacher = DroneTeacher3D()
    
    obs = env.reset()
    total_reward = 0
    
    for step in range(500):
        action = teacher.get_action(obs)
        obs, reward, done, info = env.step(action)
        total_reward += reward
        
        if done:
            print(f"Episode ended at step {step}")
            print(f"Total reward: {total_reward}")
            print(f"Info: {info}")
            break
    
    env.close()
    print(f"Teacher test complete! Survived {step} steps")

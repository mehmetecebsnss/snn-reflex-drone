"""
3D Drone Environment with Obstacle Avoidance
Using PyBullet physics simulation
"""
import numpy as np
import pybullet as p
import pybullet_data
from typing import Tuple, List


class DroneEnv3D:
    """
    3D Drone environment with obstacles and LiDAR-like sensors
    
    Task: Navigate through 3D space while avoiding obstacles
    Sensors: 8 distance sensors (front, back, left, right, up, down, front-left, front-right)
    Actions: [thrust, roll, pitch, yaw_rate]
    """
    
    def __init__(self, gui=True, max_steps=1000):
        self.gui = gui
        self.max_steps = max_steps
        self.step_count = 0
        
        # Connect to PyBullet
        if gui:
            self.client = p.connect(p.GUI)
        else:
            self.client = p.connect(p.DIRECT)
        
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -9.81)
        
        # Environment bounds (increased for more space)
        self.bounds = {
            'x': [-15, 15],  # Increased from [-10, 10]
            'y': [-15, 15],  # Increased from [-10, 10]
            'z': [0, 12]     # Increased from [0, 10]
        }
        
        # Sensor configuration (8 directions)
        self.sensor_angles = [
            (0, 0),      # front
            (180, 0),    # back
            (90, 0),     # left
            (-90, 0),    # right
            (0, 90),     # up
            (0, -90),    # down
            (45, 0),     # front-left
            (-45, 0),    # front-right
        ]
        self.max_sensor_dist = 5.0
        self.num_sensors = len(self.sensor_angles)
        
        # Drone parameters
        self.drone_mass = 0.5  # kg
        self.drone_radius = 0.2
        
        # Physics parameters (more forgiving for trained models)
        self.collision_margin = 0.05  # Small margin for collision detection
        
        # Initialize environment
        self.drone_id = None
        self.obstacle_ids = []
        self.reset()
    
    def reset(self) -> np.ndarray:
        """Reset environment and return initial observation"""
        # Remove existing objects
        if self.drone_id is not None:
            p.removeBody(self.drone_id)
        for obs_id in self.obstacle_ids:
            p.removeBody(obs_id)
        self.obstacle_ids = []
        
        # Create ground plane
        p.loadURDF("plane.urdf")
        
        # Create drone (realistic quadcopter model)
        drone_start_pos = [0, 0, 2]
        drone_start_orientation = p.getQuaternionFromEuler([0, 0, 0])
        
        # Try to load URDF, fallback to sphere if not found
        try:
            self.drone_id = p.loadURDF("data/quadcopter.urdf", 
                                      drone_start_pos, 
                                      drone_start_orientation)
            # Set collision margin for better physics
            p.setCollisionFilterGroupMask(self.drone_id, -1, 1, 1)
        except:
            # Fallback to sphere if URDF not found
            collision_shape = p.createCollisionShape(p.GEOM_SPHERE, radius=self.drone_radius)
            visual_shape = p.createVisualShape(p.GEOM_SPHERE, radius=self.drone_radius, 
                                              rgbaColor=[0, 0, 1, 1])
            
            self.drone_id = p.createMultiBody(
                baseMass=self.drone_mass,
                baseCollisionShapeIndex=collision_shape,
                baseVisualShapeIndex=visual_shape,
                basePosition=drone_start_pos,
                baseOrientation=drone_start_orientation
            )
        
        # Create random obstacles (cylinders and boxes)
        self._create_obstacles()
        
        self.step_count = 0
        
        return self._get_observation()
    
    def _create_obstacles(self):
        """Create random obstacles in the environment"""
        num_obstacles = 12  # Reduced from 15 for easier navigation
        
        for i in range(num_obstacles):
            # Random position (avoid spawn area)
            x = np.random.uniform(-8, 8)
            y = np.random.uniform(-8, 8)
            z = np.random.uniform(0.5, 6)
            
            # Skip if too close to drone start
            if np.sqrt(x**2 + y**2) < 3:
                continue
            
            # Random obstacle type
            if np.random.rand() > 0.5:
                # Cylinder (pole)
                height = np.random.uniform(2, 8)
                radius = np.random.uniform(0.2, 0.5)
                collision_shape = p.createCollisionShape(p.GEOM_CYLINDER, 
                                                        radius=radius, height=height)
                visual_shape = p.createVisualShape(p.GEOM_CYLINDER, 
                                                  radius=radius, length=height,
                                                  rgbaColor=[0.7, 0.3, 0.3, 1])
                pos = [x, y, height/2]
            else:
                # Box
                half_extents = [np.random.uniform(0.3, 1.0) for _ in range(3)]
                collision_shape = p.createCollisionShape(p.GEOM_BOX, 
                                                        halfExtents=half_extents)
                visual_shape = p.createVisualShape(p.GEOM_BOX, 
                                                  halfExtents=half_extents,
                                                  rgbaColor=[0.5, 0.5, 0.5, 1])
                pos = [x, y, z]
            
            obs_id = p.createMultiBody(
                baseMass=0,  # static
                baseCollisionShapeIndex=collision_shape,
                baseVisualShapeIndex=visual_shape,
                basePosition=pos
            )
            self.obstacle_ids.append(obs_id)
    
    def _get_observation(self) -> np.ndarray:
        """
        Get sensor readings (LiDAR-like distance measurements)
        
        Returns:
            obs: [8 distances, 3 velocity, 3 angular_velocity, 3 orientation] = 17 values
        """
        # Get drone state
        pos, orn = p.getBasePositionAndOrientation(self.drone_id)
        vel, ang_vel = p.getBaseVelocity(self.drone_id)
        euler = p.getEulerFromQuaternion(orn)
        
        # Get distance sensors
        distances = self._get_distance_sensors()
        
        # Normalize distances [0, 1] where 0=collision, 1=safe
        normalized_distances = np.array(distances) / self.max_sensor_dist
        normalized_distances = np.clip(normalized_distances, 0, 1)
        
        # Combine all observations
        obs = np.concatenate([
            normalized_distances,  # 8 values
            np.array(vel),         # 3 values
            np.array(ang_vel),     # 3 values
            np.array(euler)        # 3 values (roll, pitch, yaw)
        ])
        
        return obs.astype(np.float32)
    
    def _get_distance_sensors(self) -> List[float]:
        """Ray casting for distance measurements in 8 directions"""
        pos, orn = p.getBasePositionAndOrientation(self.drone_id)
        rotation_matrix = p.getMatrixFromQuaternion(orn)
        rotation_matrix = np.array(rotation_matrix).reshape(3, 3)
        
        distances = []
        
        for yaw_deg, pitch_deg in self.sensor_angles:
            # Convert to radians
            yaw = np.radians(yaw_deg)
            pitch = np.radians(pitch_deg)
            
            # Direction vector in drone's local frame
            local_dir = np.array([
                np.cos(pitch) * np.cos(yaw),
                np.cos(pitch) * np.sin(yaw),
                np.sin(pitch)
            ])
            
            # Transform to world frame
            world_dir = rotation_matrix @ local_dir
            
            # Ray cast
            ray_from = pos
            ray_to = np.array(pos) + world_dir * self.max_sensor_dist
            
            result = p.rayTest(ray_from, ray_to.tolist())
            
            if result[0][0] == -1:  # No hit
                distances.append(self.max_sensor_dist)
            else:
                hit_fraction = result[0][2]
                distances.append(hit_fraction * self.max_sensor_dist)
        
        return distances
    
    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, dict]:
        """
        Execute action and return next state
        
        Args:
            action: [thrust, roll_rate, pitch_rate, yaw_rate] normalized [-1, 1]
        
        Returns:
            observation, reward, done, info
        """
        # Parse action
        thrust = (action[0] + 1) / 2  # [0, 1]
        roll_rate = action[1] * 2     # [-2, 2] rad/s
        pitch_rate = action[2] * 2
        yaw_rate = action[3] * 2
        
        # Get current state
        pos, orn = p.getBasePositionAndOrientation(self.drone_id)
        vel, ang_vel = p.getBaseVelocity(self.drone_id)
        
        # Apply thrust (simplified physics)
        thrust_force = thrust * self.drone_mass * 9.81 * 2  # 2x gravity for maneuverability
        rotation_matrix = p.getMatrixFromQuaternion(orn)
        rotation_matrix = np.array(rotation_matrix).reshape(3, 3)
        thrust_world = rotation_matrix @ np.array([0, 0, thrust_force])
        
        p.applyExternalForce(self.drone_id, -1, thrust_world.tolist(), pos, p.WORLD_FRAME)
        
        # Apply angular velocities (simplified)
        p.applyExternalTorque(self.drone_id, -1, 
                             [roll_rate * 0.1, pitch_rate * 0.1, yaw_rate * 0.1],
                             p.WORLD_FRAME)
        
        # Step simulation
        p.stepSimulation()
        
        # Get new observation
        obs = self._get_observation()
        
        # Calculate reward
        reward, done, info = self._calculate_reward()
        
        self.step_count += 1
        if self.step_count >= self.max_steps:
            done = True
            info['timeout'] = True
        
        return obs, reward, done, info
    
    def _calculate_reward(self) -> Tuple[float, bool, dict]:
        """Calculate reward based on drone state"""
        pos, orn = p.getBasePositionAndOrientation(self.drone_id)
        vel, ang_vel = p.getBaseVelocity(self.drone_id)
        
        reward = 0.0
        done = False
        info = {}
        
        # Survival reward
        reward += 1.0
        
        # Check collision (with small tolerance)
        contact_points = p.getContactPoints(self.drone_id)
        # Filter out very light contacts (allow gentle touches)
        significant_contacts = [c for c in contact_points if len(c) > 8 and abs(c[9]) > 0.1]
        if len(significant_contacts) > 0:
            reward -= 100.0
            done = True
            info['collision'] = True
            return reward, done, info
        
        # Check bounds (with soft penalty zone)
        x, y, z = pos
        
        # Hard bounds (terminate)
        if (x < self.bounds['x'][0] or x > self.bounds['x'][1] or
            y < self.bounds['y'][0] or y > self.bounds['y'][1] or
            z < self.bounds['z'][0] or z > self.bounds['z'][1]):
            reward -= 50.0
            done = True
            info['out_of_bounds'] = True
            return reward, done, info
        
        # Soft penalty zone (encourage staying in center)
        soft_bounds = 10.0
        if abs(x) > soft_bounds or abs(y) > soft_bounds:
            penalty = (max(abs(x), abs(y)) - soft_bounds) * 0.5
            reward -= penalty
        
        # Penalty for high velocity (encourage smooth flight)
        speed = np.linalg.norm(vel)
        if speed > 5.0:
            reward -= 0.1 * (speed - 5.0)
        
        # Bonus for staying in center area
        dist_from_center = np.sqrt(x**2 + y**2)
        if dist_from_center < 5.0:
            reward += 0.5
        
        # Penalty for extreme orientations
        euler = p.getEulerFromQuaternion(orn)
        tilt = np.sqrt(euler[0]**2 + euler[1]**2)  # roll and pitch
        if tilt > np.pi/3:  # More than 60 degrees
            reward -= 1.0
        
        return reward, done, info
    
    def render(self):
        """Rendering is handled by PyBullet GUI"""
        pass
    
    def close(self):
        """Close the environment"""
        p.disconnect(self.client)
    
    def get_observation_space_size(self) -> int:
        """Return size of observation space"""
        return 17  # 8 distances + 3 vel + 3 ang_vel + 3 orientation
    
    def get_action_space_size(self) -> int:
        """Return size of action space"""
        return 4  # thrust, roll_rate, pitch_rate, yaw_rate


if __name__ == "__main__":
    # Test the environment
    print("Testing DroneEnv3D...")
    env = DroneEnv3D(gui=True)
    
    obs = env.reset()
    print(f"Observation shape: {obs.shape}")
    print(f"Initial observation: {obs}")
    
    # Random actions for testing
    for i in range(1000):
        action = np.random.uniform(-1, 1, 4)
        obs, reward, done, info = env.step(action)
        
        if done:
            print(f"Episode ended at step {i}")
            print(f"Info: {info}")
            obs = env.reset()
    
    env.close()

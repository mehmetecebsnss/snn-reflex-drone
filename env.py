"""
2D Environment for agent navigation with obstacle avoidance
"""
import math
import random
import pygame
import numpy as np
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, AGENT_SPEED, 
    TURN_ANGLE, SENSOR_ANGLES, MAX_SENSOR_DIST
)


class Agent:
    """Simple agent that moves forward and can turn"""
    
    def __init__(self, x=100, y=300, angle=0):
        self.x = x
        self.y = y
        self.angle = angle
        self.radius = 10
        self.alive = True
    
    def step(self, action):
        """
        Execute action:
        0 = turn left
        1 = go straight
        2 = turn right
        """
        if action == 0:
            self.angle -= TURN_ANGLE
        elif action == 2:
            self.angle += TURN_ANGLE
        
        # Move forward
        rad = math.radians(self.angle)
        self.x += AGENT_SPEED * math.cos(rad)
        self.y += AGENT_SPEED * math.sin(rad)
    
    def pos(self):
        return np.array([self.x, self.y], dtype=np.float32)


class ObstacleEnv:
    """2D environment with obstacles and walls"""
    
    def __init__(self):
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        self.agent = None
        self.obstacles = []
        self.reset()
    
    def reset(self):
        """Reset environment with new obstacles"""
        self.agent = Agent()
        self.obstacles = self._generate_obstacles()
        return self.get_state()
    
    def _generate_obstacles(self):
        """Generate random rectangular obstacles"""
        obs = []
        for _ in range(8):
            w = random.randint(40, 100)
            h = random.randint(40, 100)
            x = random.randint(200, self.width - w - 20)
            y = random.randint(20, self.height - h - 20)
            obs.append(pygame.Rect(x, y, w, h))
        return obs
    
    def _point_hits(self, px, py):
        """Check if point hits wall or obstacle"""
        # Check walls
        if px < 0 or px >= self.width or py < 0 or py >= self.height:
            return True
        
        # Check obstacles
        point = pygame.Rect(px, py, 2, 2)
        for o in self.obstacles:
            if o.colliderect(point):
                return True
        return False
    
    def get_sensors(self):
        """
        Get sensor readings in three directions
        Returns normalized distances [0,1] where 1 = safe, 0 = very close
        """
        readings = []
        for rel_ang in SENSOR_ANGLES:
            ang = math.radians(self.agent.angle + rel_ang)
            dist = MAX_SENSOR_DIST
            
            # Ray cast to find obstacle
            for d in range(0, MAX_SENSOR_DIST, 3):
                px = self.agent.x + d * math.cos(ang)
                py = self.agent.y + d * math.sin(ang)
                if self._point_hits(px, py):
                    dist = d
                    break
            
            # Normalize to [0, 1]
            readings.append(dist / MAX_SENSOR_DIST)
        
        return np.array(readings, dtype=np.float32)
    
    def get_state(self):
        """Get current state (sensor readings)"""
        return self.get_sensors()
    
    def _collision(self):
        """Check if agent collided with obstacle or wall"""
        return self._point_hits(self.agent.x, self.agent.y)
    
    def step(self, action):
        """
        Execute action and return next state
        Returns: (state, reward, done)
        """
        self.agent.step(action)
        done = self._collision()
        reward = 1.0 if not done else -10.0
        return self.get_state(), reward, done
    
    def render(self, screen):
        """Render environment to pygame screen"""
        # Background
        screen.fill((20, 20, 20))
        
        # Obstacles
        for o in self.obstacles:
            pygame.draw.rect(screen, (180, 60, 60), o)
        
        # Sensor rays
        for rel_ang, val in zip(SENSOR_ANGLES, self.get_sensors()):
            ang = math.radians(self.agent.angle + rel_ang)
            dist = val * MAX_SENSOR_DIST
            endx = self.agent.x + dist * math.cos(ang)
            endy = self.agent.y + dist * math.sin(ang)
            pygame.draw.line(screen, (80, 200, 255), 
                           (self.agent.x, self.agent.y), 
                           (endx, endy), 2)
        
        # Agent
        pygame.draw.circle(screen, (240, 240, 100), 
                         (int(self.agent.x), int(self.agent.y)), 
                         self.agent.radius)

"""
Rule-based teacher policy for generating training labels
"""
import numpy as np


def teacher_policy(state):
    """
    Simple rule-based policy for obstacle avoidance
    
    Args:
        state: [left, front, right] normalized distances
    
    Returns:
        action: 0 (left), 1 (straight), 2 (right)
    """
    left, front, right = state
    
    # Convert to danger (inverse of distance)
    danger_front = 1.0 - front
    danger_left = 1.0 - left
    danger_right = 1.0 - right
    
    # Critical: front obstacle very close
    if front < 0.25:
        return 0 if left > right else 2
    
    # Warning: front obstacle moderately close
    if front < 0.45:
        if left > right + 0.1:
            return 0  # Turn left
        elif right > left + 0.1:
            return 2  # Turn right
        else:
            return 1  # Go straight
    
    # Side obstacles
    if left < 0.2:
        return 2  # Turn away from left wall
    if right < 0.2:
        return 0  # Turn away from right wall
    
    # Default: go straight
    return 1

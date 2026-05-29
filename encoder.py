"""
Spike encoding for converting sensor data to spike trains
"""
import torch
from config import TIME_STEPS


def rate_encode(states, time_steps=TIME_STEPS):
    """
    Rate encoding: convert normalized distances to spike trains
    
    Higher danger (closer obstacle) = more spikes
    
    Args:
        states: [batch, 3] normalized distances [0,1]
        time_steps: number of time steps for spike train
    
    Returns:
        spikes: [time_steps, batch, 3] binary spike tensor
    """
    # Convert distance to danger
    danger = 1.0 - states
    
    batch_size, input_size = danger.shape
    
    # Generate random values for Poisson-like encoding
    spikes = torch.rand(time_steps, batch_size, input_size, device=states.device)
    
    # Spike if random value < danger level
    return (spikes < danger.unsqueeze(0)).float()

"""
Run live simulation with trained SNN model
"""
import pygame
import torch
import numpy as np

from config import SCREEN_WIDTH, SCREEN_HEIGHT, DEVICE
from env import ObstacleEnv
from encoder import rate_encode
from model import SNNReflexNet


def main():
    print("=== SNN Reflex Live Demo ===\n")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("SNN Reflex - Live Demo")
    clock = pygame.time.Clock()
    
    # Create environment
    env = ObstacleEnv()
    
    # Load model
    print("Loading trained model...")
    model = SNNReflexNet().to(DEVICE)
    try:
        model.load_state_dict(torch.load("checkpoints/snn_reflex.pt", map_location=DEVICE))
        model.eval()
        print("Model loaded successfully!\n")
    except FileNotFoundError:
        print("ERROR: Model not found. Please run train.py first.")
        return
    
    # Initialize
    state = env.reset()
    running = True
    steps = 0
    episodes = 0
    total_steps = 0
    
    # Font for stats
    font = pygame.font.Font(None, 24)
    
    print("Controls:")
    print("  SPACE - Reset environment")
    print("  ESC   - Quit")
    print("\nRunning simulation...\n")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    state = env.reset()
                    steps = 0
        
        # Get action from SNN
        with torch.no_grad():
            states = torch.tensor(state, dtype=torch.float32, device=DEVICE).unsqueeze(0)
            spikes = rate_encode(states)
            _, mem = model(spikes)
            logits = mem.sum(dim=0)
            action = logits.argmax(dim=1).item()
        
        # Step environment
        state, reward, done = env.step(action)
        steps += 1
        
        if done:
            episodes += 1
            total_steps += steps
            avg_steps = total_steps / episodes
            print(f"Episode {episodes} ended after {steps} steps (avg: {avg_steps:.1f})")
            state = env.reset()
            steps = 0
        
        # Render
        env.render(screen)
        
        # Draw stats
        stats_text = [
            f"Episode: {episodes}",
            f"Steps: {steps}",
            f"Avg: {total_steps/max(episodes,1):.1f}",
            f"Action: {['LEFT', 'STRAIGHT', 'RIGHT'][action]}"
        ]
        
        for i, text in enumerate(stats_text):
            surf = font.render(text, True, (255, 255, 255))
            screen.blit(surf, (10, 10 + i * 25))
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()
    print(f"\nSimulation ended.")
    print(f"Total episodes: {episodes}")
    print(f"Average survival: {total_steps/max(episodes,1):.1f} steps")


if __name__ == "__main__":
    main()

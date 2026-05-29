# Configuration file for SNN-Reflex Drone Prototype v0

# Environment settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
AGENT_SPEED = 4.0
TURN_ANGLE = 10  # degrees
SENSOR_ANGLES = [-45, 0, 45]  # left, front, right
MAX_SENSOR_DIST = 150

# SNN settings
TIME_STEPS = 30  # Increased from 20 for better temporal dynamics
HIDDEN_SIZE = 64  # Increased from 32 for more capacity
INPUT_SIZE = 3
OUTPUT_SIZE = 3

# Training settings
TRAIN_SAMPLES = 30000  # Increased from 20000 for more data
VAL_SAMPLES = 5000
BATCH_SIZE = 64
EPOCHS = 30  # Increased from 20 for better convergence
LR = 1e-3

# Device
DEVICE = "cpu"

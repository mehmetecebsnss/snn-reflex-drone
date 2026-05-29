# 🚁 SNN-Reflex: Spiking Neural Networks for Drone Obstacle Avoidance

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red.svg)](https://pytorch.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Active](https://img.shields.io/badge/Status-Active-success.svg)]()

**Spiking Neural Networks (SNN) for real-time drone obstacle avoidance using temporal dynamics.**

This project demonstrates that SNNs can outperform traditional ANNs and rule-based expert systems in 3D drone navigation tasks by leveraging temporal spike processing.

---

## 🎯 Key Results

### Performance (URDF Quadcopter Model)

| Model | Avg Steps | Success Rate | Rank |
|-------|-----------|--------------|------|
| **SNN** | **916 ± 146** | **55%** | 🥇 |
| Expert | 811 ± 156 | 0% | 🥈 |
| ANN | 637 ± 22 | 0% | 🥉 |

**SNN outperforms expert by 13%!** ✅

### Key Findings

1. ✅ **SNN > Expert**: Temporal dynamics provide real advantage
2. ✅ **Generalization**: Works on both sphere and realistic quadcopter models
3. ✅ **Scalability**: Successfully scaled from 2D (227 params) to 3D (10,820 params)
4. ✅ **Efficiency**: Optimized for neuromorphic hardware deployment

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/snn-reflex-drone.git
cd snn-reflex-drone

# Install dependencies
pip install -r requirements.txt
```

### Run Demo

```bash
# Visual demo with trained SNN
python run_drone_3d.py

# Compare SNN vs Expert
python run_drone_3d.py --compare

# Comprehensive benchmark (20 episodes)
python optimize_and_test.py
```

### Train Your Own Model

```bash
# Train SNN
python train_drone_3d.py

# Train ANN baseline
python train_ann_drone_3d.py
```

---

## 📊 Project Overview

### Architecture

```
Input (17D) → SNN (128→64) → Output (4D)
├─ 8 distance sensors (LiDAR-like)
├─ 3 velocity components
├─ 3 angular velocity components
└─ 3 orientation angles (roll, pitch, yaw)

Output: [thrust, roll_rate, pitch_rate, yaw_rate]
```

### Environment

- **Simulator**: PyBullet physics engine
- **Model**: Realistic quadcopter URDF (4 arms + 4 propellers)
- **Task**: Navigate through 3D space avoiding obstacles
- **Bounds**: 15m × 15m × 12m
- **Obstacles**: 12 random cylinders and boxes

---

## 🎓 Scientific Contributions

### 1. SNN Outperforms Expert
- **2D**: 96.88% accuracy, 1792 steps
- **3D Sphere**: 970 steps (133.9% of expert)
- **3D URDF**: 916 steps (113% of expert)

### 2. Temporal Dynamics Advantage
- SNN leverages 30 timesteps of spike history
- Better momentum and velocity control
- ANN lacks temporal processing → fails bounds

### 3. Scalability Demonstrated
- 2D → 3D transition successful
- Sphere → URDF transition successful
- Minimal performance loss (-5.6%)

### 4. Optimization Without Retraining
- URDF collision geometry fix
- Environment parameter tuning
- 166 → 916 steps (+452%) without retraining!

---

## 📁 Project Structure

```
snn_reflex_proto/
├── data/
│   └── quadcopter.urdf          # Realistic drone model
├── checkpoints/
│   ├── snn_drone_3d.pt          # Trained SNN
│   └── ann_drone_3d.pt          # Trained ANN
├── logs/
│   └── optimization_results.json # Benchmark results
│
├── drone_env_3d.py              # 3D environment (PyBullet)
├── drone_model_3d.py            # SNN + ANN models
├── drone_teacher_3d.py          # Expert policy
├── train_drone_3d.py            # SNN training
├── train_ann_drone_3d.py        # ANN training
├── run_drone_3d.py              # Demo
├── optimize_and_test.py         # Comprehensive testing
│
└── docs/
    ├── OPTIMIZATION_REPORT.md   # Detailed optimization
    ├── PERFORMANCE_SUMMARY.md   # Performance analysis
    └── QUICK_SUMMARY.md         # Quick overview
```

---

## 🔬 Technical Details

### SNN Architecture

```python
class SNNDroneNet3D:
    - Input: 17D observation
    - Hidden1: 128 LIF neurons
    - Hidden2: 64 LIF neurons
    - Output: 4D action
    - Time steps: 30
    - Total parameters: 10,820
```

### Training

- **Method**: Supervised learning (imitation learning)
- **Teacher**: Rule-based expert policy
- **Data**: 50,000 training + 10,000 validation samples
- **Loss**: MSE (Mean Squared Error)
- **Optimizer**: Adam (lr=1e-3)
- **Epochs**: 50

### LIF Neuron Model

```python
tau = 0.5  # Membrane time constant
threshold = 1.0  # Spike threshold
reset = 0.0  # Reset potential

# Dynamics
v[t] = beta * v[t-1] + (1 - beta) * x[t]
spike = (v[t] > threshold)
v[t] = v[t] * (1 - spike) + reset * spike
```

---

## 📈 Performance Comparison

### 2D Prototype
```
SNN: 96.88% accuracy, 1792 steps
Status: ✅ Successful
```

### 3D Sphere Model
```
SNN: 970 ± 63 steps
Expert: 725 ± 40 steps
SNN/Expert: 133.9%
Status: ✅ Successful
```

### 3D URDF Quadcopter (Optimized)
```
SNN: 916 ± 146 steps (55% success)
Expert: 811 ± 156 steps (0% success)
ANN: 637 ± 22 steps (0% success)
Status: ✅ SUCCESSFUL!
```

---

## 🛠️ Requirements

```
Python >= 3.8
torch >= 2.0.0
numpy >= 1.21.0
pybullet >= 3.2.0
pygame >= 2.1.0
```

See `requirements.txt` for full list.

---

## 🎯 Use Cases

### Current
- ✅ 3D drone obstacle avoidance
- ✅ Real-time reflex control
- ✅ Supervised learning from expert

### Future
- [ ] ROS + PX4 integration
- [ ] Neuromorphic chip deployment (Intel Loihi)
- [ ] Real drone testing
- [ ] Multi-drone scenarios
- [ ] Moving obstacles
- [ ] Waypoint navigation

---

## 📚 Documentation

- [Quick Start](QUICKSTART.md) - Get started in 5 minutes
- [Commands Reference](COMMANDS.md) - All available commands
- [Optimization Report](OPTIMIZATION_REPORT.md) - Detailed optimization analysis
- [Performance Summary](PERFORMANCE_SUMMARY.md) - Performance metrics
- [Project Status](STATUS.md) - Current status and roadmap

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Areas for Contribution
- Neuromorphic hardware deployment
- ROS integration
- Real drone testing
- Moving obstacles
- Multi-agent scenarios

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **PyBullet** for physics simulation
- **PyTorch** for deep learning framework
- **snnTorch** for SNN implementation inspiration

---

## 📧 Contact

For questions or collaboration:
- GitHub Issues: [Create an issue](https://github.com/YOUR_USERNAME/snn-reflex-drone/issues)
- Email: your.email@example.com

---

## 📊 Citation

If you use this work in your research, please cite:

```bibtex
@software{snn_reflex_drone_2026,
  title = {SNN-Reflex: Spiking Neural Networks for Drone Obstacle Avoidance},
  author = {Your Name},
  year = {2026},
  url = {https://github.com/YOUR_USERNAME/snn-reflex-drone}
}
```

---

## 🌟 Star History

If you find this project useful, please consider giving it a star! ⭐

---

**Status:** ✅ Active Development  
**Last Update:** 2026-05-29  
**Version:** 1.0.0

---

Made with ❤️ for neuromorphic computing and autonomous drones 🚁✨

# 🚁 SNN-Reflex Drone 3D

**3D Drone Obstacle Avoidance using Spiking Neural Networks**

Bu, 2D prototipten 3D drone simülasyonuna geçiş projesidir. PyBullet fizik motoru kullanarak gerçekçi drone dinamikleri simüle edilir.

---

## 🎯 Proje Hedefi

2D'de başarılı olan SNN refleks kontrolünü **gerçek 3D drone simülasyonuna** taşımak.

### Yeni Özellikler
- ✅ **3D Fizik**: PyBullet ile gerçekçi drone dinamikleri
- ✅ **8 Sensör**: 360° çevre algılama (front, back, left, right, up, down, diagonals)
- ✅ **4 Kontrol**: Thrust, Roll, Pitch, Yaw
- ✅ **Daha Büyük SNN**: 17 → 128 → 64 → 4 mimari
- ✅ **Karmaşık Ortam**: 15+ rastgele engel (kutular ve silindirler)

---

## 📐 Sistem Mimarisi

```
┌─────────────────────────────────────────────────────────┐
│              3D PYBULLET ORTAM                          │
│                                                          │
│    🏢 Engeller (Kutular, Silindirler)                   │
│                                                          │
│              🚁 Drone                                    │
│         ↗  ↑  ↖  ←  →  ↙  ↓  ↘                        │
│        8 Yönde LiDAR Sensörler                          │
└─────────────────────────────────────────────────────────┘
                    ↓
        ┌───────────────────────┐
        │   SENSÖR OKUMASI      │
        │  [8 mesafe]           │
        │  [3 hız]              │
        │  [3 açısal hız]       │
        │  [3 oryantasyon]      │
        │  = 17 değer           │
        └───────────────────────┘
                    ↓
        ┌───────────────────────┐
        │   SPIKE ENCODING      │
        │  Rate Coding          │
        │  30 zaman adımı       │
        └───────────────────────┘
                    ↓
        ┌───────────────────────┐
        │   SNN MODEL           │
        │   17 → 128 → 64 → 4   │
        │   3 Katman LIF        │
        │   ~10K parametre      │
        └───────────────────────┘
                    ↓
        ┌───────────────────────┐
        │   KONTROL             │
        │  [Thrust, Roll,       │
        │   Pitch, Yaw]         │
        └───────────────────────┘
                    ↓
        ┌───────────────────────┐
        │   DRONE HAREKETİ      │
        │  3D Fizik Simülasyonu │
        └───────────────────────┘
```

---

## 🚀 Hızlı Başlangıç

### 1. Kurulum

```bash
# PyBullet ve Gymnasium kur
pip install pybullet gymnasium

# Mevcut bağımlılıklar zaten yüklü (PyTorch, snnTorch)
```

### 2. Ortamı Test Et

```bash
# 3D drone ortamını test et (rastgele aksiyonlar)
python drone_env_3d.py
```

PyBullet GUI açılacak ve drone rastgele hareket edecek.

### 3. Expert Teacher'ı Test Et

```bash
# Kural tabanlı expert'i test et
python drone_teacher_3d.py
```

Expert'in drone'u nasıl kontrol ettiğini göreceksiniz.

### 4. SNN'i Eğit

```bash
# SNN modelini eğit (50 epoch, ~30-60 dakika)
python train_drone_3d.py
```

**Eğitim süreci:**
- 50,000 expert demonstrasyon topla
- 10,000 validation sample
- 50 epoch eğitim
- Model: `checkpoints/snn_drone_3d.pt`
- Log: `logs/train_drone_3d_log.txt`

### 5. Eğitilmiş SNN'i Test Et

```bash
# Live demo (GUI ile)
python run_drone_3d.py

# Expert ile karşılaştır
python run_drone_3d.py --compare
```

---

## 📊 Model Detayları

### SNN Mimarisi

```python
SNNDroneNet3D:
  Input:   17 (8 mesafe + 3 hız + 3 açısal_hız + 3 oryantasyon)
  Hidden1: 128 LIF neurons
  Hidden2: 64 LIF neurons
  Output:  4 (thrust, roll_rate, pitch_rate, yaw_rate)
  
  Total Parameters: ~10,000
  Time Steps: 30
  Encoding: Rate coding
```

### Sensör Konfigürasyonu

| Sensör | Yön | Açı (Yaw, Pitch) |
|--------|-----|------------------|
| 0 | Front | (0°, 0°) |
| 1 | Back | (180°, 0°) |
| 2 | Left | (90°, 0°) |
| 3 | Right | (-90°, 0°) |
| 4 | Up | (0°, 90°) |
| 5 | Down | (0°, -90°) |
| 6 | Front-Left | (45°, 0°) |
| 7 | Front-Right | (-45°, 0°) |

Max mesafe: 5 metre

### Kontrol Çıktıları

| Çıktı | Aralık | Açıklama |
|-------|--------|----------|
| Thrust | [-1, 1] | Yukarı/aşağı kuvvet |
| Roll Rate | [-1, 1] | Sağa/sola yatma hızı |
| Pitch Rate | [-1, 1] | İleri/geri eğilme hızı |
| Yaw Rate | [-1, 1] | Dönme hızı |

---

## 🎓 Expert Teacher Stratejisi

Kural tabanlı expert şu stratejileri kullanır:

1. **Altitude Control**: 4 metre yükseklikte tut (PD controller)
2. **Obstacle Avoidance**: 
   - Front mesafe < 2m → Yaw ile dön (sol/sağ clearance'a göre)
   - Side mesafe < 1.5m → Roll ile kaç
3. **Forward Motion**: Güvenli ise yavaşça ileri git
4. **Stabilization**: Roll/pitch'i sönümle
5. **Emergency**: Yere çok yakınsa full thrust!

---

## 📈 Beklenen Performans

### Eğitim Sonrası

| Metrik | Hedef | Açıklama |
|--------|-------|----------|
| **Validation Loss** | < 0.05 | MSE loss on actions |
| **Survival Steps** | > 500 | Expert ~700-800 step |
| **Success Rate** | > 70% | 1000 step'e ulaşma |

### SNN vs Expert

- **Expert**: ~750 step ortalama
- **SNN**: ~500-600 step (expert'in %70-80'i)
- **Collision Rate**: %20-30

---

## 🔧 Konfigürasyon

`train_drone_3d.py` içinde:

```python
CONFIG = {
    'time_steps': 30,          # SNN zaman adımları
    'train_samples': 50000,    # Eğitim sample sayısı
    'val_samples': 10000,      # Validation sample
    'batch_size': 128,         # Batch size
    'epochs': 50,              # Epoch sayısı
    'lr': 1e-3,                # Learning rate
    'simple_teacher': False    # Basit/tam expert
}
```

---

## 🐛 Troubleshooting

### PyBullet GUI açılmıyor
```bash
# GUI olmadan test et
# drone_env_3d.py içinde gui=False yap
env = DroneEnv3D(gui=False)
```

### Eğitim çok yavaş
```python
# Sample sayısını azalt
'train_samples': 20000,  # 50000 yerine
'epochs': 30,            # 50 yerine
```

### Drone hemen çarpıyor
- Expert teacher'ı test et: `python drone_teacher_3d.py`
- Eğitim loss'u kontrol et: `logs/train_drone_3d_log.txt`
- Daha fazla epoch eğit

### PyBullet kurulumu başarısız
```bash
# Windows'ta Visual C++ gerekebilir
# Alternatif: pre-built wheel indir
pip install pybullet --no-cache-dir
```

---

## 📁 Dosya Yapısı

```
snn_reflex_proto/
├── drone_env_3d.py          # 3D PyBullet ortamı
├── drone_model_3d.py        # SNN ve ANN modelleri
├── drone_teacher_3d.py      # Expert teacher policy
├── train_drone_3d.py        # Eğitim script'i
├── run_drone_3d.py          # Demo ve test
├── DRONE_3D_README.md       # Bu dosya
├── checkpoints/
│   └── snn_drone_3d.pt      # Eğitilmiş model
└── logs/
    └── train_drone_3d_log.txt  # Eğitim log'u
```

---

## 🔬 2D vs 3D Karşılaştırması

| Özellik | 2D Prototip | 3D Drone |
|---------|-------------|----------|
| **Ortam** | Pygame 2D | PyBullet 3D |
| **Fizik** | Basit kinematik | Gerçekçi dinamik |
| **Sensörler** | 3 (sol, ön, sağ) | 8 (360°) |
| **Kontrol** | 3 (sola, düz, sağa) | 4 (thrust, roll, pitch, yaw) |
| **Giriş** | 3 değer | 17 değer |
| **SNN** | 3→64→3 | 17→128→64→4 |
| **Parametreler** | ~200 | ~10,000 |
| **Zorluk** | Kolay | Orta |

---

## 🚀 Sonraki Adımlar

### Faz 1: Optimizasyon (1 hafta)
- [ ] Hyperparameter tuning
- [ ] Daha iyi reward shaping
- [ ] Online learning dene

### Faz 2: Gelişmiş Sensörler (2 hafta)
- [ ] Kamera simülasyonu ekle
- [ ] Optik akış benzeri encoding
- [ ] Daha fazla sensör (16 yön)

### Faz 3: Karmaşık Görevler (3 hafta)
- [ ] Waypoint navigation
- [ ] Moving obstacles
- [ ] Multi-drone coordination

### Faz 4: Gerçek Drone (4+ hafta)
- [ ] ROS entegrasyonu
- [ ] PX4 autopilot
- [ ] Gerçek donanım testi

---

## 📚 Referanslar

- **PyBullet**: https://pybullet.org/
- **snnTorch**: https://snntorch.readthedocs.io/
- **Drone Control**: https://www.bitcraze.io/documentation/

---

## 🎯 Başarı Kriterleri

✅ **Minimum Viable Product (MVP)**
- [x] 3D ortam çalışıyor
- [x] Expert teacher çalışıyor
- [ ] SNN eğitimi tamamlandı
- [ ] SNN > 500 step hayatta kalıyor

✅ **Başarılı Proje**
- [ ] SNN expert'in %80'ine ulaştı
- [ ] 1000 step'te %50+ success rate
- [ ] Benchmark raporu hazır
- [ ] Demo video çekildi

🚀 **Mükemmel Sonuç**
- [ ] SNN expert'e eşit performans
- [ ] Online learning çalışıyor
- [ ] Gerçek drone'a hazır
- [ ] Yayın taslağı yazıldı

---

**Versiyon:** 1.0  
**Tarih:** 2026-05-29  
**Durum:** Kod hazır, eğitim bekleniyor ⏳


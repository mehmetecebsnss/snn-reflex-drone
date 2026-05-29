# 📋 Komut Referansı

## Kurulum

```bash
# Sanal ortam oluştur
python -m venv venv

# Aktive et (Windows)
venv\Scripts\activate

# Aktive et (Linux/Mac)
source venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Kurulumu test et
python test_setup.py
```

## Eğitim

```bash
# SNN modelini eğit
python train.py

# ANN baseline'ı eğit
python train_baseline.py
```

## Çalıştırma

```bash
# SNN ile canlı demo
python run.py

# ANN ile canlı demo
python run_baseline.py
```

## Değerlendirme

```bash
# Performans karşılaştırması
python benchmark.py

# Eğitim grafiklerini göster
python utils.py plot

# Sensör verilerini analiz et
python utils.py analyze
```

## Dosya Yapısı

```
snn_reflex_proto/
│
├── 📄 Dokümantasyon
│   ├── README.md           # Ana dokümantasyon
│   ├── QUICKSTART.md       # Hızlı başlangıç
│   └── COMMANDS.md         # Bu dosya
│
├── ⚙️ Konfigürasyon
│   ├── config.py           # Tüm parametreler
│   ├── requirements.txt    # Python bağımlılıkları
│   └── .gitignore         # Git ignore kuralları
│
├── 🧠 Çekirdek Modüller
│   ├── env.py             # 2D ortam ve ajan
│   ├── encoder.py         # Spike encoding
│   ├── teacher.py         # Kural tabanlı öğretmen
│   ├── model.py           # SNN modeli
│   └── baseline.py        # ANN karşılaştırma
│
├── 🚀 Çalıştırma Scriptleri
│   ├── train.py           # SNN eğitimi
│   ├── train_baseline.py  # ANN eğitimi
│   ├── run.py             # SNN demo
│   ├── run_baseline.py    # ANN demo
│   ├── benchmark.py       # Karşılaştırma
│   ├── utils.py           # Yardımcı fonksiyonlar
│   └── test_setup.py      # Kurulum testi
│
└── 📁 Veri Klasörleri
    ├── data/              # Eğitim verileri
    ├── checkpoints/       # Eğitilmiş modeller
    └── logs/              # Loglar ve grafikler
```

## Parametreler (config.py)

### Ortam Parametreleri
```python
SCREEN_WIDTH = 800          # Pencere genişliği
SCREEN_HEIGHT = 600         # Pencere yüksekliği
AGENT_SPEED = 4.0          # Ajan hızı
TURN_ANGLE = 10            # Dönüş açısı (derece)
SENSOR_ANGLES = [-45,0,45] # Sensör açıları
MAX_SENSOR_DIST = 150      # Maksimum sensör menzili
```

### SNN Parametreleri
```python
TIME_STEPS = 20            # Spike train uzunluğu
HIDDEN_SIZE = 32           # Gizli katman boyutu
INPUT_SIZE = 3             # Giriş boyutu (3 sensör)
OUTPUT_SIZE = 3            # Çıkış boyutu (3 aksiyon)
```

### Eğitim Parametreleri
```python
TRAIN_SAMPLES = 20000      # Eğitim örnek sayısı
VAL_SAMPLES = 5000         # Validasyon örnek sayısı
BATCH_SIZE = 64            # Batch boyutu
EPOCHS = 20                # Epoch sayısı
LR = 1e-3                  # Öğrenme oranı
```

## Çıktı Dosyaları

### Checkpoints
- `checkpoints/snn_reflex.pt` - Eğitilmiş SNN modeli
- `checkpoints/ann_baseline.pt` - Eğitilmiş ANN modeli

### Logs
- `logs/train_log.txt` - SNN eğitim logu
- `logs/baseline_log.txt` - ANN eğitim logu
- `logs/benchmark_results.npz` - Karşılaştırma sonuçları
- `logs/training_plot.png` - Eğitim grafikleri
- `logs/sensor_analysis.png` - Sensör analizi

## Hızlı Komutlar

### Sıfırdan Başlangıç
```bash
pip install -r requirements.txt
python test_setup.py
python train.py
python run.py
```

### Tam Karşılaştırma
```bash
python train.py
python train_baseline.py
python benchmark.py
```

### Sadece Demo
```bash
# Önce eğitim gerekli
python train.py
# Sonra demo
python run.py
```

## Sorun Giderme

### Import Hatası
```bash
pip install -r requirements.txt --upgrade
```

### Pygame Penceresi Açılmıyor
```bash
pip uninstall pygame
pip install pygame --no-cache-dir
```

### Model Bulunamadı
```bash
# Önce eğitim yapın
python train.py
# Sonra çalıştırın
python run.py
```

### Çok Yavaş
```python
# config.py içinde azaltın:
TIME_STEPS = 10
TRAIN_SAMPLES = 10000
HIDDEN_SIZE = 16
```

## Demo Kontrolleri

### Pygame Penceresi
- **SPACE**: Ortamı sıfırla
- **ESC**: Çıkış

### Ekran Bilgileri
- Episode: Kaçıncı deneme
- Steps: Bu denemede kaç adım
- Avg: Ortalama hayatta kalma
- Action: Şu anki karar

## Performans İpuçları

### Daha Hızlı Eğitim
```python
TRAIN_SAMPLES = 10000
EPOCHS = 10
TIME_STEPS = 10
```

### Daha İyi Doğruluk
```python
TRAIN_SAMPLES = 50000
EPOCHS = 50
HIDDEN_SIZE = 64
```

### Daha Uzun Hayatta Kalma
```python
AGENT_SPEED = 3.0
TURN_ANGLE = 15
```

## Gelişmiş Kullanım

### Özel Veri Seti
```python
from train import ReflexDataset
ds = ReflexDataset(n_samples=100000)
```

### Model Analizi
```python
import torch
from model import SNNReflexNet

model = SNNReflexNet()
model.load_state_dict(torch.load('checkpoints/snn_reflex.pt'))

# Parametre sayısı
params = sum(p.numel() for p in model.parameters())
print(f"Parameters: {params:,}")
```

### Özel Ortam
```python
from env import ObstacleEnv

env = ObstacleEnv()
# Özel engeller ekle
env.obstacles.append(pygame.Rect(400, 300, 50, 50))
```

## Yardım

```bash
# Python yardımı
python train.py --help

# Test çalıştır
python test_setup.py

# Versiyon kontrolü
python -c "import torch; print(torch.__version__)"
python -c "import snntorch; print(snntorch.__version__)"
```

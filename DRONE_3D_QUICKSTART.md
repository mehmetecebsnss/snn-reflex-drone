# 🚁 3D Drone SNN - Hızlı Başlangıç

## ✅ Sistem Hazır!

Tüm testler başarılı! 3D drone simülasyonu çalışıyor.

---

## 🎯 Ne Yaptık?

### 2D → 3D Geçiş Tamamlandı

| Özellik | 2D | 3D |
|---------|----|----|
| **Ortam** | Pygame | PyBullet (gerçek fizik) |
| **Sensörler** | 3 | 8 (360°) |
| **Kontrol** | 3 (sola/düz/sağa) | 4 (thrust/roll/pitch/yaw) |
| **Giriş** | 3 değer | 17 değer |
| **SNN** | 3→64→3 | 17→128→64→4 |
| **Parametreler** | 227 | 10,820 |

---

## 🚀 Şimdi Ne Yapacağız?

### Seçenek 1: Hemen Eğit (Önerilen)

```bash
python train_drone_3d.py
```

**Süre:** ~30-60 dakika  
**Sonuç:** Eğitilmiş SNN drone modeli

### Seçenek 2: Önce Expert'i İzle

```bash
# Expert teacher'ın drone'u nasıl kontrol ettiğini gör
python drone_teacher_3d.py
```

PyBullet GUI açılır, expert'in stratejisini görebilirsin.

---

## 📊 Eğitim Süreci

```
1. Expert Demonstrasyon Toplama
   ├─ 50,000 training sample
   └─ 10,000 validation sample
   Süre: ~10-15 dakika

2. SNN Eğitimi
   ├─ 50 epoch
   ├─ Batch size: 128
   └─ Learning rate: 0.001
   Süre: ~20-40 dakika

3. Model Kaydetme
   └─ checkpoints/snn_drone_3d.pt
```

---

## 🎮 Eğitim Sonrası

### Demo Çalıştır

```bash
python run_drone_3d.py
```

PyBullet GUI'de eğitilmiş SNN'in drone'u kontrol ettiğini göreceksin!

### Expert ile Karşılaştır

```bash
python run_drone_3d.py --compare
```

SNN vs Expert performans karşılaştırması.

---

## 📈 Beklenen Sonuçlar

### Eğitim Metrikleri
- **Validation Loss:** < 0.05 (MSE)
- **Eğitim Süresi:** 30-60 dakika

### Test Performansı
- **Expert:** ~700-800 step hayatta kalma
- **SNN:** ~500-600 step (expert'in %70-80'i)
- **Hedef:** > 500 step

---

## 🔧 Ayarlar (İsteğe Bağlı)

`train_drone_3d.py` içinde değiştirebilirsin:

```python
CONFIG = {
    'train_samples': 50000,  # Daha az → daha hızlı ama daha kötü
    'epochs': 50,            # Daha az → daha hızlı ama daha kötü
    'batch_size': 128,       # Daha küçük → daha yavaş ama daha iyi
}
```

**Hızlı test için:**
```python
'train_samples': 10000,
'epochs': 20,
```

---

## 📁 Dosyalar

```
snn_reflex_proto/
├── drone_env_3d.py          # 3D ortam (PyBullet)
├── drone_model_3d.py        # SNN modeli (17→128→64→4)
├── drone_teacher_3d.py      # Expert policy
├── train_drone_3d.py        # Eğitim script'i ← ŞİMDİ BU!
├── run_drone_3d.py          # Demo (eğitim sonrası)
└── test_drone_system.py     # Test (✓ tamamlandı)
```

---

## 🎯 Başarı Kriterleri

### ✅ Minimum (MVP)
- [ ] Eğitim tamamlandı
- [ ] Model kaydedildi
- [ ] SNN > 300 step

### 🎖️ İyi
- [ ] SNN > 500 step
- [ ] Expert'in %70'i

### 🏆 Mükemmel
- [ ] SNN > 700 step
- [ ] Expert'in %90'ı

---

## 🐛 Sorun mu Var?

### Eğitim çok yavaş
```python
# train_drone_3d.py içinde:
'train_samples': 20000,  # 50000 yerine
'epochs': 30,            # 50 yerine
```

### PyBullet GUI donuyor
```python
# drone_env_3d.py içinde:
env = DroneEnv3D(gui=False)  # GUI'yi kapat
```

### Out of memory
```python
# train_drone_3d.py içinde:
'batch_size': 64,  # 128 yerine
```

---

## 🚀 Hazır mısın?

```bash
# Eğitime başla!
python train_drone_3d.py
```

**Tahmini süre:** 30-60 dakika  
**Kahve molası ver, geri gel, drone'un uçtuğunu gör!** ☕🚁

---

**Not:** Eğitim sırasında log dosyasını takip edebilirsin:
```bash
# Başka bir terminal'de:
tail -f logs/train_drone_3d_log.txt
```

veya Windows'ta:
```bash
Get-Content logs/train_drone_3d_log.txt -Wait
```


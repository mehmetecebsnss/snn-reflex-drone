# 🚀 Hızlı Başlangıç Kılavuzu

## 5 Dakikada Çalıştırın

### 1. Kurulum (2 dakika)

```bash
cd snn_reflex_proto
pip install -r requirements.txt
```

### 2. SNN Modelini Eğitin (5-10 dakika)

```bash
python train.py
```

**Çıktı örneği:**
```
=== SNN Reflex Training ===

Generating 20000 samples...
Dataset created: 20000 samples
...
Epoch 20 | Loss: 0.3421 | Val Acc: 0.8567
  → Best model saved (acc: 0.8567)

Training complete! Best validation accuracy: 0.8567
```

### 3. Canlı Demo (Hemen!)

```bash
python run.py
```

Pencerede ajanın engeller arasında gezdiğini göreceksiniz!

### 4. Karşılaştırma (Opsiyonel)

ANN baseline'ı da eğitin:
```bash
python train_baseline.py
```

Sonra karşılaştırın:
```bash
python benchmark.py
```

## 🎯 Beklenen Sonuçlar

### İlk Hafta Sonu Hedefleri

✅ **Başarı Kriterleri:**
1. Pencere açılıyor ✓
2. Ajan engeller arasında yaşayabiliyor ✓
3. Model checkpoint kaydediliyor ✓

### Performans Metrikleri

| Metrik | Hedef | Tipik Sonuç |
|--------|-------|-------------|
| Eğitim Doğruluğu | >80% | ~85% |
| Hayatta Kalma | >100 adım | ~150 adım |
| Eğitim Süresi | <15 dk | ~8 dk |

## 🐛 Sorun Giderme

### Pygame yüklenmiyor
```bash
pip install pygame --upgrade
```

### snnTorch hatası
```bash
pip install snntorch --upgrade
```

### Model bulunamadı hatası
Önce `train.py` çalıştırın, sonra `run.py`

### Çok yavaş çalışıyor
`config.py` içinde:
- `TIME_STEPS = 10` (20 yerine)
- `TRAIN_SAMPLES = 10000` (20000 yerine)

## 📊 Sonuçları Görselleştirme

Eğitim grafiklerini görmek için:
```bash
python utils.py plot
```

Sensör verilerini analiz etmek için:
```bash
python utils.py analyze
```

## 🎮 Demo Kontrolleri

- **SPACE**: Ortamı sıfırla (yeni engeller)
- **ESC**: Çıkış

## 📈 Sonraki Adımlar

1. ✅ İlk prototip çalışıyor
2. 🔄 Parametreleri optimize edin
3. 🚁 Drone simülasyonuna geçin

## 💡 İpuçları

### Daha İyi Sonuçlar İçin

1. **Daha fazla veri:**
   ```python
   # config.py
   TRAIN_SAMPLES = 50000
   ```

2. **Daha uzun eğitim:**
   ```python
   # config.py
   EPOCHS = 50
   ```

3. **Daha büyük ağ:**
   ```python
   # config.py
   HIDDEN_SIZE = 64
   ```

### Hızlı Test İçin

```python
# config.py
TRAIN_SAMPLES = 5000
EPOCHS = 10
TIME_STEPS = 10
```

## 🎓 Öğrenme Kaynakları

- **snnTorch Tutorial:** https://snntorch.readthedocs.io/
- **SNN Basics:** https://www.frontiersin.org/articles/10.3389/fnins.2018.00774/full
- **Neuromorphic Computing:** https://en.wikipedia.org/wiki/Neuromorphic_engineering

## 📞 Yardım

Sorun mu yaşıyorsunuz?

1. README.md dosyasını okuyun
2. `config.py` ayarlarını kontrol edin
3. Hata mesajını kopyalayıp arayın
4. Issue açın

---

**Başarılar! 🚀**

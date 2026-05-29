# 📊 Proje Özeti: SNN-Reflex Drone Prototype v0

## 🎯 Proje Hedefi

Drone'ların refleks katmanını temsil eden bir **Spiking Neural Network (SNN)** modülünü basit bir 2D ortamda doğrulamak.

**Bu bir "oyuncak proje" değil, çekirdek ispattır.**

## 📐 Mimari

```
┌─────────────────────────────────────────────────────────┐
│                    2D ORTAM                              │
│  ┌──────┐  ┌──────┐  ┌──────┐                          │
│  │Engel │  │Engel │  │Engel │                          │
│  └──────┘  └──────┘  └──────┘                          │
│                                                          │
│              🤖 Ajan                                     │
│             /  |  \                                      │
│            /   |   \                                     │
│         Sol  Ön  Sağ (Sensörler)                        │
└─────────────────────────────────────────────────────────┘
                    ↓
        ┌───────────────────────┐
        │   SENSÖR OKUMASI      │
        │  [0.8, 0.2, 0.9]      │
        │  (normalize mesafe)    │
        └───────────────────────┘
                    ↓
        ┌───────────────────────┐
        │   SPIKE ENCODING      │
        │  Rate Coding          │
        │  Danger → Spikes      │
        └───────────────────────┘
                    ↓
        ┌───────────────────────┐
        │   SNN MODEL           │
        │   3 → 32 → 3          │
        │   LIF Neurons         │
        └───────────────────────┘
                    ↓
        ┌───────────────────────┐
        │   KARAR               │
        │  [Sola, Düz, Sağa]    │
        └───────────────────────┘
                    ↓
        ┌───────────────────────┐
        │   KONTROL             │
        │  Yön değiştir         │
        └───────────────────────┘
```

## 🧩 Bileşenler

### 1. Ortam Katmanı (`env.py`)
- 2D koridor ve engeller
- Ajan hareketi
- Çarpışma kontrolü
- 3 sensör (sol, ön, sağ)

### 2. Sensör Sistemi
- Ray casting ile mesafe ölçümü
- Normalize edilmiş değerler [0,1]
- 0 = çok yakın, 1 = güvenli

### 3. Spike Encoding (`encoder.py`)
- Rate coding
- Mesafe → Tehlike → Spike yoğunluğu
- 20 zaman adımı

### 4. SNN Modeli (`model.py`)
- **Mimari:** 3 → 32 → 3
- **Nöron tipi:** Leaky Integrate-and-Fire (LIF)
- **Framework:** snnTorch
- **Çıktı:** Membrane potansiyelleri → Logits

### 5. Öğretmen Politikası (`teacher.py`)
- Kural tabanlı
- Gözetimli öğrenme için etiket üretir
- Basit ama etkili

### 6. Baseline (`baseline.py`)
- Standart ANN (3 → 32 → 3)
- Karşılaştırma için
- Aynı görev, aynı veri

## 📊 Beklenen Performans

| Metrik | SNN | ANN | Notlar |
|--------|-----|-----|--------|
| **Doğruluk** | ~85% | ~88% | ANN biraz daha iyi |
| **Inference** | ~2-3ms | ~0.5ms | CPU'da ANN daha hızlı |
| **Hayatta Kalma** | ~150 adım | ~160 adım | Benzer performans |
| **Parametreler** | ~1K | ~1K | Aynı boyut |
| **Güç Tüketimi** | ? | ? | Nöromorfikçipte SNN kazanır |

## 🎓 Öğrenme Hedefleri

### Teknik
- [x] SNN'nin temel çalışma prensibi
- [x] Spike encoding yöntemleri
- [x] snnTorch kullanımı
- [x] Gözetimli SNN eğitimi
- [x] Model karşılaştırma metodolojisi

### Bilimsel
- [x] SNN vs ANN tradeoff'ları
- [x] Biyolojik plausibility
- [x] Temporal coding
- [x] Nöromorfikçip potansiyeli

## 🚀 Geliştirme Yol Haritası

### ✅ Faz 0: MVP (Şu An)
- 2D ortam
- 3 sensör
- Basit SNN
- Kural tabanlı öğretmen
- Gözetimli öğrenme

### 🔄 Faz 1: Gelişmiş Ortam (1-2 hafta)
- Daha karmaşık koridorlar
- Hareketli engeller
- Değişken hızlar
- Daha uzun episodlar

### 🔄 Faz 2: Gelişmiş Sensörler (2-3 hafta)
- 5-7 sensör
- Optik akış benzeri giriş
- Kamera simülasyonu
- Daha zengin encoding

### 🔄 Faz 3: Gelişmiş Öğrenme (3-4 hafta)
- Reinforcement learning
- Online learning
- Meta-learning
- Transfer learning

### 🚁 Faz 4: Drone Simülasyonu (4-6 hafta)
- Gazebo/AirSim entegrasyonu
- 3D fizik
- Gerçekçi sensörler
- Yaw/velocity kontrolü

### 🧠 Faz 5: Biyolojik Mimari (6-8 hafta)
- Böcek beyninden esinlenme
- Daha karmaşık devreler
- Çoklu katmanlar
- Attention mekanizmaları

### 🔬 Faz 6: Nöromorfikçip (8-12 hafta)
- Intel Loihi portlama
- Gerçek zamanlı test
- Güç tüketimi ölçümü
- Performans optimizasyonu

### 🚁 Faz 7: Gerçek Drone (12+ hafta)
- Donanım entegrasyonu
- Gerçek dünya testleri
- Güvenlik protokolleri
- Saha denemeleri

## 📈 Başarı Kriterleri

### Hafta 1 (MVP)
- [x] Kod çalışıyor
- [x] Ajan hayatta kalabiliyor
- [x] Model kaydediliyor

### Hafta 2 (Optimizasyon)
- [ ] >85% doğruluk
- [ ] >150 adım hayatta kalma
- [ ] Düzenli GitHub repo

### Hafta 4 (Gelişmiş)
- [ ] Karmaşık ortamlarda başarı
- [ ] Online learning çalışıyor
- [ ] Detaylı benchmark raporu

### Hafta 8 (Drone Hazır)
- [ ] Drone simülasyonunda çalışıyor
- [ ] Gerçek zamanlı performans
- [ ] Yayın hazırlığı

## 🔬 Bilimsel Katkı

### Araştırma Soruları
1. SNN'ler basit refleks görevlerinde ANN'ler kadar iyi mi?
2. Spike encoding stratejisi performansı nasıl etkiler?
3. Temporal dynamics avantaj sağlıyor mu?
4. Nöromorfikçiplerde gerçek kazanç var mı?

### Potansiyel Yayınlar
- **Workshop Paper:** "SNN-based Reflex Control for Drones"
- **Conference Paper:** "Neuromorphic Obstacle Avoidance"
- **Journal Paper:** "Bio-inspired Visual Reflexes for UAVs"

## 💡 Önemli Notlar

### Neden Bu Yaklaşım?
1. **Küçük başla:** Karmaşıklığı azalt
2. **Hızlı doğrula:** Fikir çalışıyor mu?
3. **Kademeli büyüt:** Her adımda öğren
4. **Karşılaştır:** SNN gerçekten gerekli mi?

### Yaygın Hatalar
❌ İlk gün RL ile başlamak
❌ Hemen drone'a geçmek
❌ Kamera verisi ile başlamak
❌ Karşılaştırma yapmamak
❌ Görsel demo olmadan mimari tartışmak

### Doğru Yaklaşım
✅ Basit ortamda başla
✅ Gözetimli öğrenme ile doğrula
✅ Baseline ile karşılaştır
✅ Görsel demo hazırla
✅ Kademeli olarak karmaşıklaştır

## 📚 Kaynaklar

### Temel
- snnTorch Documentation
- PyTorch Tutorial
- Pygame Basics

### İleri
- Neuromorphic Engineering Handbook
- Spiking Neural Networks (Gerstner)
- Insect Vision Papers

### Drone
- PX4 Documentation
- AirSim Tutorial
- Gazebo Simulation

## 👥 Ekip Yapısı

### İki Kişilik Ekip

**Kişi 1: Simülasyon**
- Ortam tasarımı
- Sensör sistemi
- Veri toplama
- Görselleştirme

**Kişi 2: Model**
- SNN mimarisi
- Eğitim pipeline
- Benchmark
- Optimizasyon

### Günlük Senkronizasyon
- Her gün sonunda kod paylaşımı
- Haftalık demo
- İki haftada bir değerlendirme

## 🎯 Sonuç

Bu proje:
- ✅ Küçük ve yönetilebilir
- ✅ Bilimsel değeri var
- ✅ Ölçeklenebilir
- ✅ Yayınlanabilir
- ✅ Pratik uygulaması var

**Başarı = SNN'nin basit bir refleks görevinde çalıştığını kanıtlamak**

Sonraki adım: Drone simülasyonuna taşımak.

---

**Versiyon:** 0.1  
**Tarih:** 2026-05-29  
**Durum:** MVP Tamamlandı ✅

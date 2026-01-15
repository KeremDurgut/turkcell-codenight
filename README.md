# Turkcell Decision Engine

Çok Servisli Davranış ve Karar Platformu - Code Night 2026

## Özellikler

- **Dashboard**: Kullanıcı bazlı karşılaştırmalı metrikler (İnternet, Harcama, İçerik)
- **Event Yönetimi**: Event ekleme ve kümülatif kullanım takibi
- **Kural Motoru**: Dinamik kural değerlendirme ve aksiyon tetikleme
- **Karar Geçmişi**: Audit log - tüm kararların kaydı
- **Bildirimler**: BiP üzerinden gönderilen aksiyonlar
- **Kural Wizard**: Adım adım kural oluşturma sihirbazı

## Teknolojiler

- Python 3.10+
- PyQt6 (Desktop UI)
- PostgreSQL (Veritabanı)
- pyqtgraph (Grafikler)

## Kurulum

### 1. Bağımlılıkları Yükle

```bash
pip install -r requirements.txt
```

### 2. PostgreSQL Veritabanı

```bash
# Veritabanı oluştur
createdb codenight

# Schema'yı uygula
psql -d codenight -f database/schema.sql

# Örnek verileri yükle
psql -d codenight -f database/seed_data.sql
```

### 3. Ortam Değişkenleri

`.env.example` dosyasını `.env` olarak kopyala ve değerleri düzenle:

```bash
cp .env.example .env
```

### 4. Uygulamayı Çalıştır

```bash
python main.py
```

## Proje Yapısı

```
codenight/
├── main.py                 # Uygulama giriş noktası
├── requirements.txt        # Python bağımlılıkları
├── .env.example           # Örnek ortam değişkenleri
├── database/
│   ├── schema.sql         # PostgreSQL şeması
│   └── seed_data.sql      # Örnek veriler
└── src/
    ├── config.py          # Yapılandırma
    ├── database.py        # Veritabanı bağlantısı ve repository'ler
    ├── rule_engine.py     # Kural değerlendirme motoru
    └── ui/
        ├── styles.py      # Turkcell renk paleti ve stiller
        ├── widgets.py     # Yeniden kullanılabilir widget'lar
        ├── dashboard.py   # Dashboard paneli
        ├── events_panel.py    # Event yönetimi
        ├── rules_panel.py     # Kural yönetimi
        ├── decisions_panel.py # Karar geçmişi
        ├── notifications_panel.py # Bildirimler
        └── rule_wizard.py     # Kural oluşturma sihirbazı
```

## Kural Sözdizimi

Kurallar şu formatta tanımlanır:

```
internet_today_gb > 15
spend_today_try >= 100
content_minutes_today BETWEEN 60 AND 120
internet_today_gb > 10 AND spend_today_try > 50
```

## Aksiyon Tipleri

- `DATA_USAGE_WARNING` - Veri kullanım uyarısı
- `SPEND_ALERT` - Harcama uyarısı
- `CONTENT_COOLDOWN_SUGGESTION` - İçerik mola önerisi
- `CRITICAL_ALERT` - Kritik uyarı
- `DATA_USAGE_NUDGE` - Veri kullanım hatırlatması
- `SPEND_NUDGE` - Harcama hatırlatması

## Lisans

MIT License - Code Night 2026

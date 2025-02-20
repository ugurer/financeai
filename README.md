#Finance AI - Türk Borsası Analiz ve Portföy Yönetimi

Modern ve kullanıcı dostu bir borsa analiz ve portföy yönetim uygulaması.

## Özellikler

- 📈 Gerçek zamanlı borsa verileri
- 💼 Portföy yönetimi
- 🔍 Gelişmiş hisse senedi arama
- 📊 Piyasa özeti ve analizler
- 🤖 Yapay zeka destekli yatırım önerileri
- 📱 Responsive tasarım

## Başlangıç

### Gereksinimler

- Node.js (v18+)
- Python (3.9+)
- Docker ve Docker Compose
- PostgreSQL

### Kurulum

1. Repoyu klonlayın:
```bash
git clone https://github.com/ugurer/financeAi.git
cd financeAi
```

2. Gerekli ortam değişkenlerini ayarlayın:
```bash
cp .env.example .env
# .env dosyasını düzenleyin
```

3. Docker container'larını başlatın:
```bash
docker-compose up --build
```

4. Frontend bağımlılıklarını yükleyin:
```bash
cd frontend
npm install
```

5. Frontend'i başlatın:
```bash
npm run dev
```

Uygulama şu adreslerde çalışacak:
- Frontend: http://localhost:5173
- Python API: http://localhost:8000
- Node API: http://localhost:3001

## Proje Yapısı

```
financeAi/
├── frontend/                # React + TypeScript frontend
│   ├── src/
│   │   ├── components/     # UI bileşenleri
│   │   ├── pages/         # Sayfa bileşenleri
│   │   ├── services/      # API servisleri
│   │   └── utils/         # Yardımcı fonksiyonlar
│   └── ...
├── backend/
│   ├── python-api/        # FastAPI backend
│   │   ├── main.py       # Ana uygulama
│   │   └── ...
│   └── node-api/         # Node.js auth servisi
│       ├── src/
│       └── ...
└── ...
```

## Teknoloji Yığını

### Frontend
- React
- TypeScript
- Vite
- Chakra UI
- Axios
- React Query

### Backend
- FastAPI (Python)
- Express.js (Node.js)
- PostgreSQL
- JWT Authentication

## TODO List

### Frontend
- [ ] Portföy sayfası tasarımı
- [ ] Hisse detay sayfası
- [ ] Grafiklerde zoom ve pan özellikleri
- [ ] Tema desteği (açık/koyu)
- [ ] Mobil uyumluluk iyileştirmeleri
- [ ] Offline mod desteği
- [ ] Unit testler
- [ ] E2E testler
- [ ] PWA desteği

### Backend
- [ ] Gerçek borsa API entegrasyonu
- [ ] WebSocket desteği
- [ ] Veritabanı şeması ve migrasyonlar
- [ ] Kullanıcı yetkilendirme sistemi
- [ ] Rate limiting
- [ ] Caching sistemi
- [ ] API dokümantasyonu
- [ ] Unit testler
- [ ] CI/CD pipeline

### Genel
- [ ] Error tracking (Sentry)
- [ ] Analytics entegrasyonu
- [ ] Docker optimizasyonları
- [ ] Performans iyileştirmeleri
- [ ] Security audit
- [ ] Load testing

## Katkıda Bulunma

1. Fork'layın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'feat: add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır - detaylar için [LICENSE](LICENSE) dosyasına bakın.

## İletişim

Proje Sahibi - [slymnugurer](https://twitter.com/slymnugurer)

Proje Linki: [https://github.com/ugurer/financeAi](https://github.com/ugurer/financeAi)
# Backend - Manevi Rehber

## 📋 Genel Bakış

Bu backend, **Manevi Rehber** React Native mobil uygulaması için API servisleri sağlar.

## 🛠️ Teknoloji Stack

| Katman | Teknoloji |
|--------|-----------|
| **Framework** | Django 5.x + Django REST Framework |
| **Dil** | Python 3.11+ |
| **Veritabanı** | PostgreSQL 15+ |
| **ORM** | Django ORM |
| **Auth** | JWT (djangorestframework-simplejwt) |
| **Cache** | Redis (opsiyonel, rate limiting için) |
| **Task Queue** | Celery (opsiyonel, bildirimler için) |

## 📁 Klasör Yapısı

```
backend/
├── manage.py
├── requirements.txt
├── .env
├── .env.example
├── AGENTS.md
├── core/                    # Django projesi
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── apps/
│   ├── users/             # Kullanıcı yönetimi
│   │   ├── models.py      # Custom User model
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── prayer_times/      # Namaz vakitleri
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── content/           # Ayet, hadis, dua içerikleri
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── premium/           # Premium üyelik
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   └── chat/              # AI chat (Gemini)
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       └── urls.py
└── media/                 # Kullanıcı upload'ları
```

## 🔌 API Endpoints

### Auth
```
POST   /api/auth/register/          # Kayıt
POST   /api/auth/login/             # Giriş
POST   /api/auth/logout/            # Çıkış
POST   /api/auth/refresh/           # Token yenileme
POST   /api/auth/password/reset/    # Şifre sıfırlama
```

### Namaz Vakitleri
```
GET    /api/prayer-times/           # Bugünkü vakitler
GET    /api/prayer-times/next/      # Sonraki vakit
GET    /api/prayer-times/monthly/   # Aylık vakitler
POST   /api/prayer-times/location/  # Konum kaydet
```

### İçerik (Ayet, Hadis, Dua)
```
GET    /api/content/daily-verse/    # Günlük ayet
GET    /api/content/daily-hadith/   # Günlük hadis
GET    /api/content/duas/           # Dua listesi
GET    /api/content/duas/{id}/      # Detay
GET    /api/content/search/         # İçerik arama
```

### AI Chat (Gemini)
```
POST   /api/chat/                   # AI'ya soru sor
GET    /api/chat/history/           # Sohbet geçmişi
DELETE /api/chat/history/           # Geçmişi sil
```

### Premium
```
GET    /api/premium/status/         # Premium durumu
POST   /api/premium/subscribe/      # Abone ol
POST   /api/premium/cancel/         # Abonelik iptal
```

### Kullanıcı
```
GET    /api/user/profile/           # Profil bilgileri
PUT    /api/user/profile/           # Profil güncelle
PUT    /api/user/settings/          # Ayarlar
```

## 🔑 Çevresel Değişkenler

`.env` dosyası:

```env
# Django
DEBUG=True
SECRET_KEY=django-insecure-your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Veritabanı
POSTGRES_NAME=manevi_rehber
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DATABASE_URL=postgresql://postgres:password@localhost:5432/manevi_rehber

# JWT
JWT_ACCESS_TOKEN_LIFETIME=60  # dakika
JWT_REFRESH_TOKEN_LIFETIME=1440  # dakika (24 saat)

# Gemini AI
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-1.5-flash

# Redis (opsiyonel)
REDIS_URL=redis://localhost:6379/0

# CORS (React Native için)
CORS_ALLOWED_ORIGINS=http://localhost:3000

# Bildirim (opsiyonel, Firebase)
FIREBASE_CREDENTIALS=path/to/serviceAccountKey.json
```

## 🚀 Kurulum

### 1. Gereksinimler
- Python 3.11+
- PostgreSQL 15+
- pip veya poetry

### 2. Veritabanı Kurulumu
```bash
# PostgreSQL'e bağlan
psql -U postgres

# Veritabanı oluştur
CREATE DATABASE manevi_rehber;
CREATE USER manevi_user WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE manevi_rehber TO manevi_user;
\q
```

### 3. Proje Kurulumu
```bash
# Virtual environment oluştur
python -m venv venv

# Aktif et (Windows)
venv\Scripts\activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# .env dosyasını oluştur
copy .env.example .env

# Migration'ları çalıştır
python manage.py migrate

# Superuser oluştur (admin panel için)
python manage.py createsuperuser

# Development serverı başlat
python manage.py runserver
```

## 📦 Temel Bağımlılıklar (`requirements.txt`)

```txt
# Core
Django==5.0.6
djangorestframework==3.15.1
djangorestframework-simplejwt==5.3.1

# Database
psycopg2-binary==2.9.9

# CORS
django-cors-headers==4.3.1

# Environment
python-decouple==3.8

# AI
google-generativeai==0.5.4

# Validation
django-filter==24.2

# Image processing (profil foto vb.)
Pillow==10.3.0

# Development
black==24.4.2
flake8==7.0.0
pytest==8.2.0
pytest-django==4.8.0
```

## 🧪 Test

```bash
# Tüm testleri çalıştır
python manage.py test

# Belirli bir app testi
python manage.py test apps.chat

# Coverage ile
pytest --cov=apps
```

## 📝 Kodlama Standartları

### Model Örneği
```python
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """Custom User Model"""
    phone = models.CharField(max_length=15, unique=True)
    is_premium = models.BooleanField(default=False)
    premium_expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'users'
```

### Serializer Örneği
```python
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'is_premium']
        read_only_fields = ['id', 'is_premium']
```

### View Örneği
```python
from rest_framework import viewsets, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import User
from .serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
```

## 🔒 Güvenlik

- ✅ JWT authentication zorunlu (public endpoint'ler hariç)
- ✅ CORS sadece whitelist domain'ler için
- ✅ Rate limiting (django-ratelimit veya Redis)
- ✅ Input validation (DRF serializers)
- ✅ HTTPS production'da zorunlu
- ✅ Secret key environment variable'dan gelmeli
- ✅ Debug=False production'da

## 📊 Admin Panel

Django'nun hazır admin paneli `/admin/` endpoint'inde:

- Kullanıcı yönetimi
- İçerik (ayet, hadis, dua) CRUD
- Premium üyelik takibi
- Chat geçmişi görüntüleme

## 🔗 React Native Entegrasyonu

### Frontend'de API Client Örneği
```typescript
// src/services/api.ts
const API_BASE_URL = 'http://192.168.1.100:8000/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token interceptor
api.interceptors.request.use((config) => {
  const token = await SecureStore.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### Önemli Notlar
1. **Local Development**: React Native emulator'dan Django'ya erişim için `ALLOWED_HOSTS` ayarı gerekli
2. **Android Emulator**: `http://10.0.2.2:8000` (localhost'u temsil eder)
3. **iOS Simulator**: `http://localhost:8000`
4. **Gerçek Cihaz**: Aynı network'te olmalı, `0.0.0.0:8000` ile başlat

## 🐛 Health Check

```
GET /health/  # Veritabanı bağlantısı ve servis durumu
```

Response:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-04-26T10:30:00Z"
}
```

## 📌 Sonraki Adımlar

1. [ ] Django projesini oluştur (`django-admin startproject core .`)
2. [ ] Apps'leri oluştur (`python manage.py startapp users` vb.)
3. [ ] PostgreSQL bağlantısını yapılandır
4. [ ] JWT authentication kurulumu
5. [ ] Model ve serializer'ları yaz
6. [ ] API endpoint'leri implement et
7. [ ] Admin panel'i özelleştir
8. [ ] Test yaz
9. [ ] React Native ile entegre et

## 📚 Kaynaklar

- [Django Docs](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Django JWT Auth](https://django-rest-framework-simplejwt.readthedocs.io/)
- [PostgreSQL + Django](https://docs.djangoproject.com/en/stable/ref/databases/#postgresql-notes)

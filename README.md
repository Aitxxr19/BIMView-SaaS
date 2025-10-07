# BIMView SaaS - Conversión de Nubes de Puntos 3D

[![CI/CD](https://github.com/Aitxxr19/BIMView-SaaS/workflows/API%20Tests%20and%20Deploy/badge.svg)](https://github.com/Aitxxr19/BIMView-SaaS/actions)
[![Deploy Status](https://img.shields.io/badge/deploy-railway-blue)](https://tu-api.railway.app)
[![Frontend](https://img.shields.io/badge/frontend-vercel-black)](https://tu-app.vercel.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Características

- Conversión de nubes de puntos (.ply, .las, .laz) a mallas 3D
- Procesamiento asíncrono con Celery
- Suscripciones con Stripe
- Dashboard en tiempo real
- API REST con FastAPI
- Despliegue automático con GitHub Actions

## 🛠️ Stack Tecnológico

- **Backend**: FastAPI, PostgreSQL, Redis, Celery, Open3D
- **Frontend**: Next.js 14, TailwindCSS, TypeScript
- **Infraestructura**: Docker, Railway, Vercel
- **Pagos**: Stripe
- **CI/CD**: GitHub Actions

## 📖 Documentación

- [API Docs](https://tu-api.railway.app/docs)
- [Guía de Despliegue](docs/deployment.md)
- [Contribuir](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

## 🚀 Despliegue Rápido

```bash
# Clonar repositorio
git clone https://github.com/Aitxxr19/BIMView-SaaS.git
cd BIMView-SaaS

# Backend
cd api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## 🏗️ Estructura del Proyecto

```
BIMView-SaaS/
├── .github/           # GitHub Actions y templates
├── api/              # Backend FastAPI
├── frontend/         # Frontend Next.js
├── infra/            # Docker y configuración
├── docs/             # Documentación
└── tests/            # Tests E2E
```

## 🤝 Contribuir

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para detalles sobre cómo contribuir.

## 📄 Licencia

MIT License - ver [LICENSE](LICENSE) para detalles.

## 📞 Soporte

- Crear un [issue](https://github.com/Aitxxr19/BIMView-SaaS/issues)
- Email: soporte@bimview.com

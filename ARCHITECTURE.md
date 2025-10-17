# Arquitectura del Sistema - BIMView SaaS

## Diagrama de Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (PostgreSQL)  │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       │
         │              ┌─────────────────┐              │
         │              │     Redis       │              │
         │              │   (Celery)      │              │
         │              │   Port: 6379    │              │
         │              └─────────────────┘              │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Storage       │    │   Workers       │    │   Monitoring    │
│   (S3/MinIO)    │    │   (Celery)      │    │   (GitHub)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Componentes Principales

### Frontend (Next.js 14)
- **Framework**: Next.js 14 con App Router
- **Styling**: TailwindCSS
- **Language**: TypeScript
- **Features**: SSR, SSG, API Routes
- **Deployment**: Vercel

### Backend (FastAPI)
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Features**: Async, Auto-docs, Validation
- **Deployment**: Railway

### Base de Datos (PostgreSQL)
- **Type**: Relational Database
- **ORM**: SQLAlchemy
- **Features**: ACID, JSON support
- **Deployment**: Railway PostgreSQL

### Cache (Redis)
- **Type**: In-memory database
- **Usage**: Celery broker, session cache
- **Deployment**: Railway Redis

### Storage (S3/MinIO)
- **Type**: Object storage
- **Usage**: File uploads, processed files
- **Deployment**: AWS S3 / MinIO

### Workers (Celery)
- **Type**: Task queue
- **Usage**: 3D processing, background tasks
- **Deployment**: Railway workers

## Flujo de Datos

### 1. Autenticación
```
User → Frontend → API → Database → JWT Token
```

### 2. Subida de Archivos
```
User → Frontend → API → Storage → Database (Job)
```

### 3. Procesamiento 3D
```
API → Celery → Worker → Open3D → Storage → Database (Update)
```

### 4. Descarga de Resultados
```
User → Frontend → API → Storage → User
```

## Seguridad

- **Autenticación**: JWT tokens
- **Autorización**: Role-based access
- **Validación**: Pydantic schemas
- **CORS**: Configurado para frontend
- **HTTPS**: En producción

## Escalabilidad

- **Horizontal**: Múltiples workers
- **Vertical**: Auto-scaling en Railway
- **Caching**: Redis para sesiones
- **CDN**: Vercel Edge Network

## Monitoreo

- **Logs**: GitHub Actions
- **Metrics**: Railway dashboard
- **Errors**: Sentry (futuro)
- **Uptime**: GitHub Actions health checks

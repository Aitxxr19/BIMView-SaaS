# Guía de Despliegue - BIMView SaaS

## Despliegue en Producción

### Backend (Railway)

1. **Crear cuenta en Railway**
   - Ir a https://railway.app
   - Conectar con GitHub

2. **Configurar variables de entorno**
   ```env
   DATABASE_URL=postgresql://...
   SECRET_KEY=your-production-secret-key
   REDIS_URL=redis://...
   ```

3. **Desplegar**
   - Conectar repositorio
   - Configurar build: `cd saas3d/api && pip install -r requirements.txt`
   - Configurar start: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel)

1. **Crear cuenta en Vercel**
   - Ir a https://vercel.com
   - Conectar con GitHub

2. **Configurar variables de entorno**
   ```env
   NEXT_PUBLIC_API_URL=https://tu-api.railway.app
   ```

3. **Desplegar**
   - Conectar repositorio
   - Configurar root directory: `saas3d/frontend`
   - Deploy automático

### Base de Datos (PostgreSQL)

1. **Railway PostgreSQL**
   - Crear servicio PostgreSQL
   - Obtener DATABASE_URL
   - Configurar en backend

### Redis (Railway)

1. **Railway Redis**
   - Crear servicio Redis
   - Obtener REDIS_URL
   - Configurar en backend

## URLs de Producción

- **API**: https://tu-api.railway.app
- **Frontend**: https://tu-app.vercel.app
- **API Docs**: https://tu-api.railway.app/docs

## Monitoreo

- **Railway**: Dashboard de métricas
- **Vercel**: Analytics y logs
- **GitHub Actions**: CI/CD status

## Backup

- **Base de datos**: Backup automático en Railway
- **Archivos**: S3/MinIO para almacenamiento
- **Código**: GitHub como backup principal

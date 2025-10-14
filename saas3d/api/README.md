# BIMView API

Backend FastAPI para la plataforma SaaS de conversión de nubes de puntos 3D.

## Características

- ✅ Autenticación JWT
- ✅ Gestión de usuarios
- ✅ Subida de archivos
- ✅ Gestión de trabajos
- ✅ Base de datos PostgreSQL
- ✅ Tests unitarios

## Instalación

```bash
cd saas3d/api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Configuración

Crear archivo `.env`:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/saas3d
SECRET_KEY=your-secret-key-change-in-production
```

## Ejecutar

```bash
# Desarrollo
uvicorn main:app --reload

# Producción
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Tests

```bash
pytest tests/ -v --cov=. --cov-report=html
```

## Estructura

```
saas3d/api/
├── main.py              # Aplicación principal
├── database.py          # Configuración de base de datos
├── models.py            # Modelos SQLAlchemy
├── schemas.py           # Esquemas Pydantic
├── auth.py              # Utilidades de autenticación
├── enums.py             # Enumeraciones
├── routes/              # Endpoints
│   ├── auth.py         # Autenticación
│   ├── jobs.py         # Trabajos
│   └── upload.py       # Subida de archivos
├── tests/              # Tests unitarios
└── uploads/            # Archivos subidos

```

## Endpoints

### Autenticación
- `POST /auth/register` - Registrar usuario
- `POST /auth/login` - Iniciar sesión
- `GET /auth/me` - Obtener usuario actual

### Jobs
- `GET /api/jobs` - Listar trabajos
- `POST /api/jobs` - Crear trabajo
- `GET /api/jobs/{id}` - Obtener trabajo
- `DELETE /api/jobs/{id}` - Eliminar trabajo

### Upload
- `POST /api/upload` - Subir archivo
- `GET /api/files/{filename}` - Descargar archivo
- `DELETE /api/files/{filename}` - Eliminar archivo

## Documentación API

Acceder a:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

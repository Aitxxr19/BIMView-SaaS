# BIMView SaaS - Configuración de Desarrollo

## Requisitos Previos

- Python 3.11+
- Node.js 18+
- Docker y Docker Compose
- Git

## Configuración Inicial

### 1. Clonar el repositorio
```bash
git clone https://github.com/Aitxxr19/BIMView-SaaS.git
cd BIMView-SaaS
```

### 2. Configurar variables de entorno
```bash
cp env.example .env
# Editar .env con tus configuraciones
```

### 3. Levantar servicios de desarrollo
```bash
# Windows
start-dev.bat

# Linux/Mac
./start-dev.sh
```

### 4. Configurar Backend
```bash
cd saas3d/api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### 5. Configurar Frontend
```bash
cd saas3d/frontend
npm install
npm run dev
```

## URLs de Desarrollo

- **API**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## Comandos Útiles

```bash
# Tests del backend
cd saas3d/api
pytest tests/ -v --cov=.

# Tests del frontend
cd saas3d/frontend
npm test

# Build completo
cd saas3d/frontend
npm run build

# Linting
cd saas3d/frontend
npm run lint
```

## Estructura del Proyecto

```
BIMView-SaaS/
├── .github/           # GitHub Actions y templates
├── saas3d/
│   ├── api/          # Backend FastAPI
│   ├── frontend/     # Frontend Next.js
│   ├── docs/         # Documentación
│   ├── infra/        # Infraestructura
│   └── tests/        # Tests E2E
├── docker-compose.yml
├── start-dev.bat
├── start-dev.sh
└── env.example
```

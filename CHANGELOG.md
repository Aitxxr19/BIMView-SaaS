# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Procesamiento 3D con Open3D
- Integración con Celery para workers
- Almacenamiento S3/MinIO
- Integración con Stripe para pagos
- Tests E2E con Playwright

## [0.8.0] - 2025-10-14

### Added
- Sistema completo de subida de archivos
- Componente FileUpload con drag & drop
- Validación de tipos de archivo (.ply, .las, .laz, .pcd, .xyz)
- Límite de tamaño de archivo (100MB)
- Endpoint /upload con autenticación
- Tests completos para upload
- Documentación de API y frontend

### Changed
- Mejorado el dashboard con botón de subida
- Actualizado cliente API con métodos de upload
- Mejorada la experiencia de usuario

## [0.7.0] - 2025-10-14

### Added
- Conexión completa frontend-backend
- Cliente API centralizado
- Hook useAuth para gestión de autenticación
- Hook useJobs para gestión de trabajos
- AuthProvider para contexto global
- Componente ProtectedRoute
- Persistencia de sesión con localStorage

### Changed
- Refactorizado dashboard con hooks
- Actualizadas páginas login/register
- Mejorado manejo de errores

## [0.6.0] - 2025-10-14

### Added
- Frontend Next.js 14 con TypeScript
- Páginas: home, login, register, dashboard
- TailwindCSS con tema personalizado
- Componentes reutilizables
- Navegación y estados de carga
- ESLint y configuración TypeScript

## [0.5.0] - 2025-10-14

### Added
- Conexión a PostgreSQL con Docker
- Modelo Job con estados y progreso
- Relaciones entre User y Job
- Endpoints CRUD para Jobs
- Scripts de desarrollo para Windows/Linux
- Variables de entorno configuradas

## [0.4.0] - 2025-10-14

### Added
- Autenticación completa con JWT
- Modelo User con SQLAlchemy
- Endpoints: /register, /login, /me
- Hash de contraseñas con bcrypt
- Middleware de autenticación
- Tests completos para autenticación

## [0.3.0] - 2025-10-14

### Added
- Tests unitarios con pytest
- GitHub Actions para CI/CD
- CodeQL para análisis de seguridad
- Cobertura de código con Codecov
- Configuración de pytest

## [0.2.0] - 2025-10-14

### Added
- API FastAPI básica
- Templates de GitHub Issues/PRs
- Dependabot para actualizaciones
- CONTRIBUTING.md
- Estructura de dependencias

## [0.1.0] - 2025-10-14

### Added
- Repositorio GitHub configurado
- Estructura de carpetas profesional
- README.md con badges
- .gitignore completo
- Configuración inicial del proyecto

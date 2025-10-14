# BIMView Frontend

Frontend Next.js 14 para la plataforma SaaS de conversión de nubes de puntos 3D.

## Características

- ✅ Next.js 14 con App Router
- ✅ TypeScript
- ✅ TailwindCSS
- ✅ Autenticación con JWT
- ✅ Subida de archivos drag & drop
- ✅ Dashboard en tiempo real
- ✅ Rutas protegidas

## Instalación

```bash
cd saas3d/frontend
npm install
```

## Configuración

Crear archivo `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Ejecutar

```bash
# Desarrollo
npm run dev

# Build
npm run build

# Producción
npm start
```

## Estructura

```
saas3d/frontend/
├── src/
│   ├── app/                # Páginas (App Router)
│   │   ├── page.tsx       # Home
│   │   ├── login/         # Login
│   │   ├── register/      # Registro
│   │   ├── dashboard/     # Dashboard
│   │   └── upload/        # Subida de archivos
│   ├── components/         # Componentes reutilizables
│   │   ├── FileUpload.tsx
│   │   └── ProtectedRoute.tsx
│   ├── lib/               # Utilidades
│   │   ├── api.ts         # Cliente API
│   │   ├── auth.tsx       # Context de autenticación
│   │   ├── useJobs.ts     # Hook para jobs
│   │   └── useFileUpload.ts
│   └── types/             # Tipos TypeScript
├── public/                # Archivos estáticos
└── tailwind.config.js     # Configuración Tailwind
```

## Páginas

- `/` - Página principal
- `/login` - Iniciar sesión
- `/register` - Crear cuenta
- `/dashboard` - Dashboard de usuario (protegida)
- `/upload` - Subir archivos (protegida)

## Componentes Principales

### FileUpload
Componente de subida de archivos con drag & drop.

### ProtectedRoute
HOC para proteger rutas que requieren autenticación.

### useAuth
Hook para gestionar el estado de autenticación.

### useJobs
Hook para gestionar trabajos del usuario.

## Tecnologías

- **Next.js 14**: Framework React
- **TypeScript**: Tipado estático
- **TailwindCSS**: Estilos
- **React Dropzone**: Drag & drop de archivos

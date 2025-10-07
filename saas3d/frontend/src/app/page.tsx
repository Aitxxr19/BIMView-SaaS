export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">BIMView</h1>
            </div>
            <nav className="flex space-x-8">
              <a href="/login" className="text-gray-500 hover:text-gray-900">Iniciar Sesión</a>
              <a href="/register" className="btn-primary">Registrarse</a>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl md:text-6xl">
              Convierte Nubes de Puntos a Mallas 3D
            </h1>
            <p className="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
              Plataforma SaaS profesional para conversión de archivos .ply, .las, .laz a mallas 3D optimizadas
            </p>
            <div className="mt-5 max-w-md mx-auto sm:flex sm:justify-center md:mt-8">
              <div className="rounded-md shadow">
                <a href="/register" className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 md:py-4 md:text-lg md:px-10">
                  Comenzar Gratis
                </a>
              </div>
              <div className="mt-3 rounded-md shadow sm:mt-0 sm:ml-3">
                <a href="#features" className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-primary-600 bg-white hover:bg-gray-50 md:py-4 md:text-lg md:px-10">
                  Ver Características
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Features Section */}
        <div id="features" className="py-12 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <h2 className="text-3xl font-bold text-gray-900">Características Principales</h2>
              <p className="mt-4 text-lg text-gray-500">
                Todo lo que necesitas para convertir nubes de puntos a mallas 3D
              </p>
            </div>
            <div className="mt-10 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
              <div className="card">
                <div className="text-primary-600 text-4xl mb-4">⚡</div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Procesamiento Rápido</h3>
                <p className="text-gray-500">Conversión optimizada con algoritmos avanzados de reconstrucción 3D</p>
              </div>
              <div className="card">
                <div className="text-primary-600 text-4xl mb-4">🔒</div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Seguro y Privado</h3>
                <p className="text-gray-500">Tus archivos están protegidos con encriptación y almacenamiento seguro</p>
              </div>
              <div className="card">
                <div className="text-primary-600 text-4xl mb-4">📊</div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Dashboard en Tiempo Real</h3>
                <p className="text-gray-500">Seguimiento en vivo del progreso de tus conversiones</p>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800">
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <p className="text-gray-400">© 2025 BIMView SaaS. Todos los derechos reservados.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

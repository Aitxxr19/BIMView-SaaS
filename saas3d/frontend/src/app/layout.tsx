import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { AuthProvider } from '@/lib/auth'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'BIMView SaaS - Conversión de Nubes de Puntos 3D',
  description: 'Plataforma SaaS para conversión de nubes de puntos (.ply, .las, .laz) a mallas 3D',
  keywords: ['3D', 'point cloud', 'mesh', 'conversion', 'BIM', 'CAD'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es">
      <body className={inter.className}>
        <AuthProvider>
          <div className="min-h-screen bg-gray-50">
            {children}
          </div>
        </AuthProvider>
      </body>
    </html>
  )
}

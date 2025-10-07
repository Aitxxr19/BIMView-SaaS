'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import ProtectedRoute from '@/components/ProtectedRoute'
import FileUpload from '@/components/FileUpload'
import { useFileUpload } from '@/lib/useFileUpload'
import { useJobs } from '@/lib/useJobs'

function UploadContent() {
  const router = useRouter()
  const { uploadFile, isUploading, uploadProgress, error } = useFileUpload()
  const { fetchJobs } = useJobs()
  const [success, setSuccess] = useState(false)
  const [uploadedFile, setUploadedFile] = useState<any>(null)

  const handleUpload = async (file: File) => {
    const result = await uploadFile(file)
    
    if (result.success && result.data) {
      setUploadedFile(result.data)
      setSuccess(true)
      // Actualizar la lista de trabajos
      await fetchJobs()
      
      // Redirigir al dashboard después de 2 segundos
      setTimeout(() => {
        router.push('/dashboard')
      }, 2000)
    }
  }

  if (success && uploadedFile) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <div className="text-green-600 text-6xl mb-4">✅</div>
            <h2 className="text-3xl font-extrabold text-gray-900">¡Archivo Subido!</h2>
            <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-sm text-green-800">
                <strong>Archivo:</strong> {uploadedFile.filename}
              </p>
              <p className="text-sm text-green-800">
                <strong>Tamaño:</strong> {(uploadedFile.file_size / (1024 * 1024)).toFixed(2)} MB
              </p>
              <p className="text-sm text-green-800">
                <strong>Job ID:</strong> {uploadedFile.job_id}
              </p>
            </div>
            <p className="mt-4 text-gray-600">
              Tu archivo ha sido procesado y añadido a la cola de trabajos.
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Redirigiendo al dashboard...
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <button
                onClick={() => router.push('/dashboard')}
                className="text-gray-500 hover:text-gray-900 mr-4"
              >
                ← Volver
              </button>
              <h1 className="text-2xl font-bold text-gray-900">Subir Archivo</h1>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900">Subir Nube de Puntos</h2>
          <p className="mt-2 text-gray-600">
            Sube tu archivo de nube de puntos para convertirlo a malla 3D
          </p>
        </div>

        {/* Upload Area */}
        <div className="card">
          {error && (
            <div className="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
              <strong>Error:</strong> {error}
            </div>
          )}

          <FileUpload
            onUpload={handleUpload}
            isUploading={isUploading}
            maxSize={100}
            acceptedTypes={['.ply', '.las', '.laz', '.pcd', '.xyz']}
          />

          {isUploading && (
            <div className="mt-6">
              <div className="flex justify-between text-sm text-gray-600 mb-2">
                <span>Subiendo archivo...</span>
                <span>{uploadProgress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-primary-600 h-2 rounded-full transition-all duration-300" 
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
            </div>
          )}
        </div>

        {/* Instructions */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="card">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Formatos Soportados</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✓</span>
                PLY (Polygon File Format)
              </li>
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✓</span>
                LAS (Laser Scanning)
              </li>
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✓</span>
                LAZ (Compressed LAS)
              </li>
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✓</span>
                PCD (Point Cloud Data)
              </li>
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✓</span>
                XYZ (Simple Text Format)
              </li>
            </ul>
          </div>

          <div className="card">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Requisitos</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-center">
                <span className="text-blue-500 mr-2">ℹ</span>
                Tamaño máximo: 100MB
              </li>
              <li className="flex items-center">
                <span className="text-blue-500 mr-2">ℹ</span>
                Un archivo por vez
              </li>
              <li className="flex items-center">
                <span className="text-blue-500 mr-2">ℹ</span>
                Procesamiento automático
              </li>
              <li className="flex items-center">
                <span className="text-blue-500 mr-2">ℹ</span>
                Resultado en formato PLY
              </li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  )
}

export default function UploadPage() {
  return (
    <ProtectedRoute>
      <UploadContent />
    </ProtectedRoute>
  )
}

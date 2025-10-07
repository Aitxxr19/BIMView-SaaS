'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'

interface FileUploadProps {
  onUpload: (file: File) => Promise<void>
  isUploading?: boolean
  maxSize?: number // en MB
  acceptedTypes?: string[]
}

export default function FileUpload({ 
  onUpload, 
  isUploading = false,
  maxSize = 100,
  acceptedTypes = ['.ply', '.las', '.laz', '.pcd', '.xyz']
}: FileUploadProps) {
  const [dragActive, setDragActive] = useState(false)

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0]
      await onUpload(file)
    }
  }, [onUpload])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/octet-stream': acceptedTypes,
      'text/plain': ['.xyz'],
    },
    maxSize: maxSize * 1024 * 1024, // Convertir MB a bytes
    multiple: false,
    disabled: isUploading
  })

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive || dragActive 
            ? 'border-primary-500 bg-primary-50' 
            : 'border-gray-300 hover:border-gray-400'
          }
          ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}
        `}
        onDragEnter={() => setDragActive(true)}
        onDragLeave={() => setDragActive(false)}
      >
        <input {...getInputProps()} />
        
        <div className="space-y-4">
          <div className="text-6xl text-gray-400">
            {isUploading ? '⏳' : '📁'}
          </div>
          
          {isUploading ? (
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Subiendo archivo...
              </h3>
              <p className="text-gray-500">
                Por favor espera mientras se procesa tu archivo
              </p>
            </div>
          ) : (
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {isDragActive ? 'Suelta el archivo aquí' : 'Arrastra tu archivo aquí'}
              </h3>
              <p className="text-gray-500 mb-4">
                o haz clic para seleccionar un archivo
              </p>
              
              <div className="text-sm text-gray-400">
                <p>Formatos soportados: {acceptedTypes.join(', ')}</p>
                <p>Tamaño máximo: {maxSize}MB</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

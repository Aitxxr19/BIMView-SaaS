'use client'

import { useState } from 'react'
import { upload, UploadResponse } from '@/lib/api'

export function useFileUpload() {
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)

  const uploadFile = async (file: File): Promise<{ success: boolean; data?: UploadResponse; error?: string }> => {
    setIsUploading(true)
    setError(null)
    setUploadProgress(0)

    try {
      // Simular progreso de subida
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return 90
          }
          return prev + 10
        })
      }, 200)

      const response = await upload.file(file)
      
      clearInterval(progressInterval)
      setUploadProgress(100)

      if (response.data) {
        return { success: true, data: response.data }
      } else {
        setError(response.error || 'Error al subir archivo')
        return { success: false, error: response.error || 'Error al subir archivo' }
      }
    } catch (err) {
      setError('Error de conexión')
      return { success: false, error: 'Error de conexión' }
    } finally {
      setIsUploading(false)
      setTimeout(() => setUploadProgress(0), 1000)
    }
  }

  const reset = () => {
    setIsUploading(false)
    setUploadProgress(0)
    setError(null)
  }

  return {
    uploadFile,
    isUploading,
    uploadProgress,
    error,
    reset,
  }
}

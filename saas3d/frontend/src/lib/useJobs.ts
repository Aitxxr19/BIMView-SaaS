'use client'

import { useState, useEffect } from 'react'
import { jobs, Job } from '@/lib/api'

export function useJobs() {
  const [jobsList, setJobsList] = useState<Job[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchJobs = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const response = await jobs.getAll()
      
      if (response.data) {
        setJobsList(response.data)
      } else {
        setError(response.error || 'Error al cargar trabajos')
      }
    } catch (err) {
      setError('Error de conexión')
    } finally {
      setIsLoading(false)
    }
  }

  const createJob = async (inputKey: string) => {
    try {
      const response = await jobs.create({ input_key: inputKey })
      if (response.data) {
        // Actualizar la lista de trabajos
        await fetchJobs()
        return { success: true, job: response.data }
      } else {
        return { success: false, error: response.error || 'Error al crear trabajo' }
      }
    } catch (err) {
      return { success: false, error: 'Error de conexión' }
    }
  }

  const deleteJob = async (jobId: number) => {
    try {
      const response = await jobs.delete(jobId)
      if (response.data) {
        // Actualizar la lista de trabajos
        await fetchJobs()
        return { success: true }
      } else {
        return { success: false, error: response.error || 'Error al eliminar trabajo' }
      }
    } catch (err) {
      return { success: false, error: 'Error de conexión' }
    }
  }

  useEffect(() => {
    fetchJobs()
  }, [])

  return {
    jobs: jobsList,
    isLoading,
    error,
    fetchJobs,
    createJob,
    deleteJob,
  }
}

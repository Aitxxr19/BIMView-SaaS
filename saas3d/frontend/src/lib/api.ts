// Cliente API centralizado para comunicación con el backend
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface ApiResponse<T> {
  data?: T
  error?: string
  status: number
}

export interface User {
  id: number
  email: string
  is_active: boolean
  is_verified: boolean
  created_at: string
}

export interface Job {
  id: number
  user_id: number
  input_key?: string
  output_key?: string
  status: 'queued' | 'processing' | 'completed' | 'failed'
  progress: number
  error?: string
  task_id?: string
  created_at: string
  finished_at?: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
}

export interface JobCreateRequest {
  input_key: string
}

export interface UploadResponse {
  message: string
  filename: string
  unique_filename: string
  job_id: number
  file_size: number
  file_path: string
}

class ApiClient {
  private baseURL: string
  private token: string | null = null

  constructor(baseURL: string) {
    this.baseURL = baseURL
    // Cargar token del localStorage si existe
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('token')
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}${endpoint}`
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    }

    // Añadir token de autenticación si existe
    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      })

      const data = await response.json()

      if (!response.ok) {
        return {
          error: data.detail || 'Error en la petición',
          status: response.status,
        }
      }

      return {
        data,
        status: response.status,
      }
    } catch (error) {
      return {
        error: 'Error de conexión',
        status: 0,
      }
    }
  }

  // Métodos de autenticación
  async login(credentials: LoginRequest): Promise<ApiResponse<{ access_token: string; token_type: string }>> {
    const response = await this.request<{ access_token: string; token_type: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    })

    if (response.data?.access_token) {
      this.setToken(response.data.access_token)
    }

    return response
  }

  async register(userData: RegisterRequest): Promise<ApiResponse<User>> {
    return this.request<User>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    })
  }

  async getCurrentUser(): Promise<ApiResponse<User>> {
    return this.request<User>('/auth/me')
  }

  // Métodos de jobs
  async getJobs(): Promise<ApiResponse<Job[]>> {
    return this.request<Job[]>('/api/jobs')
  }

  async getJob(jobId: number): Promise<ApiResponse<Job>> {
    return this.request<Job>(`/api/jobs/${jobId}`)
  }

  async createJob(jobData: JobCreateRequest): Promise<ApiResponse<Job>> {
    return this.request<Job>('/api/jobs', {
      method: 'POST',
      body: JSON.stringify(jobData),
    })
  }

  async deleteJob(jobId: number): Promise<ApiResponse<{ message: string }>> {
    return this.request<{ message: string }>(`/api/jobs/${jobId}`, {
      method: 'DELETE',
    })
  }

  // Métodos de subida de archivos
  async uploadFile(file: File): Promise<ApiResponse<UploadResponse>> {
    const formData = new FormData()
    formData.append('file', file)

    const url = `${this.baseURL}/api/upload`
    
    const headers: HeadersInit = {}
    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`
    }

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: formData,
      })

      const data = await response.json()

      if (!response.ok) {
        return {
          error: data.detail || 'Error al subir archivo',
          status: response.status,
        }
      }

      return {
        data,
        status: response.status,
      }
    } catch (error) {
      return {
        error: 'Error de conexión',
        status: 0,
      }
    }
  }

  async downloadFile(filename: string): Promise<Blob | null> {
    const url = `${this.baseURL}/api/files/${filename}`
    
    const headers: HeadersInit = {}
    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`
    }

    try {
      const response = await fetch(url, {
        headers,
      })

      if (!response.ok) {
        return null
      }

      return await response.blob()
    } catch (error) {
      return null
    }
  }

  // Métodos de utilidad
  setToken(token: string) {
    this.token = token
    if (typeof window !== 'undefined') {
      localStorage.setItem('token', token)
    }
  }

  clearToken() {
    this.token = null
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token')
    }
  }

  isAuthenticated(): boolean {
    return !!this.token
  }
}

// Instancia singleton del cliente API
export const apiClient = new ApiClient(API_BASE_URL)

// Funciones de conveniencia
export const auth = {
  login: (credentials: LoginRequest) => apiClient.login(credentials),
  register: (userData: RegisterRequest) => apiClient.register(userData),
  getCurrentUser: () => apiClient.getCurrentUser(),
  logout: () => apiClient.clearToken(),
  isAuthenticated: () => apiClient.isAuthenticated(),
}

export const jobs = {
  getAll: () => apiClient.getJobs(),
  getById: (id: number) => apiClient.getJob(id),
  create: (jobData: JobCreateRequest) => apiClient.createJob(jobData),
  delete: (id: number) => apiClient.deleteJob(id),
}

export const upload = {
  file: (file: File) => apiClient.uploadFile(file),
  download: (filename: string) => apiClient.downloadFile(filename),
}

export default apiClient

import axios from 'axios'
import { ElMessage } from 'element-plus'
import type { ApiResponse } from '@/types'

export const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 30000,
})

http.interceptors.request.use((config) => {
  const userToken = localStorage.getItem('user_token')
  const adminToken = localStorage.getItem('admin_token')
  const isAdmin = config.url?.startsWith('/admin') || config.headers?.['X-Admin-Auth']
  const token = isAdmin ? adminToken : userToken
  if (token) config.headers.Authorization = `Bearer ${token}`
  delete config.headers?.['X-Admin-Auth']
  return config
})

http.interceptors.response.use(
  (response) => response,
  (error) => {
    const detail = error.response?.data?.detail
    const message = typeof detail === 'string' ? detail : detail?.message || error.message || '请求失败'
    ElMessage.error(message)
    return Promise.reject(error)
  },
)

export async function apiGet<T>(url: string, params?: Record<string, unknown>, admin = false) {
  const response = await http.get<ApiResponse<T>>(url, { params, headers: admin ? { 'X-Admin-Auth': '1' } : {} })
  return response.data.data
}

export async function apiPost<T>(url: string, data?: unknown, admin = false) {
  const response = await http.post<ApiResponse<T>>(url, data, { headers: admin ? { 'X-Admin-Auth': '1' } : {} })
  return response.data.data
}

export async function apiPut<T>(url: string, data?: unknown, admin = false) {
  const response = await http.put<ApiResponse<T>>(url, data, { headers: admin ? { 'X-Admin-Auth': '1' } : {} })
  return response.data.data
}

export async function apiDelete<T>(url: string, admin = false) {
  const response = await http.delete<ApiResponse<T>>(url, { headers: admin ? { 'X-Admin-Auth': '1' } : {} })
  return response.data.data
}


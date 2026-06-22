import { apiDelete, apiGet, apiPost, apiPut } from './http'
import type { Admin, AiResponse, Cart, Category, Order, PageResponse, Product, User } from '@/types'

export const mallApi = {
  register: (data: { username: string; password: string; phone?: string }) => apiPost<User>('/auth/register', data),
  login: (data: { username: string; password: string }) =>
    apiPost<{ access_token: string; user: User }>('/auth/login', data),
  me: () => apiGet<User>('/users/me'),
  categories: () => apiGet<Category[]>('/categories'),
  products: (params?: Record<string, unknown>) => apiGet<PageResponse<Product>>('/products', params),
  hotProducts: (limit = 8) => apiGet<Product[]>('/products/hot', { limit }),
  product: (id: number) => apiGet<Product>(`/products/${id}`),
  cart: () => apiGet<Cart>('/cart'),
  addCart: (data: { product_id: number; quantity: number }) => apiPost<Cart>('/cart/items', data),
  updateCart: (id: number, data: { quantity?: number; selected?: boolean }) => apiPut<Cart>(`/cart/items/${id}`, data),
  deleteCart: (id: number) => apiDelete<Cart>(`/cart/items/${id}`),
  createOrder: (data: unknown) => apiPost<{ order_id: number; order_no: string; total_amount: string; status: string }>('/orders', data),
  orders: () => apiGet<PageResponse<Order>>('/orders'),
  payOrder: (id: number) => apiPost<{ balance: string; status: string }>(`/orders/${id}/pay`),
  cancelOrder: (id: number) => apiPut<{ balance: string; status: string }>(`/orders/${id}/cancel`),
  aiChat: (data: { agent_type: string; message: string; conversation_id?: number }) => apiPost<AiResponse>('/ai/chat', data),
}

export const adminApi = {
  login: (data: { username: string; password: string }) =>
    apiPost<{ access_token: string; admin: Admin }>('/admin/auth/login', data, true),
  dashboard: () => apiGet<{ today_sales_amount: string; today_order_count: number; user_count: number; inventory_alert_count: number }>('/admin/dashboard', undefined, true),
  products: (params?: Record<string, unknown>) => apiGet<PageResponse<Product>>('/admin/products', params, true),
  createProduct: (data: Partial<Product>) => apiPost<Product>('/admin/products', data, true),
  updateProduct: (id: number, data: Partial<Product>) => apiPut<Product>(`/admin/products/${id}`, data, true),
  updateProductStatus: (id: number, status: string) => apiPut<Product>(`/admin/products/${id}/status`, { status }, true),
  deleteProduct: (id: number) => apiDelete<Product>(`/admin/products/${id}`, true),
  categories: () => apiGet<Category[]>('/admin/categories', undefined, true),
  createCategory: (data: Partial<Category>) => apiPost<Category>('/admin/categories', data, true),
  updateCategory: (id: number, data: Partial<Category>) => apiPut<Category>(`/admin/categories/${id}`, data, true),
  updateCategoryStatus: (id: number, status: string) => apiPut<Category>(`/admin/categories/${id}/status`, { status }, true),
  orders: (params?: Record<string, unknown>) => apiGet<PageResponse<Order>>('/admin/orders', params, true),
  updateOrderStatus: (id: number, status: string) => apiPut<Order>(`/admin/orders/${id}/status`, { status }, true),
  users: (params?: Record<string, unknown>) => apiGet<PageResponse<User>>('/admin/users', params, true),
  updateUserStatus: (id: number, status: string) => apiPut<User>(`/admin/users/${id}/status`, { status }, true),
  inventoryAlerts: (params?: Record<string, unknown>) => apiGet<PageResponse<any>>('/admin/inventory/alerts', params, true),
  updateAlertStatus: (id: number, status: string) => apiPut<any>(`/admin/inventory/alerts/${id}/status`, { status }, true),
  salesStatistics: (params?: Record<string, unknown>) => apiGet<any[]>('/admin/sales/statistics', params, true),
  predictSales: (data: { product_id: number; days: number }) => apiPost<any>('/admin/sales/predict', data, true),
  toolCalls: () => apiGet<PageResponse<any>>('/admin/ai/tool-calls', undefined, true),
  aiChat: (data: { agent_type: string; message: string; conversation_id?: number }) => apiPost<AiResponse>('/ai/chat', data, true),
}


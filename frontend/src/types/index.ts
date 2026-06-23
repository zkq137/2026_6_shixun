export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export interface PageResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export interface User {
  id: number
  username: string
  nickname?: string
  phone?: string
  email?: string
  balance: string
  status: string
}

export interface Admin {
  id: number
  username: string
  role: string
  status: string
}

export interface Category {
  id: number
  name: string
  parent_id: number
  sort_order: number
  status: string
}

export interface Product {
  id: number
  category_id: number
  name: string
  subtitle?: string
  main_image?: string
  price: string
  stock: number
  sales_count: number
  description?: string
  status: string
}

export interface Review {
  id: number
  product_id: number
  user_id: number
  username: string
  nickname?: string
  rating: number
  content: string
  is_anonymous: boolean
  is_purchased: boolean
  status: string
  created_at?: string
}

export interface AdminReview extends Review {
  product_name: string
  order_id?: number
  updated_at?: string
}

export interface ReviewPage extends PageResponse<Review> {
  summary: {
    total: number
    average_rating: number
  }
}

export interface UploadResult {
  url: string
  filename: string
  size: number
  content_type: string
}

export interface CartItem {
  id: number
  product_id: number
  product_name: string
  product_image?: string
  price: string
  stock: number
  quantity: number
  selected: boolean
  subtotal: string
}

export interface Cart {
  items: CartItem[]
  total_amount: string
}

export interface OrderItem {
  id: number
  product_id: number
  product_name: string
  product_image?: string
  price: string
  quantity: number
  subtotal: string
}

export interface Order {
  id: number
  order_no: string
  total_amount: string
  status: string
  receiver_name: string
  receiver_phone: string
  receiver_address: string
  remark?: string
  created_at?: string
  items: OrderItem[]
}

export interface AiResponse {
  conversation_id: number
  agent_type: string
  answer: string
  tool_calls: Array<{ tool_name: string; status: string }>
}

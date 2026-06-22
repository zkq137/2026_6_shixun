import { defineStore } from 'pinia'
import { mallApi, adminApi } from '@/api'
import type { Admin, User } from '@/types'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as User | null,
    admin: null as Admin | null,
    userToken: localStorage.getItem('user_token') || '',
    adminToken: localStorage.getItem('admin_token') || '',
  }),
  actions: {
    async login(username: string, password: string) {
      const data = await mallApi.login({ username, password })
      this.userToken = data.access_token
      this.user = data.user
      localStorage.setItem('user_token', data.access_token)
    },
    async register(username: string, password: string, phone?: string) {
      await mallApi.register({ username, password, phone })
      await this.login(username, password)
    },
    async loadMe() {
      if (!this.userToken) return
      this.user = await mallApi.me()
    },
    logout() {
      this.user = null
      this.userToken = ''
      localStorage.removeItem('user_token')
    },
    async adminLogin(username: string, password: string) {
      const data = await adminApi.login({ username, password })
      this.adminToken = data.access_token
      this.admin = data.admin
      localStorage.setItem('admin_token', data.access_token)
    },
    adminLogout() {
      this.admin = null
      this.adminToken = ''
      localStorage.removeItem('admin_token')
    },
  },
})


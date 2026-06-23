import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import UserLayout from '@/layouts/UserLayout.vue'
import AdminLayout from '@/layouts/AdminLayout.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: UserLayout,
      children: [
        { path: '', component: () => import('@/views/HomeView.vue') },
        { path: 'login', component: () => import('@/views/LoginView.vue') },
        { path: 'products', component: () => import('@/views/ProductsView.vue') },
        { path: 'products/:id', component: () => import('@/views/ProductDetailView.vue') },
        { path: 'cart', component: () => import('@/views/CartView.vue'), meta: { user: true } },
        { path: 'checkout', component: () => import('@/views/CheckoutView.vue'), meta: { user: true } },
        { path: 'orders', component: () => import('@/views/OrdersView.vue'), meta: { user: true } },
        { path: 'profile', component: () => import('@/views/ProfileView.vue'), meta: { user: true } },
        { path: 'ai/customer-service', component: () => import('@/views/AiCustomerView.vue'), meta: { user: true } },
      ],
    },
    { path: '/admin/login', component: () => import('@/views/admin/AdminLoginView.vue') },
    {
      path: '/admin',
      component: AdminLayout,
      meta: { admin: true },
      children: [
        { path: '', redirect: '/admin/dashboard' },
        { path: 'dashboard', component: () => import('@/views/admin/AdminDashboardView.vue') },
        { path: 'products', component: () => import('@/views/admin/AdminProductsView.vue') },
        { path: 'categories', component: () => import('@/views/admin/AdminCategoriesView.vue') },
        { path: 'orders', component: () => import('@/views/admin/AdminOrdersView.vue') },
        { path: 'reviews', component: () => import('@/views/admin/AdminReviewsView.vue') },
        { path: 'users', component: () => import('@/views/admin/AdminUsersView.vue') },
        { path: 'inventory', component: () => import('@/views/admin/AdminInventoryView.vue') },
        { path: 'ai/operation', component: () => import('@/views/admin/AdminAiView.vue') },
        { path: 'ai/tool-calls', component: () => import('@/views/admin/AdminToolCallsView.vue') },
      ],
    },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.user && !auth.userToken) return '/login'
  if (to.meta.admin && !auth.adminToken) return '/admin/login'
})

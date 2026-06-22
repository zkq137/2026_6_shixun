<template>
  <el-container class="admin-shell">
    <el-aside width="230px">
      <div class="admin-brand">AI商城后台</div>
      <el-menu router default-active="/admin/dashboard">
        <el-menu-item index="/admin/dashboard">数据看板</el-menu-item>
        <el-menu-item index="/admin/products">商品管理</el-menu-item>
        <el-menu-item index="/admin/categories">分类管理</el-menu-item>
        <el-menu-item index="/admin/orders">订单管理</el-menu-item>
        <el-menu-item index="/admin/users">用户管理</el-menu-item>
        <el-menu-item index="/admin/inventory">库存管理</el-menu-item>
        <el-menu-item index="/admin/ai/operation">AI运营助手</el-menu-item>
        <el-menu-item index="/admin/ai/tool-calls">工具日志</el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="admin-header">
        <span>{{ auth.admin?.username || '管理员' }}</span>
        <el-button @click="logout">退出</el-button>
      </el-header>
      <el-main>
        <RouterView />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

function logout() {
  auth.adminLogout()
  router.push('/admin/login')
}
</script>

<style scoped>
.admin-shell {
  min-height: 100vh;
}

.admin-brand {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  font-size: 18px;
  font-weight: 800;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
}

.admin-header {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  align-items: center;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
}
</style>


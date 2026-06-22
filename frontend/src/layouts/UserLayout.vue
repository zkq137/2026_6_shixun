<template>
  <el-container>
    <el-header class="user-header">
      <RouterLink class="brand" to="/">AI智能商城</RouterLink>
      <el-menu mode="horizontal" router :ellipsis="false" class="nav">
        <el-menu-item index="/">首页</el-menu-item>
        <el-menu-item index="/products">商品</el-menu-item>
        <el-menu-item index="/cart">购物车</el-menu-item>
        <el-menu-item index="/orders">订单</el-menu-item>
        <el-menu-item index="/ai/customer-service">AI客服</el-menu-item>
      </el-menu>
      <div class="actions">
        <RouterLink v-if="!auth.userToken" to="/login">
          <el-button type="primary">登录</el-button>
        </RouterLink>
        <template v-else>
          <RouterLink to="/profile">
            <el-button>{{ auth.user?.nickname || auth.user?.username || '个人中心' }}</el-button>
          </RouterLink>
          <el-button @click="auth.logout()">退出</el-button>
        </template>
        <RouterLink to="/admin/login">
          <el-button text>后台</el-button>
        </RouterLink>
      </div>
    </el-header>
    <el-main>
      <RouterView />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
onMounted(() => auth.loadMe())
</script>

<style scoped>
.user-header {
  display: flex;
  align-items: center;
  gap: 18px;
  border-bottom: 1px solid #e5e7eb;
  background: #fff;
}

.brand {
  font-size: 20px;
  font-weight: 800;
  white-space: nowrap;
}

.nav {
  flex: 1;
  border-bottom: 0;
}

.actions {
  display: flex;
  gap: 8px;
  align-items: center;
}
</style>


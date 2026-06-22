<template>
  <div class="page" style="max-width: 720px">
    <el-card v-if="auth.user">
      <h2>个人中心</h2>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="用户名">{{ auth.user.username }}</el-descriptions-item>
        <el-descriptions-item label="昵称">{{ auth.user.nickname }}</el-descriptions-item>
        <el-descriptions-item label="手机号">{{ auth.user.phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="商城币余额">¥{{ auth.user.balance }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{ auth.user.status }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
const auth = useAuthStore()
onMounted(() => auth.loadMe())
</script>


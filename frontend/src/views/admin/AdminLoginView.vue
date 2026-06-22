<template>
  <div class="page" style="max-width: 420px">
    <el-card>
      <h2>后台登录</h2>
      <el-form label-position="top">
        <el-form-item label="账号"><el-input v-model="form.username" /></el-form-item>
        <el-form-item label="密码"><el-input v-model="form.password" type="password" show-password /></el-form-item>
        <el-button type="primary" style="width: 100%" @click="submit">登录</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const form = reactive({ username: 'admin', password: 'admin123456' })
async function submit() {
  await auth.adminLogin(form.username, form.password)
  router.push('/admin/dashboard')
}
</script>


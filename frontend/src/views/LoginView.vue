<template>
  <div class="page" style="max-width: 460px">
    <el-card>
      <el-tabs v-model="mode">
        <el-tab-pane label="登录" name="login" />
        <el-tab-pane label="注册" name="register" />
      </el-tabs>
      <el-form label-position="top">
        <el-form-item label="用户名"><el-input v-model="form.username" /></el-form-item>
        <el-form-item label="密码"><el-input v-model="form.password" type="password" show-password /></el-form-item>
        <el-form-item v-if="mode === 'register'" label="手机号"><el-input v-model="form.phone" /></el-form-item>
        <el-button type="primary" style="width: 100%" @click="submit">{{ mode === 'login' ? '登录' : '注册' }}</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const mode = ref('login')
const form = reactive({ username: '', password: '', phone: '' })

async function submit() {
  if (mode.value === 'login') await auth.login(form.username, form.password)
  else await auth.register(form.username, form.password, form.phone)
  router.push('/')
}
</script>


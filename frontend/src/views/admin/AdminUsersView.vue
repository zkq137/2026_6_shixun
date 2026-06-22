<template>
  <div class="admin-page">
    <el-table :data="items">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="balance" label="余额" width="120" />
      <el-table-column prop="status" label="状态" width="120" />
      <el-table-column label="操作" width="140"><template #default="{ row }"><el-button size="small" @click="toggle(row)">{{ row.status === 'normal' ? '禁用' : '启用' }}</el-button></template></el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { adminApi } from '@/api'
import type { User } from '@/types'
const items = ref<User[]>([])
async function load() { items.value = (await adminApi.users()).items }
async function toggle(row: User) { await adminApi.updateUserStatus(row.id, row.status === 'normal' ? 'disabled' : 'normal'); await load() }
onMounted(load)
</script>


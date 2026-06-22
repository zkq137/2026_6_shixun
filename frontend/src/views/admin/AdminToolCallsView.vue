<template>
  <div class="admin-page">
    <el-table :data="items">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="agent_type" label="Agent" width="130" />
      <el-table-column prop="tool_name" label="工具" width="180" />
      <el-table-column prop="status" label="状态" width="100" />
      <el-table-column prop="duration_ms" label="耗时ms" width="100" />
      <el-table-column prop="created_at" label="时间" width="180" />
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { adminApi } from '@/api'
const items = ref<any[]>([])
onMounted(async () => { items.value = (await adminApi.toolCalls()).items })
</script>


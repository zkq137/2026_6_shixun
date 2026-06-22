<template>
  <div class="admin-page">
    <el-table :data="items">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="product_id" label="商品ID" width="100" />
      <el-table-column prop="current_stock" label="库存" width="100" />
      <el-table-column prop="predicted_sales" label="预测销量" width="120" />
      <el-table-column prop="risk_level" label="风险" width="100" />
      <el-table-column prop="suggestion" label="建议" />
      <el-table-column prop="status" label="状态" width="100" />
      <el-table-column label="操作" width="110"><template #default="{ row }"><el-button size="small" @click="handle(row)">处理</el-button></template></el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { adminApi } from '@/api'
const items = ref<any[]>([])
async function load() { items.value = (await adminApi.inventoryAlerts()).items }
async function handle(row: any) { await adminApi.updateAlertStatus(row.id, 'handled'); await load() }
onMounted(load)
</script>


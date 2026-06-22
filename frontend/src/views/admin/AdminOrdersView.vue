<template>
  <div class="admin-page">
    <el-table :data="items">
      <el-table-column prop="order_no" label="订单号" min-width="180" />
      <el-table-column prop="total_amount" label="金额" width="110" />
      <el-table-column prop="status" label="状态" width="120" />
      <el-table-column prop="receiver_name" label="收货人" width="120" />
      <el-table-column label="操作" width="180"><template #default="{ row }"><el-select v-model="row.status" @change="update(row)" size="small"><el-option v-for="s in statuses" :key="s" :label="s" :value="s" /></el-select></template></el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { adminApi } from '@/api'
import type { Order } from '@/types'
const items = ref<Order[]>([])
const statuses = ['pending', 'paid', 'shipped', 'completed', 'cancelled']
async function load() { items.value = (await adminApi.orders()).items }
async function update(row: Order) { await adminApi.updateOrderStatus(row.id, row.status) }
onMounted(load)
</script>


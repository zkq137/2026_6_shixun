<template>
  <div class="page">
    <h2>我的订单</h2>
    <el-table :data="orders">
      <el-table-column prop="order_no" label="订单号" min-width="180" />
      <el-table-column prop="total_amount" label="金额" width="120" />
      <el-table-column prop="status" label="状态" width="120" />
      <el-table-column label="操作" width="220">
        <template #default="{ row }">
          <el-button v-if="row.status === 'pending'" size="small" type="primary" @click="pay(row.id)">支付</el-button>
          <el-button v-if="['pending','paid'].includes(row.status)" size="small" @click="cancel(row.id)">取消</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { mallApi } from '@/api'
import type { Order } from '@/types'

const orders = ref<Order[]>([])
async function load() { orders.value = (await mallApi.orders()).items }
async function pay(id: number) { await mallApi.payOrder(id); await load() }
async function cancel(id: number) { await mallApi.cancelOrder(id); await load() }
onMounted(load)
</script>


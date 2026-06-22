<template>
  <div class="admin-page">
    <div class="stat-grid">
      <el-card><p class="muted">今日销售额</p><h2>¥{{ stats.today_sales_amount }}</h2></el-card>
      <el-card><p class="muted">今日订单</p><h2>{{ stats.today_order_count }}</h2></el-card>
      <el-card><p class="muted">用户数</p><h2>{{ stats.user_count }}</h2></el-card>
      <el-card><p class="muted">库存预警</p><h2>{{ stats.inventory_alert_count }}</h2></el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive } from 'vue'
import { adminApi } from '@/api'

const stats = reactive({ today_sales_amount: '0.00', today_order_count: 0, user_count: 0, inventory_alert_count: 0 })
onMounted(async () => Object.assign(stats, await adminApi.dashboard()))
</script>


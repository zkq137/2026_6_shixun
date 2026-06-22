<template>
  <el-card class="product-card" shadow="hover" @click="$router.push(`/products/${product.id}`)">
    <div class="image">{{ product.name.slice(0, 2) }}</div>
    <h3>{{ product.name }}</h3>
    <p class="muted">{{ product.subtitle || '精选商品' }}</p>
    <div class="section-title">
      <span class="price">¥{{ product.price }}</span>
      <span class="muted">销量 {{ product.sales_count }}</span>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import type { Product } from '@/types'

defineProps<{ product: Product }>()
</script>


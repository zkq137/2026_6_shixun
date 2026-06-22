<template>
  <div class="page">
    <div class="section-title">
      <h2>热门商品</h2>
      <RouterLink to="/products"><el-button type="primary">查看全部</el-button></RouterLink>
    </div>
    <el-space wrap style="margin-bottom: 18px">
      <el-tag v-for="item in categories" :key="item.id">{{ item.name }}</el-tag>
    </el-space>
    <div class="product-grid">
      <ProductCard v-for="item in products" :key="item.id" :product="item" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { mallApi } from '@/api'
import ProductCard from '@/components/ProductCard.vue'
import type { Category, Product } from '@/types'

const categories = ref<Category[]>([])
const products = ref<Product[]>([])

onMounted(async () => {
  categories.value = await mallApi.categories()
  products.value = await mallApi.hotProducts(8)
})
</script>


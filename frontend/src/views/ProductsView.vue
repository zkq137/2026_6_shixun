<template>
  <div class="page">
    <div class="toolbar">
      <el-input v-model="query.keyword" placeholder="搜索商品" style="width: 240px" clearable />
      <el-select v-model="query.category_id" placeholder="分类" clearable style="width: 180px">
        <el-option v-for="item in categories" :key="item.id" :label="item.name" :value="item.id" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
    </div>
    <div class="product-grid">
      <ProductCard v-for="item in products" :key="item.id" :product="item" />
    </div>
    <el-pagination style="margin-top: 20px" layout="prev, pager, next" :total="total" v-model:current-page="query.page" @current-change="load" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { mallApi } from '@/api'
import ProductCard from '@/components/ProductCard.vue'
import type { Category, Product } from '@/types'

const categories = ref<Category[]>([])
const products = ref<Product[]>([])
const total = ref(0)
const query = reactive<{ keyword: string; category_id?: number; page: number; page_size: number }>({ keyword: '', page: 1, page_size: 12 })

async function load() {
  const data = await mallApi.products(query)
  products.value = data.items
  total.value = data.total
}

onMounted(async () => {
  categories.value = await mallApi.categories()
  await load()
})
</script>


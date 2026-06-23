<template>
  <div class="page" v-if="product">
    <el-row :gutter="24">
      <el-col :span="10">
        <div class="product-image">
          <img v-if="imageUrl && !imageFailed" :src="imageUrl" :alt="product.name" @error="imageFailed = true" />
          <span v-else>{{ product.name.slice(0, 2) }}</span>
        </div>
      </el-col>
      <el-col :span="14">
        <h1>{{ product.name }}</h1>
        <p class="muted">{{ product.subtitle }}</p>
        <p class="price" style="font-size: 26px">¥{{ product.price }}</p>
        <p>库存 {{ product.stock }} / 销量 {{ product.sales_count }}</p>
        <p>{{ product.description }}</p>
        <div class="toolbar">
          <el-input-number v-model="quantity" :min="1" :max="product.stock" />
          <el-button type="primary" @click="add">加入购物车</el-button>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { mallApi } from '@/api'
import type { Product } from '@/types'
import { resolveImageUrl } from '@/utils/image'

const route = useRoute()
const router = useRouter()
const product = ref<Product>()
const quantity = ref(1)
const imageFailed = ref(false)
const imageUrl = computed(() => resolveImageUrl(product.value?.main_image))

watch(imageUrl, () => {
  imageFailed.value = false
})

async function add() {
  if (!product.value) return
  await mallApi.addCart({ product_id: product.value.id, quantity: quantity.value })
  ElMessage.success('已加入购物车')
  router.push('/cart')
}

onMounted(async () => {
  product.value = await mallApi.product(Number(route.params.id))
})
</script>

<style scoped>
.product-image {
  display: grid;
  place-items: center;
  aspect-ratio: 4 / 3;
  overflow: hidden;
  border-radius: 8px;
  background: #e2e8f0;
  color: #64748b;
  font-size: 42px;
  font-weight: 800;
}

.product-image img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>

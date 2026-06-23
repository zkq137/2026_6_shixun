<template>
  <el-card class="product-card" shadow="hover" @click="$router.push(`/products/${product.id}`)">
    <div class="image">
      <img v-if="imageUrl && !imageFailed" :src="imageUrl" :alt="product.name" @error="imageFailed = true" />
      <span v-else>{{ product.name.slice(0, 2) }}</span>
    </div>
    <h3>{{ product.name }}</h3>
    <p class="muted">{{ product.subtitle || '精选商品' }}</p>
    <div class="section-title">
      <span class="price">¥{{ product.price }}</span>
      <span class="muted">销量 {{ product.sales_count }}</span>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { Product } from '@/types'
import { resolveImageUrl } from '@/utils/image'

const props = defineProps<{ product: Product }>()
const imageFailed = ref(false)
const imageUrl = computed(() => resolveImageUrl(props.product.main_image))

watch(
  () => props.product.main_image,
  () => {
    imageFailed.value = false
  },
)
</script>

<style scoped>
.image {
  overflow: hidden;
}

.image img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>

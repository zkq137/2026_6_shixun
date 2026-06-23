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
    <section class="reviews">
      <div class="review-header">
        <h2>商品评价</h2>
        <div class="review-summary">
          <el-rate :model-value="reviewSummary.average_rating" disabled allow-half />
          <span>{{ reviewSummary.average_rating.toFixed(1) }} 分 / {{ reviewSummary.total }} 条评价</span>
        </div>
      </div>

      <el-form v-if="auth.userToken" class="review-form" label-position="top">
        <el-form-item label="评分">
          <el-rate v-model="reviewForm.rating" />
        </el-form-item>
        <el-form-item label="评价内容">
          <el-input
            v-model="reviewForm.content"
            type="textarea"
            :rows="3"
            maxlength="1000"
            show-word-limit
            placeholder="说说这个商品的使用感受"
          />
        </el-form-item>
        <div class="review-form-actions">
          <el-checkbox v-model="reviewForm.is_anonymous">匿名评价</el-checkbox>
          <el-button type="primary" @click="submitReview">提交评价</el-button>
        </div>
      </el-form>
      <el-alert v-else title="登录后可以发表评价" type="info" show-icon :closable="false" />

      <el-empty v-if="reviews.length === 0" description="暂无评价" />
      <div v-else class="review-list">
        <div v-for="review in reviews" :key="review.id" class="review-item">
          <div class="review-meta">
            <strong>{{ review.nickname || review.username }}</strong>
            <el-tag v-if="review.is_purchased" size="small" type="success">已购买</el-tag>
            <span>{{ formatTime(review.created_at) }}</span>
          </div>
          <el-rate :model-value="review.rating" disabled />
          <p>{{ review.content }}</p>
        </div>
      </div>
      <el-pagination
        v-if="reviewTotal > reviewQuery.page_size"
        class="review-pagination"
        v-model:current-page="reviewQuery.page"
        :page-size="reviewQuery.page_size"
        :total="reviewTotal"
        layout="prev, pager, next"
        @current-change="loadReviews"
      />
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { mallApi } from '@/api'
import { useAuthStore } from '@/stores/auth'
import type { Product, Review } from '@/types'
import { resolveImageUrl } from '@/utils/image'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const product = ref<Product>()
const quantity = ref(1)
const imageFailed = ref(false)
const imageUrl = computed(() => resolveImageUrl(product.value?.main_image))
const reviews = ref<Review[]>([])
const reviewTotal = ref(0)
const reviewSummary = reactive({ total: 0, average_rating: 0 })
const reviewQuery = reactive({ page: 1, page_size: 5 })
const reviewForm = reactive({ rating: 5, content: '', is_anonymous: false })

watch(imageUrl, () => {
  imageFailed.value = false
})

async function add() {
  if (!product.value) return
  await mallApi.addCart({ product_id: product.value.id, quantity: quantity.value })
  ElMessage.success('已加入购物车')
  router.push('/cart')
}

async function loadReviews() {
  if (!product.value) return
  const data = await mallApi.productReviews(product.value.id, reviewQuery)
  reviews.value = data.items
  reviewTotal.value = data.total
  reviewSummary.total = data.summary.total
  reviewSummary.average_rating = data.summary.average_rating
}

async function submitReview() {
  if (!product.value) return
  if (!reviewForm.content.trim()) {
    ElMessage.warning('请填写评价内容')
    return
  }
  await mallApi.createProductReview(product.value.id, {
    rating: reviewForm.rating,
    content: reviewForm.content,
    is_anonymous: reviewForm.is_anonymous,
  })
  ElMessage.success('评价已提交')
  reviewForm.rating = 5
  reviewForm.content = ''
  reviewForm.is_anonymous = false
  reviewQuery.page = 1
  await loadReviews()
}

function formatTime(value?: string) {
  return value ? new Date(value).toLocaleString() : ''
}

onMounted(async () => {
  product.value = await mallApi.product(Number(route.params.id))
  await loadReviews()
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

.reviews {
  margin-top: 28px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

.review-header,
.review-form-actions,
.review-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.review-header {
  justify-content: space-between;
  margin-bottom: 16px;
}

.review-summary {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #64748b;
}

.review-form {
  margin-bottom: 20px;
  padding: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #fff;
}

.review-form-actions {
  justify-content: space-between;
}

.review-list {
  display: grid;
  gap: 12px;
}

.review-item {
  padding: 14px 0;
  border-bottom: 1px solid #e5e7eb;
}

.review-meta {
  margin-bottom: 6px;
  color: #64748b;
}

.review-meta strong {
  color: #111827;
}

.review-pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
</style>

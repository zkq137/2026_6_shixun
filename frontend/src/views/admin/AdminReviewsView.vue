<template>
  <div class="admin-page">
    <div class="toolbar">
      <el-select v-model="status" clearable placeholder="评论状态" style="width: 160px" @change="search">
        <el-option label="显示中" value="visible" />
        <el-option label="已隐藏" value="hidden" />
      </el-select>
      <el-button type="primary" @click="search">筛选</el-button>
    </div>

    <el-table :data="items">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="product_name" label="商品" min-width="160" />
      <el-table-column label="用户" width="140">
        <template #default="{ row }">{{ row.nickname || row.username }}</template>
      </el-table-column>
      <el-table-column label="评分" width="150">
        <template #default="{ row }"><el-rate :model-value="row.rating" disabled /></template>
      </el-table-column>
      <el-table-column prop="content" label="内容" min-width="260" show-overflow-tooltip />
      <el-table-column label="标识" width="120">
        <template #default="{ row }">
          <el-tag v-if="row.is_purchased" size="small" type="success">已购买</el-tag>
          <el-tag v-if="row.is_anonymous" size="small" type="info">匿名</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'visible' ? 'success' : 'info'">
            {{ row.status === 'visible' ? '显示中' : '已隐藏' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="时间" width="190">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="110">
        <template #default="{ row }">
          <el-button size="small" @click="toggle(row)">
            {{ row.status === 'visible' ? '隐藏' : '恢复' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 30, 50]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="load"
        @size-change="handleSizeChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { adminApi } from '@/api'
import type { AdminReview } from '@/types'

const items = ref<AdminReview[]>([])
const status = ref('')
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

async function load() {
  const data = await adminApi.reviews({
    status: status.value || undefined,
    page: page.value,
    page_size: pageSize.value,
  })
  items.value = data.items
  total.value = data.total
}

async function search() {
  page.value = 1
  await load()
}

async function handleSizeChange(size: number) {
  pageSize.value = size
  page.value = 1
  await load()
}

async function toggle(row: AdminReview) {
  const nextStatus = row.status === 'visible' ? 'hidden' : 'visible'
  await adminApi.updateReviewStatus(row.id, nextStatus)
  ElMessage.success(nextStatus === 'visible' ? '评论已恢复' : '评论已隐藏')
  await load()
}

function formatTime(value?: string) {
  return value ? new Date(value).toLocaleString() : ''
}

onMounted(load)
</script>

<style scoped>
.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>

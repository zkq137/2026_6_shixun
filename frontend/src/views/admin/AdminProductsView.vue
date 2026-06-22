<template>
  <div class="admin-page">
    <div class="toolbar">
      <el-input v-model="keyword" placeholder="商品名" style="width: 220px" />
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button @click="openCreate">新增商品</el-button>
    </div>
    <el-table :data="items">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="price" label="价格" width="100" />
      <el-table-column prop="stock" label="库存" width="100" />
      <el-table-column prop="status" label="状态" width="110" />
      <el-table-column label="操作" width="260">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" @click="toggle(row)">{{ row.status === 'on_sale' ? '下架' : '上架' }}</el-button>
          <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="dialog" title="商品">
      <el-form label-position="top">
        <el-form-item label="分类"><el-select v-model="form.category_id"><el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" /></el-select></el-form-item>
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="副标题"><el-input v-model="form.subtitle" /></el-form-item>
        <el-form-item label="价格"><el-input v-model="form.price" /></el-form-item>
        <el-form-item label="库存"><el-input-number v-model="form.stock" :min="0" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialog=false">取消</el-button><el-button type="primary" @click="save">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { adminApi } from '@/api'
import type { Category, Product } from '@/types'

const items = ref<Product[]>([])
const categories = ref<Category[]>([])
const keyword = ref('')
const dialog = ref(false)
const editingId = ref<number>()
const form = reactive<any>({ category_id: 1, name: '', subtitle: '', price: '1.00', stock: 1, description: '', status: 'on_sale' })
async function load() { items.value = (await adminApi.products({ keyword: keyword.value })).items }
function openCreate() { editingId.value = undefined; Object.assign(form, { category_id: categories.value[0]?.id || 1, name: '', subtitle: '', price: '1.00', stock: 1, description: '', status: 'on_sale' }); dialog.value = true }
function openEdit(row: Product) { editingId.value = row.id; Object.assign(form, row); dialog.value = true }
async function save() { editingId.value ? await adminApi.updateProduct(editingId.value, form) : await adminApi.createProduct(form); dialog.value = false; await load() }
async function toggle(row: Product) { await adminApi.updateProductStatus(row.id, row.status === 'on_sale' ? 'off_sale' : 'on_sale'); await load() }
async function remove(row: Product) { await adminApi.deleteProduct(row.id); await load() }
onMounted(async () => { categories.value = await adminApi.categories(); await load() })
</script>


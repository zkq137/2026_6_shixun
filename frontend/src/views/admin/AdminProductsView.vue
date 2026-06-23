<template>
  <div class="admin-page">
    <div class="toolbar">
      <el-input v-model="keyword" placeholder="商品名称" style="width: 220px" />
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button @click="openCreate">新增商品</el-button>
    </div>
    <el-table :data="items">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column label="主图" width="92">
        <template #default="{ row }">
          <div class="thumb">
            <img v-if="resolveImageUrl(row.main_image)" :src="resolveImageUrl(row.main_image)" :alt="row.name" />
            <span v-else>{{ row.name.slice(0, 2) }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="price" label="价格" width="100" />
      <el-table-column prop="stock" label="库存" width="100" />
      <el-table-column prop="status" label="状态" width="110" />
      <el-table-column label="操作" width="260">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" @click="toggle(row)">{{ row.status === 'on_sale' ? '下架' : '上架' }}</el-button>
          <el-button size="small" type="danger" @click="remove(row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="dialog" title="商品" width="680px">
      <el-form label-position="top">
        <el-form-item label="分类">
          <el-select v-model="form.category_id">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="副标题"><el-input v-model="form.subtitle" /></el-form-item>
        <el-form-item label="商品主图">
          <div class="image-manager">
            <div class="preview">
              <img v-if="previewUrl" :src="previewUrl" :alt="form.name || '商品主图'" />
              <span v-else>暂无图片</span>
            </div>
            <div class="image-actions">
              <el-upload
                :auto-upload="false"
                :show-file-list="false"
                accept="image/jpeg,image/png,image/webp,image/gif"
                :on-change="uploadImage"
              >
                <el-button :loading="uploading" type="primary">上传主图</el-button>
              </el-upload>
              <el-button :disabled="!form.main_image" @click="clearImage">清空图片</el-button>
            </div>
          </div>
        </el-form-item>
        <el-form-item label="图片路径或 URL">
          <el-input v-model="form.main_image" placeholder="/uploads/products/xxx.jpg 或 https://..." />
        </el-form-item>
        <el-form-item label="价格"><el-input v-model="form.price" /></el-form-item>
        <el-form-item label="库存"><el-input-number v-model="form.stock" :min="0" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { UploadFile } from 'element-plus'
import { adminApi } from '@/api'
import type { Category, Product } from '@/types'
import { resolveImageUrl } from '@/utils/image'

const items = ref<Product[]>([])
const categories = ref<Category[]>([])
const keyword = ref('')
const dialog = ref(false)
const uploading = ref(false)
const editingId = ref<number>()
const form = reactive<any>({
  category_id: 1,
  name: '',
  subtitle: '',
  main_image: '',
  price: '1.00',
  stock: 1,
  description: '',
  status: 'on_sale',
})

const previewUrl = computed(() => resolveImageUrl(form.main_image))

async function load() {
  items.value = (await adminApi.products({ keyword: keyword.value })).items
}

function resetForm() {
  Object.assign(form, {
    category_id: categories.value[0]?.id || 1,
    name: '',
    subtitle: '',
    main_image: '',
    price: '1.00',
    stock: 1,
    description: '',
    status: 'on_sale',
  })
}

function openCreate() {
  editingId.value = undefined
  resetForm()
  dialog.value = true
}

function openEdit(row: Product) {
  editingId.value = row.id
  Object.assign(form, row)
  dialog.value = true
}

async function uploadImage(uploadFile: UploadFile) {
  const rawFile = uploadFile.raw
  if (!rawFile) return
  uploading.value = true
  try {
    const result = await adminApi.uploadProductImage(rawFile)
    form.main_image = result.url
    ElMessage.success('图片上传成功')
  } finally {
    uploading.value = false
  }
}

function clearImage() {
  form.main_image = ''
}

async function save() {
  if (editingId.value) {
    await adminApi.updateProduct(editingId.value, form)
  } else {
    await adminApi.createProduct(form)
  }
  dialog.value = false
  await load()
}

async function toggle(row: Product) {
  await adminApi.updateProductStatus(row.id, row.status === 'on_sale' ? 'off_sale' : 'on_sale')
  await load()
}

async function remove(row: Product) {
  await ElMessageBox.confirm(
    `确认永久删除“${row.name}”吗？如果商品已有订单、购物车、行为或统计记录，系统会拒绝删除，请改用下架。`,
    '删除商品',
    { type: 'warning', confirmButtonText: '确认删除', cancelButtonText: '取消' },
  )
  await adminApi.deleteProduct(row.id)
  ElMessage.success('商品已删除')
  await load()
}

onMounted(async () => {
  categories.value = await adminApi.categories()
  await load()
})
</script>

<style scoped>
.thumb {
  display: grid;
  width: 56px;
  height: 42px;
  place-items: center;
  overflow: hidden;
  border-radius: 6px;
  color: #64748b;
  background: #e2e8f0;
  font-weight: 700;
}

.thumb img,
.preview img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-manager {
  display: flex;
  gap: 16px;
  align-items: center;
}

.preview {
  display: grid;
  width: 180px;
  aspect-ratio: 4 / 3;
  place-items: center;
  overflow: hidden;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  color: #909399;
  background: #f5f7fa;
}

.image-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}
</style>

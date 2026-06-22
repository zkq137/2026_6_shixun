<template>
  <div class="admin-page">
    <div class="toolbar"><el-button type="primary" @click="openCreate">新增分类</el-button></div>
    <el-table :data="items">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="sort_order" label="排序" width="100" />
      <el-table-column prop="status" label="状态" width="120" />
      <el-table-column label="操作" width="220"><template #default="{ row }"><el-button size="small" @click="openEdit(row)">编辑</el-button><el-button size="small" @click="toggle(row)">{{ row.status === 'enabled' ? '禁用' : '启用' }}</el-button></template></el-table-column>
    </el-table>
    <el-dialog v-model="dialog" title="分类">
      <el-form label-position="top">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.sort_order" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialog=false">取消</el-button><el-button type="primary" @click="save">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { adminApi } from '@/api'
import type { Category } from '@/types'
const items = ref<Category[]>([])
const dialog = ref(false)
const editingId = ref<number>()
const form = reactive({ name: '', sort_order: 0, parent_id: 0 })
async function load() { items.value = await adminApi.categories() }
function openCreate() { editingId.value = undefined; Object.assign(form, { name: '', sort_order: 0, parent_id: 0 }); dialog.value = true }
function openEdit(row: Category) { editingId.value = row.id; Object.assign(form, row); dialog.value = true }
async function save() { editingId.value ? await adminApi.updateCategory(editingId.value, form) : await adminApi.createCategory(form); dialog.value = false; await load() }
async function toggle(row: Category) { await adminApi.updateCategoryStatus(row.id, row.status === 'enabled' ? 'disabled' : 'enabled'); await load() }
onMounted(load)
</script>


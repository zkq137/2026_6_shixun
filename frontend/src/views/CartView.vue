<template>
  <div class="page">
    <div class="section-title"><h2>购物车</h2><el-button type="primary" :disabled="!cart.items.length" @click="$router.push('/checkout')">去结算</el-button></div>
    <el-table :data="cart.items">
      <el-table-column prop="product_name" label="商品" />
      <el-table-column prop="price" label="单价" width="120" />
      <el-table-column label="数量" width="180">
        <template #default="{ row }"><el-input-number v-model="row.quantity" :min="1" :max="row.stock" @change="update(row)" /></template>
      </el-table-column>
      <el-table-column prop="subtotal" label="小计" width="120" />
      <el-table-column label="操作" width="100"><template #default="{ row }"><el-button text type="danger" @click="remove(row.id)">删除</el-button></template></el-table-column>
    </el-table>
    <h3>总计：¥{{ cart.total_amount }}</h3>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive } from 'vue'
import { mallApi } from '@/api'
import type { Cart, CartItem } from '@/types'

const cart = reactive<Cart>({ items: [], total_amount: '0.00' })

async function load() {
  Object.assign(cart, await mallApi.cart())
}
async function update(row: CartItem) {
  Object.assign(cart, await mallApi.updateCart(row.id, { quantity: row.quantity, selected: row.selected }))
}
async function remove(id: number) {
  Object.assign(cart, await mallApi.deleteCart(id))
}
onMounted(load)
</script>


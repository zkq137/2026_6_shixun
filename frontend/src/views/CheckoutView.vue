<template>
  <div class="page" style="max-width: 720px">
    <el-card>
      <h2>确认订单</h2>
      <el-form label-position="top">
        <el-form-item label="收货人"><el-input v-model="form.receiver_name" /></el-form-item>
        <el-form-item label="手机号"><el-input v-model="form.receiver_phone" /></el-form-item>
        <el-form-item label="地址"><el-input v-model="form.receiver_address" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="form.remark" /></el-form-item>
        <el-button type="primary" @click="submit">提交订单</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { mallApi } from '@/api'
import type { Cart } from '@/types'

const router = useRouter()
const cart = ref<Cart>({ items: [], total_amount: '0.00' })
const form = reactive({ receiver_name: '张三', receiver_phone: '13800000000', receiver_address: '北京市朝阳区', remark: '' })

async function submit() {
  const ids = cart.value.items.map((item) => item.id)
  if (!ids.length) return ElMessage.warning('购物车为空')
  await mallApi.createOrder({ cart_item_ids: ids, ...form })
  ElMessage.success('订单已创建')
  router.push('/orders')
}
onMounted(async () => { cart.value = await mallApi.cart() })
</script>


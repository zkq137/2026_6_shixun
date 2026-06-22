<template>
  <div class="admin-page">
    <el-row :gutter="16">
      <el-col :span="12"><el-card><div class="section-title"><h2>运营 Agent</h2><el-tag>operation</el-tag></div><ChatPanel admin agent-type="operation" placeholder="最近7天哪些商品销量最好？" /></el-card></el-col>
      <el-col :span="12"><el-card><div class="section-title"><h2>库存 Agent</h2><el-tag>inventory</el-tag></div><ChatPanel admin agent-type="inventory" placeholder="帮我看看库存风险" /></el-card></el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import ChatPanel from '@/components/ChatPanel.vue'
</script>


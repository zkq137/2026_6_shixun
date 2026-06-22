<template>
  <div class="page" style="max-width: 860px">
    <el-card>
      <div class="section-title"><h2>AI 客服</h2><el-tag>customer</el-tag></div>
      <ChatPanel agent-type="customer" placeholder="怎么退货？我的订单在哪里看？" />
    </el-card>
    <el-card style="margin-top: 16px">
      <div class="section-title"><h2>推荐 Agent</h2><el-tag>recommendation</el-tag></div>
      <ChatPanel agent-type="recommendation" placeholder="给我推荐一些商品" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import ChatPanel from '@/components/ChatPanel.vue'
</script>


<template>
  <div>
    <div class="chat-box">
      <div v-for="(item, index) in messages" :key="index" class="message" :class="item.role">
        <div>{{ item.content }}</div>
        <el-tag v-for="tool in item.tools || []" :key="tool" size="small" style="margin-top: 8px; margin-right: 6px">
          {{ tool }}
        </el-tag>
      </div>
    </div>
    <div class="toolbar" style="margin-top: 16px">
      <el-input v-model="text" type="textarea" :rows="3" placeholder="输入问题" />
      <el-button type="primary" :loading="loading" @click="send">发送</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { adminApi, mallApi } from '@/api'

const props = defineProps<{ agentType: string; admin?: boolean; placeholder?: string }>()

const text = ref(props.placeholder || '')
const loading = ref(false)
const messages = ref<Array<{ role: string; content: string; tools?: string[] }>>([])

async function send() {
  if (!text.value.trim()) return
  const current = text.value
  messages.value.push({ role: 'user', content: current })
  text.value = ''
  loading.value = true
  try {
    const data = props.admin
      ? await adminApi.aiChat({ agent_type: props.agentType, message: current })
      : await mallApi.aiChat({ agent_type: props.agentType, message: current })
    messages.value.push({
      role: 'assistant',
      content: data.answer,
      tools: data.tool_calls.map((item) => `${item.tool_name}:${item.status}`),
    })
  } catch {
    ElMessage.error('AI 调用失败，请检查后端 LLM 配置')
  } finally {
    loading.value = false
  }
}
</script>


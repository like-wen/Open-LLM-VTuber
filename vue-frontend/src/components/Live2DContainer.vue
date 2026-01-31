<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useWsClient } from '@/stores/wsClient'
import Live2DRenderer from './Live2DRenderer.vue'

const modelInfo = ref(null)
const wsClient = useWsClient()

// 从WebSocket接收Live2D相关的消息
wsClient.onMessage('set-model-and-conf', (data) => {
  console.log('Received model info:', data)
  modelInfo.value = data.model_info
})

wsClient.onMessage('live2d-update-expression', (data) => {
  console.log('Updating Live2D expression:', data)
  // 这里可以调用Live2DRenderer的方法来更新表情
})

wsClient.onMessage('live2d-play-motion', (data) => {
  console.log('Playing Live2D motion:', data)
  // 这里可以调用Live2DRenderer的方法来播放动作
})

onMounted(() => {
  // 请求初始化配置
  wsClient.sendMessage({ type: 'request-init-config' })
})

onUnmounted(() => {
  console.log('Cleaning up Live2D container')
})
</script>

<template>
  <div class="live2d-container">
    <h2>Live2D Character</h2>
    <div class="live2d-wrapper" v-if="modelInfo">
      <Live2DRenderer 
        :model-info="modelInfo"
        @model-loaded="(model) => console.log('Model loaded in renderer')"
        @error="(error) => console.error('Live2D error:', error)"
      />
    </div>
    <div v-else class="placeholder">
      <p>Loading Live2D model...</p>
    </div>
  </div>
</template>

<style scoped>
.live2d-container {
  width: 100%;
  max-width: 500px;
  text-align: center;
}

.live2d-wrapper {
  width: 100%;
  height: 500px;
}

.placeholder {
  width: 100%;
  height: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #f8f8f8;
}
</style>
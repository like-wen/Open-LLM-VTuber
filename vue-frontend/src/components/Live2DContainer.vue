<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const canvasRef = ref(null)
const modelLoaded = ref(false)
const errorMessage = ref('')

// 模拟Live2D模型加载
const loadModel = async () => {
  try {
    // 这里会集成Live2D SDK来加载模型
    console.log('Loading Live2D model...')
    
    // 模拟加载过程
    setTimeout(() => {
      modelLoaded.value = true
      console.log('Live2D model loaded successfully')
    }, 1000)
  } catch (error) {
    errorMessage.value = `Failed to load Live2D model: ${error.message}`
    console.error('Error loading Live2D model:', error)
  }
}

onMounted(() => {
  loadModel()
})

onUnmounted(() => {
  // 清理资源
  console.log('Cleaning up Live2D resources')
})
</script>

<template>
  <div class="live2d-container">
    <h2>Live2D Character</h2>
    <div class="canvas-wrapper" v-if="!errorMessage">
      <canvas 
        ref="canvasRef" 
        class="live2d-canvas"
        :class="{ loaded: modelLoaded }"
      >
        Your browser does not support the canvas element.
      </canvas>
      <div v-if="!modelLoaded" class="loading-overlay">
        <p>Loading character...</p>
      </div>
    </div>
    <div v-else class="error-message">
      {{ errorMessage }}
    </div>
  </div>
</template>

<style scoped>
.live2d-container {
  width: 100%;
  max-width: 400px;
  text-align: center;
}

.canvas-wrapper {
  position: relative;
  width: 100%;
  height: 400px;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  background-color: #f8f8f8;
}

.live2d-canvas {
  width: 100%;
  height: 100%;
  display: block;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.live2d-canvas.loaded {
  opacity: 1;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(255, 255, 255, 0.8);
  z-index: 10;
}

.error-message {
  color: #e74c3c;
  padding: 1rem;
  text-align: center;
  background-color: #fdeded;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
}
</style>
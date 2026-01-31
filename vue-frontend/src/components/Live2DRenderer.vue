<template>
  <div class="live2d-container">
    <canvas ref="canvasRef" class="live2d-canvas" />
    <div v-if="isLoading" class="loading-overlay">
      <p>Loading Live2D model...</p>
    </div>
    <div v-if="error" class="error-message">{{ error }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'

const props = defineProps({
  modelInfo: {
    type: Object,
    default: () => ({
      url: '/live2d-models/mao_pro/runtime/mao_pro.model3.json',
      kScale: 0.5,
      initialXshift: 0,
      initialYshift: 0,
      kXOffset: 1150,
      idleMotionGroupName: 'Idle',
      emotionMap: {
        neutral: 0,
        anger: 2,
        disgust: 2,
        fear: 1,
        joy: 3,
        smirk: 3,
        sadness: 1,
        surprise: 3
      }
    })
  }
})

const emit = defineEmits(['modelLoaded', 'error'])

const canvasRef = ref(null)
const isLoading = ref(true)
const error = ref(null)

let live2dModel = null
let app = null

// 加载Live2D模型
const loadModel = async () => {
  try {
    error.value = null
    
    // 确保DOM已更新
    await nextTick()
    
    const canvas = canvasRef.value
    if (!canvas) {
      throw new Error('Canvas element not found')
    }
    
    // 检查是否已有实例，如果有则先清理
    if (app) {
      app.destroy(true, { children: true, textures: true, baseTexture: true })
    }
    
    // 动态加载Live2D库
    await loadLive2DLibraries()
    
    // 初始化PixiJS应用
    const PIXI = window.PIXI
    
    app = new PIXI.Application({
      view: canvas,
      transparent: true,
      autoStart: true,
      backgroundColor: 0x000000,
      backgroundAlpha: 0,
      width: canvas.clientWidth,
      height: canvas.clientHeight,
      antialias: true
    })
    
    // 加载Live2D模型
    const model = await PIXI.Live2D.Model.from(props.modelInfo.url)
    
    // 设置模型缩放和位置
    const scale = props.modelInfo.kScale || 0.5
    model.scale.set(scale)
    
    // 居中放置模型
    model.x = canvas.clientWidth / 2 + (props.modelInfo.initialXshift || 0)
    model.y = canvas.clientHeight / 2 + (props.modelInfo.initialYshift || 0)
    
    // 添加模型到舞台
    app.stage.addChild(model)
    
    // 保存模型引用
    live2dModel = model
    
    // 设置模型点击事件
    setupModelInteractions(model)
    
    isLoading.value = false
    emit('modelLoaded', model)
    
    console.log('Live2D model loaded successfully')
  } catch (err) {
    console.error('Error loading Live2D model:', err)
    error.value = `Failed to load Live2D model: ${err.message}`
    emit('error', err)
  }
}

// 动态加载Live2D库
const loadLive2DLibraries = async () => {
  // 检查是否已经加载了库
  if (window.PIXI && window.PIXI.Live2D) {
    return
  }
  
  // 首先加载pixi.js
  await loadScript('/libs/pixi.min.js')
  
  // 然后加载pixi-live2d库
  await loadScript('/libs/pixi-live2d.min.js')
  
  console.log('Live2D libraries loaded successfully')
}

// 加载外部脚本
const loadScript = (src) => {
  return new Promise((resolve, reject) => {
    // 检查是否已存在相同src的脚本
    const existingScript = document.querySelector(`script[src="${src}"]`)
    if (existingScript) {
      resolve()
      return
    }
    
    const script = document.createElement('script')
    script.src = src
    script.async = false // 保持顺序加载
    script.onload = resolve
    script.onerror = reject
    document.head.appendChild(script)
  })
}

// 设置模型交互
const setupModelInteractions = (model) => {
  // 如果库支持点击事件
  if (model.on) {
    model.on('hit', (hitAreas) => {
      console.log('Model hit areas:', hitAreas)
      
      // 根据击中区域播放不同动作
      if (hitAreas.includes('HitAreaHead') || hitAreas.includes('Head')) {
        playRandomMotion(model, 'TapHead')
      } else if (hitAreas.includes('HitAreaBody') || hitAreas.includes('Body')) {
        playRandomMotion(model, 'TapBody')
      }
    })
  }
}

// 播放随机动作
const playRandomMotion = (model, groupName) => {
  if (model.motion) {
    model.motion(groupName)
  }
}

// 更新模型表情
const updateExpression = (expressionKey) => {
  if (live2dModel && props.modelInfo.emotionMap && props.modelInfo.emotionMap[expressionKey]) {
    const expressionIndex = props.modelInfo.emotionMap[expressionKey]
    if (live2dModel.internalModel && live2dModel.internalModel.coreModel) {
      // 尝试应用表情
      if (live2dModel.expressions && live2dModel.expressions[expressionIndex]) {
        live2dModel.expression(live2dModel.expressions[expressionIndex])
      }
    }
  }
}

// 播放动作
const playMotion = (motionName) => {
  if (live2dModel && live2dModel.motion) {
    live2dModel.motion(motionName)
  }
}

// 处理窗口大小变化
const handleResize = () => {
  if (app && canvasRef.value) {
    app.renderer.resize(canvasRef.value.clientWidth, canvasRef.value.clientHeight)
    
    // 重新定位模型
    if (live2dModel) {
      live2dModel.x = canvasRef.value.clientWidth / 2
      live2dModel.y = canvasRef.value.clientHeight / 2
    }
  }
}

// 监听props变化，重新加载模型
watch(() => props.modelInfo, () => {
  loadModel()
}, { deep: true })

onMounted(async () => {
  await loadModel()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  // 清理资源
  if (app) {
    app.destroy(true, { children: true, textures: true, baseTexture: true })
  }
  if (live2dModel) {
    if (live2dModel.destroy) {
      live2dModel.destroy()
    }
  }
  window.removeEventListener('resize', handleResize)
  
  console.log('Live2D resources cleaned up')
})

// 暴露方法给父组件
defineExpose({
  updateExpression,
  playMotion
})
</script>

<style scoped>
.live2d-container {
  position: relative;
  width: 100%;
  height: 500px;
  overflow: hidden;
}

.live2d-canvas {
  width: 100%;
  height: 100%;
  display: block;
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
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  font-size: 18px;
  z-index: 10;
}

.error-message {
  position: absolute;
  top: 10px;
  left: 10px;
  background-color: rgba(255, 0, 0, 0.7);
  color: white;
  padding: 10px;
  border-radius: 4px;
  z-index: 20;
}
</style>
</template>
<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAudioStore } from '@/stores/audio'

const audioStore = useAudioStore()
const isRecording = ref(false)
const isPlaying = ref(false)
const volume = ref(80)
const mediaRecorder = ref(null)
const audioChunks = ref([])

// 请求麦克风权限并开始录音
const startRecording = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder.value = new MediaRecorder(stream)
    
    mediaRecorder.value.ondataavailable = event => {
      audioChunks.value.push(event.data)
    }
    
    mediaRecorder.value.onstop = () => {
      const audioBlob = new Blob(audioChunks.value, { type: 'audio/wav' })
      const audioUrl = URL.createObjectURL(audioBlob)
      
      // 发送到后端处理
      audioStore.sendAudioData(audioUrl)
      
      audioChunks.value = []
      stream.getTracks().forEach(track => track.stop())
    }
    
    mediaRecorder.value.start()
    isRecording.value = true
    console.log('Started recording')
  } catch (error) {
    console.error('Error accessing microphone:', error)
    alert('Could not access microphone. Please check permissions.')
  }
}

// 停止录音
const stopRecording = () => {
  if (mediaRecorder.value && isRecording.value) {
    mediaRecorder.value.stop()
    isRecording.value = false
    console.log('Stopped recording')
  }
}

// 播放音频
const playAudio = (audioUrl) => {
  const audio = new Audio(audioUrl)
  audio.play()
    .then(() => {
      isPlaying.value = true
      audio.onended = () => {
        isPlaying.value = false
      }
    })
    .catch(error => {
      console.error('Error playing audio:', error)
    })
}

// 切换录音状态
const toggleRecording = () => {
  if (isRecording.value) {
    stopRecording()
  } else {
    startRecording()
  }
}

onUnmounted(() => {
  if (mediaRecorder.value && isRecording.value) {
    mediaRecorder.value.stop()
  }
})
</script>

<template>
  <div class="audio-controls">
    <h3>Audio Controls</h3>
    
    <div class="recording-controls">
      <button 
        class="record-btn" 
        :class="{ active: isRecording }"
        @click="toggleRecording"
        :disabled="audioStore.isProcessing"
      >
        <span class="btn-text">
          {{ isRecording ? 'Stop Recording' : 'Start Recording' }}
        </span>
        <span class="recording-indicator" v-if="isRecording"></span>
      </button>
      
      <div v-if="audioStore.isProcessing" class="processing-indicator">
        Processing audio...
      </div>
    </div>
    
    <div class="volume-control">
      <label for="volume-slider">Volume:</label>
      <input 
        type="range" 
        id="volume-slider"
        v-model="volume"
        min="0" 
        max="100" 
        step="1"
      >
      <span>{{ volume }}%</span>
    </div>
    
    <div class="recent-audio" v-if="audioStore.recentAudio.length > 0">
      <h4>Recent Audio</h4>
      <div class="audio-list">
        <div 
          v-for="(audio, index) in audioStore.recentAudio" 
          :key="index"
          class="audio-item"
        >
          <button @click="playAudio(audio.url)" :disabled="isPlaying">
            Play
          </button>
          <span class="audio-name">{{ audio.name || `Audio ${index + 1}` }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.audio-controls {
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #f9f9f9;
}

.recording-controls {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.record-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: bold;
  color: white;
  background-color: #e74c3c;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.record-btn:hover:not(:disabled) {
  background-color: #c0392b;
}

.record-btn:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
}

.record-btn.active {
  background-color: #2ecc71;
}

.btn-text {
  margin-right: 0.5rem;
}

.recording-indicator {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: white;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(0.8);
    opacity: 0.7;
  }
  50% {
    transform: scale(1.2);
    opacity: 1;
  }
  100% {
    transform: scale(0.8);
    opacity: 0.7;
  }
}

.processing-indicator {
  padding: 0.5rem;
  background-color: #f1c40f;
  color: #7d6608;
  border-radius: 4px;
  text-align: center;
  font-size: 0.9rem;
}

.volume-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.volume-control label {
  font-weight: bold;
  min-width: 70px;
}

#volume-slider {
  flex: 1;
}

.recent-audio {
  margin-top: 1rem;
}

.audio-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.audio-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background-color: white;
  border: 1px solid #eee;
  border-radius: 4px;
}

.audio-item button {
  padding: 0.25rem 0.5rem;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 3px;
  cursor: pointer;
}

.audio-item button:hover:not(:disabled) {
  background-color: #2980b9;
}

.audio-item button:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
}

.audio-name {
  flex: 1;
  font-size: 0.9rem;
  color: #555;
}
</style>
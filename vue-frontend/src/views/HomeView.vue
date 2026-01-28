<script setup>
import Live2DContainer from '@/components/Live2DContainer.vue'
import AudioControls from '@/components/AudioControls.vue'
import ChatMessages from '@/components/ChatMessages.vue'
</script>

<template>
  <div class="home">
    <div class="main-container">
      <div class="live2d-section">
        <Live2DContainer />
      </div>
      
      <div class="chat-section">
        <ChatMessages />
        <AudioControls />
      </div>
    </div>
  </div>
</template>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 1rem;
}

.main-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 1200px;
  gap: 1rem;
}

@media (min-width: 768px) {
  .main-container {
    flex-direction: row;
  }
  
  .live2d-section {
    flex: 1;
    min-width: 300px;
  }
  
  .chat-section {
    flex: 1;
    min-width: 300px;
  }
}

.live2d-section {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.chat-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
</style>
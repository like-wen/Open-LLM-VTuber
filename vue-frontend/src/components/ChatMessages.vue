<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useChatStore } from '@/stores/chat'

const chatStore = useChatStore()
const messagesEndRef = ref(null)

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  if (messagesEndRef.value) {
    messagesEndRef.value.scrollIntoView({ behavior: 'smooth' })
  }
}

// 在消息更新后滚动到底部
onMounted(() => {
  scrollToBottom()
})
</script>

<template>
  <div class="chat-messages">
    <h3>Conversation</h3>
    
    <div class="messages-container">
      <div 
        v-for="(message, index) in chatStore.messages" 
        :key="index"
        :class="['message', message.role]"
      >
        <div class="message-header">
          <span class="role">{{ message.role === 'user' ? 'You' : 'AI' }}</span>
          <span class="timestamp">{{ new Date(message.timestamp).toLocaleTimeString() }}</span>
        </div>
        <div class="message-content">
          {{ message.content }}
        </div>
      </div>
      
      <div v-if="chatStore.isProcessing" class="message ai processing">
        <div class="message-header">
          <span class="role">AI</span>
          <span class="timestamp">{{ new Date().toLocaleTimeString() }}</span>
        </div>
        <div class="message-content">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
      
      <div ref="messagesEndRef" />
    </div>
  </div>
</template>

<style scoped>
.chat-messages {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 300px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: white;
  overflow: hidden;
}

.messages-container {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message {
  max-width: 80%;
  padding: 0.75rem;
  border-radius: 8px;
  position: relative;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.message.user {
  align-self: flex-end;
  background-color: #3498db;
  color: white;
  border-bottom-right-radius: 0;
}

.message.ai {
  align-self: flex-start;
  background-color: #f1f1f1;
  color: #333;
  border-bottom-left-radius: 0;
}

.message.processing {
  background-color: #e8f4fc;
}

.message-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.8rem;
  font-weight: bold;
}

.message.user .message-header {
  color: rgba(255, 255, 255, 0.8);
}

.message.ai .message-header {
  color: #777;
}

.role {
  font-weight: bold;
}

.timestamp {
  color: inherit;
  opacity: 0.7;
}

.message-content {
  word-wrap: break-word;
  line-height: 1.5;
}

.typing-indicator {
  display: flex;
  gap: 0.25rem;
  align-items: center;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background-color: #777;
  border-radius: 50%;
  display: inline-block;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
  animation-delay: 0s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-5px);
  }
}
</style>
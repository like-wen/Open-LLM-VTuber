import { defineStore } from 'pinia'

export const useChatStore = defineStore('chat', {
  state: () => ({
    messages: [],
    isProcessing: false,
  }),

  actions: {
    addMessage(role, content) {
      this.messages.push({
        role,
        content,
        timestamp: Date.now()
      })
    },

    startProcessing() {
      this.isProcessing = true
    },

    stopProcessing() {
      this.isProcessing = false
    },

    clearMessages() {
      this.messages = []
    },

    // 模拟发送消息到后端
    async sendMessage(content) {
      // 添加用户消息
      this.addMessage('user', content)
      
      // 模拟处理中状态
      this.startProcessing()
      
      try {
        // 模拟API调用延迟
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // 添加AI回复
        this.addMessage('ai', 'This is a simulated AI response to: ' + content)
      } catch (error) {
        console.error('Error sending message:', error)
        this.addMessage('ai', 'Sorry, there was an error processing your request.')
      } finally {
        this.stopProcessing()
      }
    }
  }
})
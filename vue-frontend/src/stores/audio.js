import { defineStore } from 'pinia'

export const useAudioStore = defineStore('audio', {
  state: () => ({
    recentAudio: [],
    isProcessing: false,
    currentVolume: 80
  }),

  actions: {
    addAudio(audioData) {
      this.recentAudio.unshift({
        id: Date.now(),
        name: `Audio ${this.recentAudio.length + 1}`,
        url: audioData.url,
        timestamp: Date.now()
      })
      
      // 只保留最近的10条音频
      if (this.recentAudio.length > 10) {
        this.recentAudio.pop()
      }
    },

    setIsProcessing(status) {
      this.isProcessing = status
    },

    setVolume(volume) {
      this.currentVolume = volume
    },

    // 模拟发送音频数据到后端
    async sendAudioData(audioUrl) {
      this.setIsProcessing(true)
      
      try {
        // 这里会通过WebSocket或HTTP API发送音频数据到后端
        console.log('Sending audio to backend:', audioUrl)
        
        // 模拟API调用延迟
        await new Promise(resolve => setTimeout(resolve, 1500))
        
        // 添加到最近音频列表
        this.addAudio({ url: audioUrl })
        
        console.log('Audio processed successfully')
      } catch (error) {
        console.error('Error processing audio:', error)
      } finally {
        this.setIsProcessing(false)
      }
    }
  }
})
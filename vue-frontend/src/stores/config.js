import { defineStore } from 'pinia'

export const useConfigStore = defineStore('config', {
  state: () => ({
    config: {
      llm: {
        provider: 'ollama',
        model: 'qwen2.5:latest',
        baseUrl: 'http://localhost:11434/v1',
        apiKey: 'ollama'
      },
      asr: {
        provider: 'sherpa_onnx',
        model: 'sense_voice'
      },
      tts: {
        provider: 'edge_tts',
        voice: 'zh-CN-XiaoxiaoNeural'
      }
    }
  }),

  actions: {
    updateConfig(newConfig) {
      this.config = { ...this.config, ...newConfig }
    },

    updateLLMConfig(llmConfig) {
      this.config.llm = { ...this.config.llm, ...llmConfig }
    },

    updateASRConfig(asrConfig) {
      this.config.asr = { ...this.config.asr, ...asrConfig }
    },

    updateTTSConfig(ttsConfig) {
      this.config.tts = { ...this.config.tts, ...ttsConfig }
    }
  }
})
<script setup>
import { ref } from 'vue'
import { useConfigStore } from '@/stores/config'

const configStore = useConfigStore()
const activeTab = ref('llm')

// 模拟配置保存
const saveConfig = () => {
  console.log('Saving configuration:', configStore.config)
  // 这里会调用API保存配置到后端
  alert('Configuration saved successfully!')
}
</script>

<template>
  <div class="config-panel">
    <h2>System Configuration</h2>
    
    <div class="tabs">
      <button 
        v-for="tab in ['llm', 'asr', 'tts']" 
        :key="tab"
        :class="['tab', { active: activeTab === tab }]"
        @click="activeTab = tab"
      >
        {{ tab.toUpperCase() }}
      </button>
    </div>
    
    <div class="config-form">
      <!-- LLM 配置 -->
      <div v-show="activeTab === 'llm'" class="config-section">
        <h3>LLM Settings</h3>
        
        <div class="form-group">
          <label for="llm-provider">Provider:</label>
          <select id="llm-provider" v-model="configStore.config.llm.provider">
            <option value="openai">OpenAI</option>
            <option value="ollama">Ollama</option>
            <option value="claude">Claude</option>
            <option value="gemini">Gemini</option>
            <option value="zhipu">Zhipu</option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="llm-model">Model:</label>
          <input 
            type="text" 
            id="llm-model" 
            v-model="configStore.config.llm.model"
            placeholder="Enter model name"
          >
        </div>
        
        <div class="form-group">
          <label for="llm-base-url">Base URL:</label>
          <input 
            type="url" 
            id="llm-base-url" 
            v-model="configStore.config.llm.baseUrl"
            placeholder="Enter API base URL"
          >
        </div>
        
        <div class="form-group">
          <label for="llm-api-key">API Key:</label>
          <input 
            type="password" 
            id="llm-api-key" 
            v-model="configStore.config.llm.apiKey"
            placeholder="Enter API key"
          >
        </div>
      </div>
      
      <!-- ASR 配置 -->
      <div v-show="activeTab === 'asr'" class="config-section">
        <h3>ASR Settings</h3>
        
        <div class="form-group">
          <label for="asr-provider">Provider:</label>
          <select id="asr-provider" v-model="configStore.config.asr.provider">
            <option value="sherpa_onnx">Sherpa ONNX</option>
            <option value="sense_voice">SenseVoice</option>
            <option value="whisper">Whisper</option>
            <option value="faster_whisper">Faster Whisper</option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="asr-model">Model:</label>
          <input 
            type="text" 
            id="asr-model" 
            v-model="configStore.config.asr.model"
            placeholder="Enter model path or name"
          >
        </div>
      </div>
      
      <!-- TTS 配置 -->
      <div v-show="activeTab === 'tts'" class="config-section">
        <h3>TTS Settings</h3>
        
        <div class="form-group">
          <label for="tts-provider">Provider:</label>
          <select id="tts-provider" v-model="configStore.config.tts.provider">
            <option value="edge_tts">Edge TTS</option>
            <option value="piper_tts">Piper TTS</option>
            <option value="elevenlabs">ElevenLabs</option>
            <option value="openai_tts">OpenAI TTS</option>
            <option value="melo_tts">Melo TTS</option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="tts-voice">Voice:</label>
          <input 
            type="text" 
            id="tts-voice" 
            v-model="configStore.config.tts.voice"
            placeholder="Enter voice name"
          >
        </div>
      </div>
    </div>
    
    <div class="actions">
      <button @click="saveConfig" class="save-btn">
        Save Configuration
      </button>
    </div>
  </div>
</template>

<style scoped>
.config-panel {
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #f9f9f9;
}

.tabs {
  display: flex;
  margin-bottom: 1rem;
  border-bottom: 1px solid #ddd;
}

.tab {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  border-bottom: none;
  background-color: #f1f1f1;
  cursor: pointer;
  border-radius: 4px 4px 0 0;
  margin-right: 0.2rem;
}

.tab.active {
  background-color: white;
  border-bottom: 1px solid white;
  margin-bottom: -1px;
  font-weight: bold;
}

.config-form {
  margin-bottom: 1rem;
}

.config-section {
  padding: 1rem 0;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-group input {
  width: 100%;
}

.actions {
  display: flex;
  justify-content: flex-end;
}

.save-btn {
  padding: 0.75rem 1.5rem;
  background-color: #2ecc71;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
}

.save-btn:hover {
  background-color: #27ae60;
}
</style>
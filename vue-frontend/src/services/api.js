// API 服务
class ApiService {
  constructor(baseURL = '/api') {
    this.baseURL = baseURL
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    }

    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error('API request failed:', error)
      throw error
    }
  }

  async get(endpoint) {
    return this.request(endpoint, { method: 'GET' })
  }

  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  async put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data)
    })
  }

  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' })
  }

  // 获取系统健康状态
  async healthCheck() {
    return this.get('/health')
  }

  // 获取配置
  async getConfigs() {
    return this.get('/configs')
  }

  // 更新配置
  async updateConfig(config) {
    return this.post('/configs', config)
  }

  // 处理音频
  async processAudio(audioData) {
    return this.post('/audio/process', audioData)
  }
}

export default ApiService
# Open-LLM-VTuber 迁移到 Go 后端方案

## 项目概述
将现有的 Python/FastAPI 后端迁移到 Go，以提升性能和并发处理能力。

## 核心功能模块迁移计划

### 1. WebSocket 服务器
- **源代码**: `src/open_llm_vtuber/server.py`, `websocket_handler.py`
- **目标**: 使用 Go 实现 WebSocket 服务器
- **技术栈**: gorilla/websocket + gin-gonic/gin
- **任务**:
  - [ ] 实现 WebSocket 连接管理
  - [ ] 实现消息路由系统
  - [ ] 实现客户端连接池管理
  - [ ] 实现心跳检测机制
  - [ ] 实现错误处理和重连机制

### 2. LLM 服务集成
- **源代码**: `src/open_llm_vtuber/agent/` 目录下的所有文件
- **目标**: 实现多种 LLM 模型的调用接口
- **技术栈**: Go HTTP 客户端
- **任务**:
  - [ ] 实现 OpenAI 兼容接口调用
  - [ ] 实现 Ollama 接口调用
  - [ ] 实现 llama.cpp 接口调用
  - [ ] 实现 Claude 接口调用
  - [ ] 实现 Gemini 接口调用
  - [ ] 实现模型工厂模式
  - [ ] 实现流式响应处理

### 3. ASR (自动语音识别) 服务
- **源代码**: `src/open_llm_vtuber/asr/` 目录下的所有文件
- **目标**: 实现多种 ASR 模型的调用接口
- **技术栈**: Go HTTP 客户端或 ONNX 运行时
- **任务**:
  - [ ] 实现 Sherpa ONNX ASR 接口
  - [ ] 实现 SenseVoice ASR 接口
  - [ ] 实现 Whisper ASR 接口
  - [ ] 实现音频预处理功能
  - [ ] 实现模型配置管理

### 4. TTS (文本转语音) 服务
- **源代码**: `src/open_llm_vtuber/tts/` 目录下的所有文件
- **目标**: 实现多种 TTS 模型的调用接口
- **技术栈**: Go HTTP 客户端或 ONNX 运行时
- **任务**:
  - [ ] 实现 Edge TTS 接口
  - [ ] 实现 Piper TTS 接口
  - [ ] 实现 ElevenLabs TTS 接口
  - [ ] 实现 OpenAI TTS 接口
  - [ ] 实现音频后处理功能
  - [ ] 实现音频流传输

### 5. VAD (语音活动检测) 服务
- **源代码**: `src/open_llm_vtuber/vad/silero.py`
- **目标**: 实现语音活动检测功能
- **技术栈**: Go ONNX 运行时或 HTTP 接口
- **任务**:
  - [ ] 实现 Silero VAD 接口
  - [ ] 实现音频流实时检测
  - [ ] 实现语音片段分割

### 6. 配置管理系统
- **源代码**: `src/open_llm_vtuber/config_manager/` 目录
- **目标**: 实现配置管理功能
- **技术栈**: Go + YAML/Viper
- **任务**:
  - [ ] 实现配置文件解析
  - [ ] 实现配置验证
  - [ ] 实现配置热更新
  - [ ] 实现配置API接口

### 7. 会话和历史管理
- **源代码**: `src/open_llm_vtuber/conversations/`, `chat_history_manager.py`
- **目标**: 实现对话和历史记录管理
- **技术栈**: Go + 内存存储或数据库
- **任务**:
  - [ ] 实现会话管理器
  - [ ] 实现历史记录存储
  - [ ] 实现会话持久化
  - [ ] 实现历史记录查询API

### 8. Live2D 集成
- **源代码**: `src/open_llm_vtuber/live2d_model.py`
- **目标**: 实现 Live2D 相关功能接口
- **技术栈**: Go
- **任务**:
  - [ ] 实现 Live2D 模型配置管理
  - [ ] 实现表情和动作控制接口
  - [ ] 实现与前端的数据交互

## 技术架构

### Go 项目结构
```
go-open-llm-vtuber/
├── cmd/
│   └── server/
│       └── main.go
├── internal/
│   ├── config/
│   │   └── config.go
│   ├── server/
│   │   ├── websocket.go
│   │   └── routes.go
│   ├── services/
│   │   ├── llm/
│   │   ├── asr/
│   │   ├── tts/
│   │   ├── vad/
│   │   └── live2d/
│   ├── handlers/
│   │   ├── websocket_handler.go
│   │   └── audio_handler.go
│   └── models/
│       ├── message.go
│       ├── config.go
│       └── audio.go
├── pkg/
│   ├── utils/
│   └── middleware/
└── go.mod
```

### Go 依赖包
- github.com/gin-gonic/gin - Web 框架
- github.com/gorilla/websocket - WebSocket 支持
- golang.org/x/exp/slices - 切片操作
- github.com/spf13/viper - 配置管理
- gorgonia.org/onnx - ONNX 运行时 (可选)
- google.golang.org/protobuf - 协议缓冲区

## 迁移步骤

### 第一阶段：基础设施搭建
1. 创建 Go 项目结构
2. 设置基本的 HTTP 服务器
3. 实现配置管理模块
4. 实现日志系统

### 第二阶段：核心服务迁移
1. 实现 WebSocket 服务器
2. 实现 LLM 服务接口
3. 实现 ASR 服务接口
4. 实现 TTS 服务接口

### 第三阶段：高级功能迁移
1. 实现 VAD 服务
2. 实现会话管理
3. 实现历史记录管理
4. 实现 Live2D 集成功能

### 第四阶段：测试和优化
1. 单元测试
2. 集成测试
3. 性能测试
4. 优化和调整

## 预期收益
- 更高的并发处理能力
- 更低的内存占用
- 更快的响应时间
- 更简单的部署方式
- 更好的生产环境稳定性
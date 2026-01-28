# Go Backend for Open-LLM-VTuber

这是一个将 Open-LLM-VTuber 项目从 Python/FastAPI 迁移到 Go 的后端实现。

## 项目结构

```
go-backend/
├── cmd/
│   └── server/
│       └── main.go          # 主程序入口
├── internal/
│   ├── config/              # 配置管理
│   │   └── config.go
│   ├── server/              # 服务器主逻辑
│   │   └── server.go
│   ├── handlers/            # 请求处理器
│   │   ├── websocket_handler.go
│   │   └── audio_handler.go
│   ├── models/              # 数据模型
│   │   └── models.go
│   └── services/            # 业务服务 (待实现)
├── pkg/                     # 公共包
│   ├── utils/
│   └── middleware/
└── go.mod                   # 依赖管理
```

## 功能实现

目前已完成的核心功能：

1. **WebSocket 服务器**: 实现了 WebSocket 连接管理、消息路由和客户端管理
2. **配置管理**: 实现了基于 Viper 的配置加载和管理
3. **音频处理**: 实现了音频数据的接收、ASR/LLM/TTS 处理链路
4. **API 路由**: 实现了 RESTful API 和 WebSocket 路由

## 依赖包

- `github.com/gin-gonic/gin`: Web 框架
- `github.com/gorilla/websocket`: WebSocket 支持
- `github.com/spf13/viper`: 配置管理
- `go.uber.org/zap`: 日志系统

## 运行方法

```bash
cd go-backend
go mod tidy
go run cmd/server/main.go
```

## 待完成任务

根据迁移计划，接下来需要完成:

1. 实现具体的 LLM 服务调用 (OpenAI, Ollama, Claude 等)
2. 实现具体的 ASR 服务调用 (Sherpa ONNX, SenseVoice 等)
3. 实现具体的 TTS 服务调用 (Edge TTS, Piper TTS 等)
4. 实现 VAD (语音活动检测) 服务
5. 实现完整的会话和历史记录管理
6. 实现 Live2D 相关功能接口
7. 添加完整的错误处理和日志记录
8. 添加单元测试和集成测试

## 设计特点

1. **模块化设计**: 代码按功能模块分离，便于维护和扩展
2. **并发安全**: 使用互斥锁保护共享资源
3. **可配置**: 支持通过配置文件或环境变量配置各项参数
4. **实时通信**: 基于 WebSocket 的实时双向通信
5. **高性能**: Go 语言的并发特性确保高吞吐量和低延迟
# Open-LLM-VTuber API 对比文档

## 概述

本文档比较了Python版本和Go版本的Open-LLM-VTuber API端点，帮助开发者了解迁移过程中API的变化。

## Python版本 API 端点

### WebSocket 端点
- `/client-ws` - 主要WebSocket端点，处理实时语音对话
- `/tts-ws` - TTS生成专用WebSocket端点
- `/proxy-ws` - 代理WebSocket端点（可选）

### HTTP API 端点
- `POST /asr` - 音频转文字服务
- `GET /web-tool` - Web工具页面重定向
- `GET /web_tool` - Web工具页面重定向
- `GET /live2d-models/info` - 获取Live2D模型信息

### 静态文件服务
- `/cache/` - 缓存音频文件
- `/live2d-models/` - Live2D模型文件
- `/bg/` - 背景图片
- `/avatars/` - 头像图片
- `/web-tool/` - Web工具文件
- `/` - 主前端文件

## Go版本 API 端点（计划）

### WebSocket 端点
- `GET /api/ws/client` - 主要WebSocket端点，处理实时语音对话
- `GET /api/ws/tts` - TTS生成专用WebSocket端点
- `GET /api/ws/proxy` - 代理WebSocket端点（可选）

### HTTP API 端点
- `GET /api/health` - 健康检查端点
- `POST /api/audio/process` - 音频处理端点（整合ASR功能）
- `GET /api/configs` - 获取配置
- `POST /api/configs` - 更新配置
- `GET /api/live2d-models/info` - 获取Live2D模型信息
- `GET /api/history` - 获取聊天历史
- `POST /api/history` - 创建聊天历史
- `DELETE /api/history/{id}` - 删除聊天历史

### 静态文件服务
- `/static/cache/` - 缓存音频文件
- `/static/live2d-models/` - Live2D模型文件
- `/static/bg/` - 背景图片
- `/static/avatars/` - 头像图片
- `/static/web-tool/` - Web工具文件
- `/` - 主前端文件

## API 功能对比

| 功能 | Python版本 | Go版本 | 变化说明 |
|------|------------|--------|----------|
| 实时语音对话 | `/client-ws` | `/api/ws/client` | 路径标准化 |
| TTS生成 | `/tts-ws` | `/api/ws/tts` | 路径标准化 |
| 音频转文字 | `POST /asr` | `POST /api/audio/process` | 功能整合 |
| 配置管理 | 通过WebSocket | `GET/POST /api/configs` | 独立API端点 |
| 历史记录 | 通过WebSocket | 独立CRUD端点 | 功能独立 |
| Live2D模型信息 | `GET /live2d-models/info` | `GET /api/live2d-models/info` | 路径标准化 |

## WebSocket消息格式变化

### Python版本消息格式
```json
{
  "type": "message_type",
  "action": "action_name",
  "text": "message_content",
  "audio": [audio_data_array],
  "history_uid": "history_id"
}
```

### Go版本消息格式（计划）
```json
{
  "type": "message_type",
  "payload": {
    "data": "actual_data",
    "metadata": {
      "timestamp": 1234567890,
      "sessionId": "session_id"
    }
  }
}
```

## 认证机制

### Python版本
- 基于配置文件的API密钥
- 通过环境变量传递

### Go版本（计划）
- JWT令牌认证
- OAuth2支持
- API密钥管理端点
- 会话管理

## 错误处理

### Python版本
- HTTP状态码
- JSON错误响应
- 详细的错误消息

### Go版本（计划）
- 标准化错误响应格式
- 错误代码系统
- 详细的错误描述和建议

## 性能改进

### Go版本预期改进
- 更快的WebSocket连接处理
- 更低的内存占用
- 更好的并发处理能力
- 更快的音频处理速度
- 更短的响应时间

## 向后兼容性

Go版本将提供一个兼容层，以确保现有客户端可以无缝迁移：

- 保留大部分WebSocket消息格式
- 提供API网关支持旧端点路径
- 逐步迁移支持
- 版本控制机制

## 迁移建议

1. **第一阶段**: 保持WebSocket协议不变，只迁移HTTP API
2. **第二阶段**: 逐步更新WebSocket消息格式
3. **第三阶段**: 完全迁移到新的Go API结构
4. **第四阶段**: 移除兼容层

## 开发者注意事项

- Go版本将提供完整的RESTful API
- 更好的API文档（Swagger/OpenAPI）
- 更强的类型安全
- 更好的错误处理
- 更快的开发迭代速度
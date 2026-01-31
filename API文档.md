# Open-LLM-VTuber Python API 文档

## API 端点概述

Open-LLM-VTuber 使用 FastAPI 框架，提供了以下 API 端点和服务：

## WebSocket 端点

### 1. `/client-ws` (WebSocket)
- **用途**: 客户端 WebSocket 连接端点
- **功能**: 
  - 处理实时语音对话
  - 传输音频数据
  - 接收AI回复
  - 管理聊天历史
- **消息类型**:
  - `mic-audio-data`: 发送麦克风音频数据
  - `mic-audio-end`: 表示音频输入结束
  - `text-input`: 发送文本输入
  - `ai-speak-signal`: AI主动发言信号
  - `fetch-history-list`: 获取历史记录列表
  - `fetch-and-set-history`: 获取并设置历史记录
  - `create-new-history`: 创建新历史记录
  - `delete-history`: 删除历史记录
  - `interrupt-signal`: 中断信号
  - `audio-play-start`: 音频播放开始通知
  - `request-init-config`: 请求初始化配置
  - `heartbeat`: 心跳检测
  - `add-client-to-group`: 将客户端添加到群组
  - `remove-client-from-group`: 从群组移除客户端
  - `request-group-info`: 请求群组信息

### 2. `/tts-ws` (WebSocket)
- **用途**: TTS (文本转语音) 生成端点
- **功能**: 
  - 接收文本并生成音频
  - 实时返回音频流
  - 发送进度更新
- **消息格式**:
  - 输入: `{"text": "要转换的文本"}`
  - 输出: `{"status": "partial", "audioPath": "音频路径", "text": "文本"}`
  - 完成: `{"status": "complete"}`

### 3. `/proxy-ws` (WebSocket)
- **用途**: 代理 WebSocket 连接端点
- **功能**: 
  - 代理客户端连接
  - 转发 WebSocket 消息
  - 仅在启用代理模式时可用

## HTTP API 端点

### 1. `/asr` (POST)
- **用途**: ASR (语音识别) 端点
- **功能**: 
  - 接收音频文件
  - 返回识别的文本
- **参数**: 
  - `file`: 上传的音频文件 (WAV格式)
- **返回**:
  ```json
  {
    "text": "识别的文本"
  }
  ```

### 2. `/web-tool` (GET)
- **用途**: Web 工具页面重定向
- **功能**: 
  - 重定向到 Web 工具页面
  - 返回 `/web-tool/index.html`

### 3. `/web_tool` (GET)
- **用途**: Web 工具页面重定向
- **功能**: 
  - 重定向到 Web 工具页面
  - 返回 `/web_tool/index.html`

### 4. `/live2d-models/info` (GET)
- **用途**: 获取可用 Live2D 模型信息
- **功能**: 
  - 扫描 `live2d-models` 目录
  - 返回有效的 Live2D 模型列表
- **返回**:
  ```json
  {
    "type": "live2d-models/info",
    "count": 2,
    "characters": [
      {
        "name": "model_name",
        "avatar": "avatar_path",
        "model_path": "model_path"
      }
    ]
  }
  ```

## 静态文件服务

### 1. `/cache/` (静态文件)
- **用途**: 提供缓存的音频文件访问
- **目录**: `cache/` 目录

### 2. `/live2d-models/` (静态文件)
- **用途**: 提供 Live2D 模型文件访问
- **目录**: `live2d-models/` 目录

### 3. `/bg/` (静态文件)
- **用途**: 提供背景图片访问
- **目录**: `backgrounds/` 目录

### 4. `/avatars/` (静态文件)
- **用途**: 提供头像图片访问
- **目录**: `avatars/` 目录

### 5. `/web-tool/` (静态文件)
- **用途**: 提供 Web 工具文件访问
- **目录**: `web_tool/` 目录

### 6. `/` (静态文件)
- **用途**: 提供主前端文件访问
- **目录**: `frontend/` 目录 (通配符)

## 服务器配置

### 启动命令
```bash
python run_server.py
# 或带详细日志
python run_server.py --verbose
```

### 配置文件
- 主配置文件: `conf.yaml`
- 系统配置: `system_config` 部分
- 主机和端口: 从配置文件读取

### CORS 配置
- 允许所有来源: `allow_origins=["*"]`
- 允许凭据: `allow_credentials=True`
- 允许所有方法: `allow_methods=["*"]`
- 允许所有头部: `allow_headers=["*"]`

## 环境变量
- `HF_HOME`: Hugging Face 模型缓存目录 (默认: `./models`)
- `MODELSCOPE_CACHE`: ModelScope 缓存目录 (默认: `./models`)
- `HF_ENDPOINT`: Hugging Face 镜像端点 (可选)

## 服务上下文
- `ServiceContext`: 管理所有服务实例
- 包含: ASR引擎、TTS引擎、LLM代理、VAD引擎等
- 每个WebSocket连接都有独立的服务上下文

## 代理模式
- 可通过配置启用代理模式
- 代理端点: `/proxy-ws`
- 用于转发到其他服务器

## 错误处理
- 500错误: 内部服务器错误
- 400错误: 请求格式错误
- 403错误: 文件类型不允许 (avatars目录)
- 404错误: 未找到资源

## 日志记录
- 使用 `loguru` 进行日志记录
- 控制台和文件双重输出
- 不同的日志级别 (INFO, DEBUG, ERROR等)
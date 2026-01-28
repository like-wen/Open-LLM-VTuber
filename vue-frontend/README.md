# Vue Frontend for Open-LLM-VTuber

这是一个将 Open-LLM-VTuber 项目从前端静态文件迁移到 Vue 3 的实现。

## 项目结构

```
vue-frontend/
├── public/
├── src/
│   ├── assets/              # 静态资源
│   │   ├── main.css
│   │   └── base.css
│   ├── components/          # Vue 组件
│   │   ├── Live2DContainer.vue
│   │   ├── AudioControls.vue
│   │   ├── ChatMessages.vue
│   │   └── ConfigPanel.vue
│   ├── views/               # 页面视图
│   │   ├── HomeView.vue
│   │   ├── SettingsView.vue
│   │   └── HistoryView.vue
│   ├── stores/              # Pinia 状态管理
│   │   ├── chat.js
│   │   ├── config.js
│   │   └── audio.js
│   ├── services/            # 服务层
│   │   ├── api.js
│   │   └── wsClient.js
│   ├── composables/         # 组合式函数 (待实现)
│   ├── utils/               # 工具函数 (待实现)
│   ├── router/              # 路由配置
│   │   └── index.js
│   ├── App.vue              # 主应用组件
│   └── main.js              # 主入口文件
├── package.json             # 项目配置
└── vite.config.js           # Vite 配置
```

## 功能实现

目前已完成的核心功能：

1. **Live2D 组件**: 实现了 Live2D 模型容器的基本结构
2. **音频控制**: 实现了麦克风录音和音频播放功能
3. **聊天界面**: 实现了消息显示和交互界面
4. **配置面板**: 实现了系统配置管理界面
5. **状态管理**: 使用 Pinia 管理应用状态
6. **路由管理**: 使用 Vue Router 实现页面导航
7. **API 服务**: 实现了与后端通信的 API 服务
8. **WebSocket 服务**: 实现了 WebSocket 连接管理

## 依赖包

- `vue`: 核心框架
- `vue-router`: 路由管理
- `pinia`: 状态管理
- `@vueuse/core`: 实用工具集
- `@vitejs/plugin-vue`: Vue 插件
- `vite`: 构建工具

## 运行方法

```bash
cd vue-frontend
npm install
npm run dev
```

## 待完成任务

根据迁移计划，接下来需要完成:

1. 实现真实的 Live2D 模型集成
2. 完善 WebSocket 与 Go 后端的通信
3. 实现完整的音频处理流程
4. 添加更多组件和页面
5. 实现历史记录管理功能
6. 添加响应式设计和主题切换
7. 添加单元测试
8. 优化用户体验和性能

## 设计特点

1. **组件化架构**: 采用 Vue 3 的组件化设计
2. **状态管理**: 使用 Pinia 进行全局状态管理
3. **响应式设计**: 支持不同屏幕尺寸
4. **实时通信**: 基于 WebSocket 的实时交互
5. **模块化服务**: 分离 API 和 WebSocket 服务
6. **TypeScript 准备**: 代码结构易于添加 TypeScript 支持
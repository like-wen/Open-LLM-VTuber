"""
Open-LLM-VTuber 服务器
========================
此模块包含 Open-LLM-VTuber 的 WebSocket 服务器，负责处理
WebSocket 连接，提供静态文件服务，并管理 Web 工具。
它使用 FastAPI 作为服务器框架，使用 Starlette 处理静态文件服务。
"""

import os
import shutil

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import Response
from starlette.staticfiles import StaticFiles as StarletteStaticFiles

from .routes import init_client_ws_route, init_webtool_routes, init_proxy_route
from .service_context import ServiceContext
from .config_manager.utils import Config


# 创建一个自定义的 StaticFiles 类，用于添加 CORS 头部
class CORSStaticFiles(StarletteStaticFiles):
    """
    静态文件处理器，为所有响应添加 CORS 头部。
    需要这样做是因为 Starlette 的 StaticFiles 可能会绕过标准中间件。
    """

    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)

        # 为所有响应添加 CORS 头部
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"

        if path.endswith(".js"):
            response.headers["Content-Type"] = "application/javascript"

        return response


class AvatarStaticFiles(CORSStaticFiles):
    """
    头像文件处理器，带有安全限制和 CORS 头部
    """

    async def get_response(self, path: str, scope):
        allowed_extensions = (".jpg", ".jpeg", ".png", ".gif", ".svg")
        if not any(path.lower().endswith(ext) for ext in allowed_extensions):
            return Response("禁止的文件类型", status_code=403)
        response = await super().get_response(path, scope)
        return response


class WebSocketServer:
    """
    Open-LLM-VTuber 的 API 服务器。包含客户端的 WebSocket 端点，托管 Web 工具，并提供静态文件服务。

    创建并配置 FastAPI 应用，注册所有路由
    (WebSocket、Web 工具、代理) 并使用 CORS 挂载静态资源。

    参数:
        config (Config): 包含系统设置的应用配置。
        default_context_cache (ServiceContext, 可选):
            预初始化的服务上下文，供会话的服务上下文引用。
            **如果省略，则需要调用 `initialize()` 方法加载服务上下文。**

    注意:
        - 如果省略了 default_context_cache，请调用 `await initialize()` 加载服务上下文缓存。
        - 使用 `clean_cache()` 清理并重新创建本地缓存目录。
    """

    def __init__(self, config: Config, default_context_cache: ServiceContext = None):
        self.app = FastAPI(title="Open-LLM-VTuber Server")  # 添加标题以提高清晰度
        self.config = config
        self.default_context_cache = (
            default_context_cache or ServiceContext()
        )  # 使用提供的上下文或初始化一个空的上下文等待加载
        # 它将在 initialize 方法调用期间被填充

        # 添加全局 CORS 中间件
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # 包含路由，传递上下文实例
        # 上下文将在初始化步骤中被填充
        self.app.include_router(
            init_client_ws_route(default_context_cache=self.default_context_cache),
        )
        self.app.include_router(
            init_webtool_routes(default_context_cache=self.default_context_cache),
        )

        # 如果启用了代理，则初始化并包含代理路由
        system_config = config.system_config
        if hasattr(system_config, "enable_proxy") and system_config.enable_proxy:
            # 为代理构建服务器 URL
            host = system_config.host
            port = system_config.port
            server_url = f"ws://{host}:{port}/client-ws"
            self.app.include_router(
                init_proxy_route(server_url=server_url),
            )

        # 首先挂载缓存目录（以确保音频文件访问）
        if not os.path.exists("cache"):
            os.makedirs("cache")
        self.app.mount(
            "/cache",
            CORSStaticFiles(directory="cache"),
            name="cache",
        )

        # 使用启用了 CORS 的处理器挂载静态文件
        self.app.mount(
            "/live2d-models",
            CORSStaticFiles(directory="live2d-models"),
            name="live2d-models",
        )
        self.app.mount(
            "/bg",
            CORSStaticFiles(directory="backgrounds"),
            name="backgrounds",
        )
        self.app.mount(
            "/avatars",
            AvatarStaticFiles(directory="avatars"),
            name="avatars",
        )

        # 将 Web 工具目录与前端分开挂载
        self.app.mount(
            "/web-tool",
            CORSStaticFiles(directory="web_tool", html=True),
            name="web_tool",
        )

        # 最后挂载主前端（作为通配符）
        self.app.mount(
            "/",
            CORSStaticFiles(directory="frontend", html=True),
            name="frontend",
        )

    async def initialize(self):
        """从配置异步加载服务上下文。
        如果构造函数中未提供 default_context_cache，则需要调用此函数。"""
        await self.default_context_cache.load_from_config(self.config)

    @staticmethod
    def clean_cache():
        """通过删除并重新创建缓存目录来清理缓存。"""
        cache_dir = "cache"
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            os.makedirs(cache_dir)

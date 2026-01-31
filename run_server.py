# -*- coding: utf-8 -*-
"""
Open-LLM-VTuber 服务器主入口点

此模块是 Open-LLM-VTuber 应用程序的主入口点。
它初始化服务器、处理配置、管理资源并启动 WebSocket 服务器。
"""

# 标准库导入
import os  # 提供与操作系统交互的功能
import sys  # 提供对Python解释器使用的变量和函数的访问
import atexit  # 允许在程序正常退出时执行清理函数
import asyncio  # 提供异步I/O支持
import argparse  # 用于解析命令行参数
import subprocess  # 用于创建新进程、连接到它们的输入/输出/错误管道，并获得返回码
from pathlib import Path  # 面向对象的路径操作接口

# 第三方库导入
import tomli  # TOML解析器，用于读取pyproject.toml文件
import uvicorn  # 运行FastAPI应用程序的ASGI服务器
from loguru import logger  # 高级日志记录库

# 本地导入
from upgrade_codes.upgrade_manager import UpgradeManager  # 版本升级管理器

from src.open_llm_vtuber.server import WebSocketServer  # 核心WebSocket服务器实现
from src.open_llm_vtuber.config_manager import Config, read_yaml, validate_config  # 配置管理实用工具

# 设置环境变量以定义模型的缓存目录
# HF_HOME: Hugging Face模型的缓存目录
# MODELSCOPE_CACHE: ModelScope模型的缓存目录
os.environ["HF_HOME"] = str(Path(__file__).parent / "models")
os.environ["MODELSCOPE_CACHE"] = str(Path(__file__).parent / "models")

# 初始化升级管理器，用于处理版本升级和配置同步
upgrade_manager = UpgradeManager()


def get_version() -> str:
    """
    从pyproject.toml文件中检索应用程序版本。

    返回:
        str: 在pyproject.toml文件中定义的版本字符串
    """
    with open("pyproject.toml", "rb") as f:
        pyproject = tomli.load(f)
    return pyproject["project"]["version"]


def init_logger(console_log_level: str = "INFO") -> None:
    """
    使用控制台和文件输出初始化日志系统。
    
    参数:
        console_log_level (str): 控制台输出的日志级别（默认: INFO）
    """
    logger.remove()
    # 控制台输出，带彩色格式
    logger.add(
        sys.stderr,  # 输出到标准错误流
        level=console_log_level,  # 设置日志级别
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | {message}",  # 设置日志格式
        colorize=True,  # 启用颜色显示
    )

    # 文件输出，带轮转和详细格式以便调试
    logger.add(
        "logs/debug_{time:YYYY-MM-DD}.log",  # 日志文件路径
        rotation="10 MB",  # 当文件大小达到10MB时轮转
        retention="30 days",  # 保留最近30天的日志文件
        level="DEBUG",  # 记录DEBUG及以上级别的日志
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message} | {extra}",  # 详细的日志格式
        backtrace=True,  # 记录完整的回溯信息
        diagnose=True,  # 提供更详细的错误诊断
    )


def check_frontend_submodule(lang=None):
    """
    检查前端子模块是否已初始化。如果没有，则尝试初始化它。
    如果初始化失败，则记录错误消息。

    参数:
        lang (str, 可选): 消息的语言偏好。如果为None，则使用upgrade_manager.lang
    """
    if lang is None:
        lang = upgrade_manager.lang

    # 定义前端主文件路径以检查子模块是否存在
    frontend_path = Path(__file__).parent / "frontend" / "index.html"
    if not frontend_path.exists():
        # 记录关于缺少前端的警告并尝试初始化子模块
        if lang == "zh":
            logger.warning("未找到前端子模块，正在尝试初始化子模块...")
        else:
            logger.warning(
                "Frontend submodule not found, attempting to initialize submodules..."
            )

        try:
            # 运行git命令以递归方式初始化和更新子模块
            subprocess.run(
                ["git", "submodule", "update", "--init", "--recursive"], check=True
            )
            if frontend_path.exists():
                # 初始化成功后的成功消息
                if lang == "zh":
                    logger.info("👍 前端子模块（和其他子模块）初始化成功。")
                else:
                    logger.info(
                        "👍 Frontend submodule (and other submodules) initialized successfully."
                    )
            else:
                # 初始化后前端文件仍缺失时的错误消息
                if lang == "zh":
                    logger.critical(
                        '子模块初始化失败。\n你之后可能会在浏览器中看到 {{"detail":"Not Found"}} 的错误提示。请检查我们的快速入门指南和常见问题页面以获取更多信息。'
                    )
                    logger.error(
                        "初始化子模块后，前端文件仍然缺失。\n"
                        + "你是否手动更改或删除了 `frontend` 文件夹？\n"
                        + "它是一个 Git 子模块 - 你不应该直接修改它。\n"
                        + "如果你这样做了，请使用 `git restore frontend` 丢弃你的更改，然后再试一次。\n"
                    )
                else:
                    logger.critical(
                        'Failed to initialize submodules. \nYou might see {{"detail":"Not Found"}} in your browser. Please check our quick start guide and common issues page from our documentation.'
                    )
                    logger.error(
                        "Frontend files are still missing after submodule initialization.\n"
                        + "Did you manually change or delete the `frontend` folder?  \n"
                        + "It's a Git submodule — you shouldn't modify it directly.  \n"
                        + "If you did, discard your changes with `git restore frontend`, then try again.\n"
                    )
        except Exception as e:
            # git命令失败时的错误消息
            if lang == "zh":
                logger.critical(
                    f'初始化子模块失败: {e}。\n怀疑你跟 GitHub 之间有网络问题。你之后可能会在浏览器中看到 {{"detail":"Not Found"}} 的错误提示。请检查我们的快速入门指南和常见问题页面以获取更多信息。\n'
                )
            else:
                logger.critical(
                    f'Failed to initialize submodules: {e}. \nYou might see {{"detail":"Not Found"}} in your browser. Please check our quick start guide and common issues page from our documentation.\n'
                )


def parse_args():
    """
    解析服务器的命令行参数。
    
    返回:
        argparse.Namespace: 解析后的命令行参数
    """
    parser = argparse.ArgumentParser(description="Open-LLM-VTuber Server")
    parser.add_argument("--verbose", action="store_true", help="启用详细日志记录")
    parser.add_argument(
        "--hf_mirror", action="store_true", help="使用Hugging Face镜像"
    )
    return parser.parse_args()


@logger.catch  # 使用装饰器捕获函数中的异常
def run(console_log_level: str):
    """
    主应用程序运行器函数。

    此函数执行以下步骤:
    1. 初始化日志记录
    2. 检查前端子模块
    3. 同步用户配置
    4. 注册清理函数
    5. 加载和验证配置
    6. 初始化WebSocket服务器
    7. 启动Uvicorn服务器

    参数:
        console_log_level (str): 控制台输出的日志级别
    """
    # 初始化日志记录系统
    init_logger(console_log_level)
    logger.info(f"Open-LLM-VTuber, version v{get_version()}")

    # 获取用于国际化的选定语言
    lang = upgrade_manager.lang

    # 确保前端资源可用
    check_frontend_submodule(lang)

    # 将用户配置与默认设置同步
    try:
        upgrade_manager.sync_user_config()
    except Exception as e:
        logger.error(f"同步用户配置时出错: {e}")

    # 注册程序退出时运行的清理函数
    atexit.register(WebSocketServer.clean_cache)

    # 从YAML文件加载并验证配置
    config: Config = validate_config(read_yaml("conf.yaml"))
    server_config = config.system_config

    # 如果启用了代理模式，则记录状态
    if server_config.enable_proxy:
        logger.info("代理模式已启用 - /proxy-ws端点将可用")

    # 初始化WebSocket服务器实例
    server = WebSocketServer(config=config)

    # 执行异步初始化（加载模型、上下文等）
    logger.info("正在初始化服务器上下文...")
    try:
        asyncio.run(server.initialize())
        logger.info("服务器上下文初始化成功。")
    except Exception as e:
        logger.error(f"服务器上下文初始化失败: {e}")
        sys.exit(1)  # 如果初始化失败则退出

    # 使用配置的主机和端口启动Uvicorn服务器
    logger.info(f"正在{server_config.host}:{server_config.port}上启动服务器")
    uvicorn.run(
        app=server.app,  # FastAPI应用实例
        host=server_config.host,  # 服务器主机地址
        port=server_config.port,  # 服务器端口
        log_level=console_log_level.lower(),  # 设置日志级别
    )


if __name__ == "__main__":
    # 直接运行脚本时解析命令行参数
    args = parse_args()
    
    # 根据详细模式标志确定控制台日志级别
    console_log_level = "DEBUG" if args.verbose else "INFO"
    if args.verbose:
        logger.info("正在详细模式下运行")
    else:
        logger.info(
            "正在标准模式下运行。要获取详细调试日志，请使用: uv run run_server.py --verbose"
        )
    
    # 如果指定，则将Hugging Face端点设置为镜像
    if args.hf_mirror:
        os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
    
    # 运行主应用程序
    run(console_log_level=console_log_level)

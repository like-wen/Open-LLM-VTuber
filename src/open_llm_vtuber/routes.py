import os
import json
from uuid import uuid4
import numpy as np
from datetime import datetime
from fastapi import APIRouter, WebSocket, UploadFile, File, Response
from starlette.responses import JSONResponse
from starlette.websockets import WebSocketDisconnect
from loguru import logger
from .service_context import ServiceContext
from .websocket_handler import WebSocketHandler
from .proxy_handler import ProxyHandler


def init_client_ws_route(default_context_cache: ServiceContext) -> APIRouter:
    """
    创建并返回用于处理 `/client-ws` WebSocket 连接的 API 路由。

    参数:
        default_context_cache: 新会话的默认服务上下文缓存。

    返回:
        APIRouter: 配置了 WebSocket 端点的路由器。
    """

    router = APIRouter()
    ws_handler = WebSocketHandler(default_context_cache)

    @router.websocket("/client-ws")
    async def websocket_endpoint(websocket: WebSocket):
        """客户端连接的 WebSocket 端点"""
        await websocket.accept()
        client_uid = str(uuid4())

        try:
            await ws_handler.handle_new_connection(websocket, client_uid)
            await ws_handler.handle_websocket_communication(websocket, client_uid)
        except WebSocketDisconnect:
            await ws_handler.handle_disconnect(client_uid)
        except Exception as e:
            logger.error(f"WebSocket 连接错误: {e}")
            await ws_handler.handle_disconnect(client_uid)
            raise

    return router


def init_proxy_route(server_url: str) -> APIRouter:
    """
    创建并返回用于处理代理连接的 API 路由。

    参数:
        server_url: 实际服务器的 WebSocket URL

    返回:
        APIRouter: 配置了代理 WebSocket 端点的路由器
    """
    router = APIRouter()
    proxy_handler = ProxyHandler(server_url)

    @router.websocket("/proxy-ws")
    async def proxy_endpoint(websocket: WebSocket):
        """代理连接的 WebSocket 端点"""
        try:
            await proxy_handler.handle_client_connection(websocket)
        except Exception as e:
            logger.error(f"代理连接错误: {e}")
            raise

    return router


def init_webtool_routes(default_context_cache: ServiceContext) -> APIRouter:
    """
    创建并返回用于处理 Web 工具交互的 API 路由。

    参数:
        default_context_cache: 新会话的默认服务上下文缓存。

    返回:
        APIRouter: 配置了 WebSocket 端点的路由器。
    """

    router = APIRouter()

    @router.get("/web-tool")
    async def web_tool_redirect():
        """将 /web-tool 重定向到 /web_tool/index.html"""
        return Response(status_code=302, headers={"Location": "/web-tool/index.html"})

    @router.get("/web_tool")
    async def web_tool_redirect_alt():
        """将 /web_tool 重定向到 /web_tool/index.html"""
        return Response(status_code=302, headers={"Location": "/web-tool/index.html"})

    @router.get("/live2d-models/info")
    async def get_live2d_folder_info():
        """获取可用 Live2D 模型的信息"""
        live2d_dir = "live2d-models"
        if not os.path.exists(live2d_dir):
            return JSONResponse(
                {"error": "未找到 Live2D 模型目录"}, status_code=404
            )

        valid_characters = []
        supported_extensions = [".png", ".jpg", ".jpeg"]

        for entry in os.scandir(live2d_dir):
            if entry.is_dir():
                folder_name = entry.name.replace("\\", "/")
                model3_file = os.path.join(
                    live2d_dir, folder_name, f"{folder_name}.model3.json"
                ).replace("\\", "/")

                if os.path.isfile(model3_file):
                    # 查找头像文件（如果存在）
                    avatar_file = None
                    for ext in supported_extensions:
                        avatar_path = os.path.join(
                            live2d_dir, folder_name, f"{folder_name}{ext}"
                        )
                        if os.path.isfile(avatar_path):
                            avatar_file = avatar_path.replace("\\", "/")
                            break

                    valid_characters.append(
                        {
                            "name": folder_name,
                            "avatar": avatar_file,
                            "model_path": model3_file,
                        }
                    )
        return JSONResponse(
            {
                "type": "live2d-models/info",
                "count": len(valid_characters),
                "characters": valid_characters,
            }
        )

    @router.post("/asr")
    async def transcribe_audio(file: UploadFile = File(...)):
        """
        使用 ASR 引擎转录音频的端点
        """
        logger.info(f"收到音频文件用于转录: {file.filename}")

        try:
            contents = await file.read()

            # 验证最小文件大小
            if len(contents) < 44:  # 最小 WAV 头部大小
                raise ValueError("无效的 WAV 文件: 文件太小")

            # 解码 WAV 头部并获取实际音频数据
            wav_header_size = 44  # 标准 WAV 头部大小
            audio_data = contents[wav_header_size:]

            # 验证音频数据大小
            if len(audio_data) % 2 != 0:
                raise ValueError("无效的音频数据: 缓冲区大小必须为偶数")

            # 转换为 16 位 PCM 样本到 float32
            try:
                audio_array = (
                    np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
                    / 32768.0
                )
            except ValueError as e:
                raise ValueError(
                    f"音频格式错误: {str(e)}。请确保文件是 16 位 PCM WAV 格式。"
                )

            # 验证音频数据
            if len(audio_array) == 0:
                raise ValueError("空音频数据")

            text = await default_context_cache.asr_engine.async_transcribe_np(
                audio_array
            )
            logger.info(f"转录结果: {text}")
            return {"text": text}

        except ValueError as e:
            logger.error(f"音频格式错误: {e}")
            return Response(
                content=json.dumps({"error": str(e)}),
                status_code=400,
                media_type="application/json",
            )
        except Exception as e:
            logger.error(f"转录过程中出错: {e}")
            return Response(
                content=json.dumps(
                    {"error": "转录过程中发生内部服务器错误"}
                ),
                status_code=500,
                media_type="application/json",
            )

    @router.websocket("/tts-ws")
    async def tts_endpoint(websocket: WebSocket):
        """TTS 生成的 WebSocket 端点"""
        await websocket.accept()
        logger.info("TTS WebSocket 连接已建立")

        try:
            while True:
                data = await websocket.receive_json()
                text = data.get("text")
                if not text:
                    continue

                logger.info(f"收到用于 TTS 的文本: {text}")

                # 将文本分割成句子
                sentences = [s.strip() for s in text.split(".") if s.strip()]

                try:
                    # 为每个句子生成并发送音频
                    for sentence in sentences:
                        sentence = sentence + "."  # 添加回句号
                        file_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid4())[:8]}"
                        audio_path = (
                            await default_context_cache.tts_engine.async_generate_audio(
                                text=sentence, file_name_no_ext=file_name
                            )
                        )
                        logger.info(
                            f"为句子生成音频: {sentence}，路径: {audio_path}"
                        )

                        await websocket.send_json(
                            {
                                "status": "partial",
                                "audioPath": audio_path,
                                "text": sentence,
                            }
                        )

                    # 发送完成信号
                    await websocket.send_json({"status": "complete"})

                except Exception as e:
                    logger.error(f"生成 TTS 时出错: {e}")
                    await websocket.send_json({"status": "error", "message": str(e)})

        except WebSocketDisconnect:
            logger.info("TTS WebSocket 客户端已断开连接")
        except Exception as e:
            logger.error(f"TTS WebSocket 连接错误: {e}")
            await websocket.close()

    return router

import asyncio
import http.cookies
import random
import traceback
import json
from typing import Callable, Dict, Any, List, Optional
from loguru import logger
import aiohttp
import websockets
import sys
import os

from .live_interface import LivePlatformInterface

# Import the blivedm library
try:
    # Add project root to path to enable imports
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))

    sys.path.insert(0, os.path.join(project_root, "blivedm"))

    import blivedm
    from blivedm.models import web as web_models
    from blivedm.handlers import BaseHandler

    BLIVEDM_AVAILABLE = True
except ImportError as e:
    logger.warning(f"blivedm import failed: {e}")
    logger.warning("BiliBili live functionality will not be available.")
    BLIVEDM_AVAILABLE = False


class BiliBiliLivePlatform(LivePlatformInterface):
    """
    用于 BiliBili 直播平台的 LivePlatformInterface 实现。
    连接到 BiliBili 直播间并将弹幕消息转发给 VTuber。
    """

    def __init__(self, room_ids: List[int], sessdata: str = ""):
        """
        初始化 BiliBili 直播平台客户端。

        参数:
            room_ids: 要监控的房间 ID 列表
            sessdata: 用于身份验证的可选 SESSDATA cookie 值
        """
        if not BLIVEDM_AVAILABLE:
            raise ImportError(
                "blivedm library is required for BiliBili live functionality"
            )

        self._room_ids = room_ids
        self._sessdata = sessdata
        self._session: Optional[aiohttp.ClientSession] = None
        self._client: Optional[blivedm.BLiveClient] = None
        self._websocket: Optional[websockets.WebSocketClientProtocol] = None
        self._connected = False
        self._running = False
        self._message_handlers: List[Callable[[Dict[str, Any]], None]] = []
        self._conversation_active = False

    @property
    def is_connected(self) -> bool:
        """检查是否连接到代理服务器。"""
        try:
            if hasattr(self._websocket, "closed"):
                return (
                    self._connected and self._websocket and not self._websocket.closed
                )
            elif hasattr(self._websocket, "open"):
                return self._connected and self._websocket and self._websocket.open
            else:
                return self._connected and self._websocket is not None
        except Exception:
            return False

    def _init_session(self):
        """初始化 HTTP 会话并设置 cookies（如果提供）。"""
        cookies = http.cookies.SimpleCookie()
        if self._sessdata:
            cookies["SESSDATA"] = self._sessdata
            cookies["SESSDATA"]["domain"] = "bilibili.com"

        self._session = aiohttp.ClientSession()
        self._session.cookie_jar.update_cookies(cookies)

    async def connect(self, proxy_url: str) -> bool:
        """
        连接到代理 WebSocket 服务器。

        参数:
            proxy_url: 代理的 WebSocket URL

        返回:
            bool: 如果连接成功则为 True
        """
        try:
            # Connect to the proxy WebSocket
            self._websocket = await websockets.connect(
                proxy_url, ping_interval=20, ping_timeout=10, close_timeout=5
            )
            self._connected = True
            logger.info(f"Connected to proxy at {proxy_url}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to proxy: {e}")
            return False

    async def disconnect(self) -> None:
        """
        断开与代理服务器的连接并停止 BiliBili 客户端。
        """
        self._running = False

        # Stop BiliBili client if running
        if self._client:
            try:
                await self._client.stop_and_close()
                self._client = None
            except Exception as e:
                logger.warning(f"Error while stopping BiliBili client: {e}")

        # Close WebSocket connection
        if self._websocket:
            try:
                await self._websocket.close()
            except Exception as e:
                logger.warning(f"Error while closing WebSocket: {e}")

        # Close HTTP session
        if self._session:
            try:
                await self._session.close()
                self._session = None
            except Exception as e:
                logger.warning(f"Error while closing HTTP session: {e}")

        self._connected = False
        logger.info("Disconnected from BiliBili Live and proxy server")

    async def send_message(self, text: str) -> bool:
        """
        通过代理向 VTuber 发送文本消息。
        BiliBili 直播不使用此功能，因为我们只接收消息，不发送消息。

        参数:
            text: 消息文本

        返回:
            bool: 如果发送成功则为 True
        """
        # BiliBili Live platform only receives messages, doesn't send them back to the live room
        logger.warning(
            "BiliBili Live platform doesn't support sending messages back to the live room"
        )
        return False

    async def register_message_handler(
        self, handler: Callable[[Dict[str, Any]], None]
    ) -> None:
        """
        注册处理传入消息的回调函数。

        参数:
            handler: 接收到消息时调用的函数
        """
        self._message_handlers.append(handler)
        logger.debug("Registered new message handler")

    async def _handle_danmaku(self, danmaku_text: str):
        """
        处理接收到的弹幕消息并将其转发给 VTuber。

        参数:
            danmaku_text: 从 BiliBili 接收的弹幕文本
        """
        try:
            # Send danmaku directly to proxy
            await self._send_to_proxy(danmaku_text)
        except Exception as e:
            logger.error(f"Error forwarding danmaku to proxy: {e}")

    async def _send_to_proxy(self, text: str) -> bool:
        """
        将弹幕文本发送到代理。

        参数:
            text: 要发送的弹幕文本

        返回:
            bool: 如果发送成功则为 True
        """
        if not self.is_connected:
            logger.error("Cannot send message: Not connected to proxy")
            return False

        try:
            message = {"type": "text-input", "text": text}
            await self._websocket.send(json.dumps(message))
            logger.info(f"Sent danmaku to VTuber: {text}")
            return True
        except Exception as e:
            logger.error(f"Error sending message to proxy: {e}")
            self._connected = False
            return False

    async def start_receiving(self) -> None:
        """
        开始从代理 WebSocket 接收消息。
        这在后台运行以接收来自 VTuber 的消息。
        """
        if not self.is_connected:
            logger.error("Cannot start receiving: Not connected to proxy")
            return

        try:
            logger.info("Started receiving messages from proxy")
            while self._running and self.is_connected:
                try:
                    message = await self._websocket.recv()
                    data = json.loads(message)

                    # Log received message (truncate audio data for readability)
                    if "audio" in data:
                        log_data = data.copy()
                        log_data["audio"] = (
                            f"[Audio data, length: {len(data['audio'])}]"
                        )
                        logger.debug(f"Received message from VTuber: {log_data}")
                    else:
                        logger.debug(f"Received message from VTuber: {data}")

                    # Process the message
                    await self.handle_incoming_messages(data)

                except websockets.exceptions.ConnectionClosed:
                    logger.warning("WebSocket connection closed by server")
                    self._connected = False
                    break
                except Exception as e:
                    logger.error(f"Error receiving message from proxy: {e}")
                    await asyncio.sleep(1)

            logger.info("Stopped receiving messages from proxy")
        except Exception as e:
            logger.error(f"Error in message receiving loop: {e}")

    async def handle_incoming_messages(self, message: Dict[str, Any]) -> None:
        """
        处理由 VTuber 接收的消息。

        参数:
            message: 从 VTuber 接收的消息
        """
        # Process the message with all registered handlers
        for handler in self._message_handlers:
            try:
                await asyncio.to_thread(handler, message)
            except Exception as e:
                logger.error(f"Error in message handler: {e}")

    class VtuberHandler(BaseHandler):
        """
        BiliBili 直播弹幕消息的处理器。
        """

        def __init__(self, platform):
            super().__init__()
            self.platform = platform

        def _on_danmaku(
            self, client: blivedm.BLiveClient, message: web_models.DanmakuMessage
        ):
            """
            处理来自 BiliBili 直播的弹幕消息。

            参数:
                client: BiliBili 直播客户端
                message: 弹幕消息
            """
            logger.debug(f"[Room {client.room_id}] {message.uname}: {message.msg}")
            asyncio.create_task(self.platform._handle_danmaku(message.msg))

        def _on_heartbeat(
            self, client: blivedm.BLiveClient, message: web_models.HeartbeatMessage
        ):
            """
            处理来自 BiliBili 直播的心跳包。

            参数:
                client: BiliBili 直播客户端
                message: 心跳消息
            """
            logger.debug(
                f"[Room {client.room_id}] Heartbeat, popularity: {message.popularity}"
            )

    async def run(self) -> None:
        """
        运行 BiliBili 直播平台客户端的主要入口点。
        连接到 BiliBili 直播间和代理，并开始监控弹幕。
        """
        proxy_url = "ws://localhost:12393/proxy-ws"

        try:
            self._running = True

            # Initialize HTTP session
            self._init_session()

            # Connect to the proxy
            if not await self.connect(proxy_url):
                logger.error("Failed to connect to proxy, exiting")
                return

            # Start background task for receiving messages from the proxy
            receive_task = asyncio.create_task(self.start_receiving())

            # Randomly select a room ID if multiple are provided
            room_id = random.choice(self._room_ids)

            # Create and start the BiliBili Live client
            self._client = blivedm.BLiveClient(room_id, session=self._session)
            handler = self.VtuberHandler(self)
            self._client.set_handler(handler)
            self._client.start()

            logger.info(f"Connected to BiliBili Live room {room_id}")

            # Wait until stopped
            try:
                await self._client.join()
            finally:
                await self._client.stop_and_close()

            # Clean up receive task if necessary
            if not receive_task.done():
                receive_task.cancel()
                try:
                    await receive_task
                except asyncio.CancelledError:
                    pass

        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down")
        except Exception as e:
            logger.error(f"Error in BiliBili Live run loop: {e}")
            logger.debug(traceback.format_exc())
        finally:
            # Ensure clean disconnect
            await self.disconnect()

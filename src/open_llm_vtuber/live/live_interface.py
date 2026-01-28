from abc import ABC, abstractmethod
import asyncio
from typing import Callable, Dict, Any


class LivePlatformInterface(ABC):
    """
    直播平台的抽象接口。
    此接口定义了任何直播平台实现必须提供的方法。
    它处理通过代理连接到 VTuber 服务器，发送来自直播平台的消息，
    并接收响应。
    """

    @abstractmethod
    async def connect(self, proxy_url: str) -> bool:
        """
        通过代理 WebSocket 连接到 VTuber 服务器。

        参数:
            proxy_url: 代理的 WebSocket URL

        返回:
            bool: 如果连接成功则为 True，否则为 False
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """
        断开与代理服务器的连接。
        """
        pass

    @abstractmethod
    async def send_message(self, text: str) -> bool:
        """
        从直播平台向 VTuber 发送消息。

        参数:
            text: 消息文本内容

        返回:
            bool: 如果消息发送成功则为 True，否则为 False
        """
        pass

    @abstractmethod
    async def register_message_handler(
        self, handler: Callable[[Dict[str, Any]], None]
    ) -> None:
        """
        注册一个回调函数来处理来自 VTuber 的响应消息。

        参数:
            handler: 以消息字典作为参数的回调函数
        """
        pass

    @abstractmethod
    async def start_receiving(self) -> None:
        """
        开始从代理服务器接收消息。
        此方法通常应在单独的任务中运行。
        """
        pass

    @abstractmethod
    async def run(self) -> None:
        """
        运行直播平台客户端的主要入口点。
        这应该处理完整的生命周期，包括连接、
        消息接收和干净断开连接。
        """
        pass

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """
        检查客户端当前是否连接到代理。

        返回:
            bool: 如果已连接则为 True，否则为 False
        """
        pass

    @abstractmethod
    async def handle_incoming_messages(self, message: Dict[str, Any]) -> None:
        """
        处理由 VTuber 服务器接收的消息。

        参数:
            message: 从 VTuber 接收的消息
        """
        pass


class MessageQueue:
    """
    A simple message queue for storing and retrieving messages.
    """

    def __init__(self):
        """Initialize an empty message queue."""
        self._queue = asyncio.Queue()

    async def put(self, message: str) -> None:
        """
        Add a message to the queue.

        Args:
            message: Message to queue
        """
        await self._queue.put(message)

    async def get(self) -> str:
        """
        Get the next message from the queue.

        Returns:
            str: The next message
        """
        return await self._queue.get()

    def empty(self) -> bool:
        """
        Check if the queue is empty.

        Returns:
            bool: True if empty, False otherwise
        """
        return self._queue.empty()

    def qsize(self) -> int:
        """
        Get the current queue size.

        Returns:
            int: Number of messages in queue
        """
        return self._queue.qsize()

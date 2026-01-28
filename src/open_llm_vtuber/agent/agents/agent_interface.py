from abc import ABC, abstractmethod
from typing import AsyncIterator
from loguru import logger

from ..output_types import BaseOutput
from ..input_types import BaseInput


class AgentInterface(ABC):
    """所有代理实现的基础接口"""

    @abstractmethod
    async def chat(self, input_data: BaseInput) -> AsyncIterator[BaseOutput]:
        """
        异步与代理聊天。

        此函数应由代理实现。
        输出类型取决于代理的 output_type：
        - SentenceOutput: 用于带有显示文本和 TTS 文本的基于文本的响应
        - AudioOutput: 用于带有显示文本和 transcript 的直接音频输出

        参数:
            input_data: BaseInput - 用户输入数据

        返回:
            AsyncIterator[BaseOutput] - 代理输出的流
        """
        logger.critical("代理: 未设置聊天功能。")
        raise ValueError("代理: 未设置聊天功能。")

    @abstractmethod
    def handle_interrupt(self, heard_response: str) -> None:
        """
        处理用户中断。当代理被中断时，将调用此函数。

        参数:
            heard_response: str - 中断前听到的响应部分
        """
        logger.warning(
            """代理: 未设置中断处理器。代理可能无法正确处理中断
            。AI 可能无法理解它被中断了。"""
        )
        pass

    @abstractmethod
    def set_memory_from_history(self, conf_uid: str, history_uid: str) -> None:
        """
        从聊天历史加载代理的工作记忆

        参数:
            conf_uid: str - 配置 ID
            history_uid: str - 历史 ID
        """
        pass

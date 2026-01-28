import abc
from typing import AsyncIterator, List, Dict, Any


class StatelessLLMInterface(metaclass=abc.ABCMeta):
    """
    无状态语言模型的接口。

    "无状态" 意味着语言模型不存储记忆、系统提示或用户消息，这是大多数 LLM 的特点。如果我们向 LLM 发送消息，它的响应将仅基于消息参数。

    StatelessLLMInterface 类提供了异步生成聊天完成的方法。

    我们使用 StatelessLLMs 来初始化 Agents，这些 Agents 会为 StatelessLLM 添加记忆、系统提示和其他功能。

    """

    @abc.abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        system: str = None,
        tools: List[Dict[str, Any]] = None,
    ) -> AsyncIterator[str]:
        """
        异步生成聊天完成并返回响应的迭代器。
        此函数不存储记忆或用户消息。

        参数:
        - messages (List[Dict[str, Any]]): 要发送到 API 的消息列表。
        - system (str, optional): 用于此完成的系统提示。
        - tools (List[Dict[str, str]], optional): 用于此完成的工具列表。
            - 每个工具应遵循以下格式:
            {
                "name": "tool_name",
                "description": "tool_description",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "param1": {
                            "type": "string",
                            "description": "param1 的描述"
                        },
                        "param2": {
                            "type": "integer",
                            "description": "param2 的描述"
                        }
                    },
                    "required": ["param1"]
                }
            }

        产生:
        - str: API 响应中每个 chunk 的内容。

        引发:
        - APIConnectionError: 当无法连接到服务器时
        - RateLimitError: 当收到 429 状态码时
        - APIError: 其他与 API 相关的错误
        """
        raise NotImplementedError

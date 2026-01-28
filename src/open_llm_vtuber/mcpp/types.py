from dataclasses import dataclass, field
from datetime import timedelta
from typing import Optional, Any


@dataclass
class MCPServer:
    """表示 MCP 服务器的类

    参数:
        name (str): 服务器名称。
        command (str): 运行服务器的命令。
        args (list[str], optional): 命令的参数。默认为空列表。
        env (Optional[dict[str, str]], optional): 命令的环境变量。默认为 None。
        cwd (Optional[str], optional): 命令的工作目录。默认为 None。
        timeout (Optional[timedelta], optional): 命令的超时时间。默认为 30 秒。
    """

    name: str
    command: str
    args: list[str] = field(default_factory=list)
    env: Optional[dict[str, str]] = None
    cwd: str | None = None
    timeout: Optional[timedelta] = timedelta(seconds=30)
    description: str = "No description available."


@dataclass
class FormattedTool:
    """ "表示格式化工具的类

    参数:
        input_schema (dict[str, Any]): 工具的输入模式。
        related_server (str): 包含该工具的服务器名称。
        generic_schema (Optional[dict[str, Any]], optional): 工具的通用模式。默认为 None。
        description (str, optional): 工具的描述，通常来自服务器的工具定义。默认为 "No description available."。
    """

    input_schema: dict[str, Any]
    related_server: str
    generic_schema: Optional[dict[str, Any]] = None
    description: str = "No description available."


@dataclass
class ToolCallFunctionObject:
    """表示工具调用中的函数对象的类

    此类模仿 OpenAI API 工具调用的函数对象结构。

    参数:
        name (str): 函数名称。
        arguments (str): 函数的参数，以 JSON 字符串形式。
    """

    name: str = ""
    arguments: str = ""


@dataclass
class ToolCallObject:
    """表示工具调用对象的类

    此类模仿 OpenAI API ChoiceDeltaToolCall 结构。

    参数:
        id (str): 工具调用的唯一标识符。
        type (str): 工具调用的类型，通常是 "function"。
        index (int): 序列中工具调用的索引。
        function (ToolCallFunctionObject): 工具调用的函数信息。
    """

    id: Optional[str] = None
    type: str = "function"
    index: int = 0
    function: ToolCallFunctionObject = field(default_factory=ToolCallFunctionObject)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ToolCallObject":
        """从字典创建 ToolCallObject

        参数:
            data (dict[str, Any]): 包含工具调用数据的字典。

        返回:
            ToolCallObject: 新的 ToolCallObject 实例。
        """
        function = ToolCallFunctionObject(
            name=data["function"]["name"], arguments=data["function"]["arguments"]
        )
        return cls(
            id=data["id"], type=data["type"], index=data["index"], function=function
        )

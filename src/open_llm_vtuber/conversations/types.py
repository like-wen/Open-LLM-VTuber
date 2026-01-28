from typing import List, Dict, Callable, Optional, TypedDict, Awaitable, ClassVar
from dataclasses import dataclass, field
from pydantic import BaseModel

from ..agent.output_types import Actions, DisplayText

# Type definitions
WebSocketSend = Callable[[str], Awaitable[None]]
BroadcastFunc = Callable[[List[str], dict, Optional[str]], Awaitable[None]]


class AudioPayload(TypedDict):
    """音频payload的类型定义"""

    type: str
    audio: Optional[str]
    volumes: Optional[List[float]]
    slice_length: Optional[int]
    display_text: Optional[DisplayText]
    actions: Optional[Actions]
    forwarded: Optional[bool]


@dataclass
class BroadcastContext:
    """群组聊天中广播消息的上下文"""

    broadcast_func: Optional[BroadcastFunc] = None
    group_members: Optional[List[str]] = None
    current_client_uid: Optional[str] = None


class ConversationConfig(BaseModel):
    """对话链的配置"""

    conf_uid: str = ""
    history_uid: str = ""
    client_uid: str = ""
    character_name: str = "AI"


@dataclass
class GroupConversationState:
    """群组对话的状态"""

    # 类变量用于跟踪当前状态
    _states: ClassVar[Dict[str, "GroupConversationState"]] = {}

    group_id: str
    conversation_history: List[str] = field(default_factory=list)
    memory_index: Dict[str, int] = field(default_factory=dict)
    group_queue: List[str] = field(default_factory=list)
    session_emoji: str = ""
    current_speaker_uid: Optional[str] = None

    def __post_init__(self):
        """初始化后注册状态实例"""
        GroupConversationState._states[self.group_id] = self

    @classmethod
    def get_state(cls, group_id: str) -> Optional["GroupConversationState"]:
        """通过group_id获取对话状态"""
        return cls._states.get(group_id)

    @classmethod
    def remove_state(cls, group_id: str) -> None:
        """完成后移除对话状态"""
        cls._states.pop(group_id, None)

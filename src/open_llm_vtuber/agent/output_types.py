from dataclasses import dataclass, asdict
from typing import List, Optional
from abc import ABC, abstractmethod


@dataclass
class Actions:
    """表示可以与文本输出一起执行的操作"""

    expressions: Optional[List[str] | List[int]] = None
    pictures: Optional[List[str]] = None
    sounds: Optional[List[str]] = None

    def to_dict(self) -> dict:
        """将 Actions 对象转换为字典以进行 JSON 序列化"""
        return {k: v for k, v in asdict(self).items() if v is not None}


class BaseOutput(ABC):
    """可迭代的代理输出的基类"""

    @abstractmethod
    def __aiter__(self):
        """使输出可迭代"""
        pass


@dataclass
class DisplayText:
    """要显示的带有可选元数据的文本"""

    text: str
    name: Optional[str] = "AI"  # Keep the name field for frontend display
    avatar: Optional[str] = None

    def to_dict(self) -> dict:
        """转换为字典以进行 JSON 序列化"""
        return {"text": self.text, "name": self.name, "avatar": self.avatar}

    def __str__(self) -> str:
        """用于日志记录的字符串表示"""
        return f"{self.name}: {self.text}"


@dataclass
class SentenceOutput(BaseOutput):
    """
    基于文本的响应的输出类型。
    包含单个句子对（显示和 TTS）以及相关操作。

    属性:
        display_text: 要在 UI 中显示的文本
        tts_text: 要发送到 TTS 引擎的文本
        actions: 相关操作（表情、图片、声音）
    """

    display_text: DisplayText  # Changed from str to DisplayText
    tts_text: str  # Text for TTS
    actions: Actions

    async def __aiter__(self):
        """产生句子对和操作"""
        yield self.display_text, self.tts_text, self.actions


@dataclass
class AudioOutput(BaseOutput):
    """基于音频的响应的输出类型"""

    audio_path: str
    display_text: DisplayText  # Changed from str to DisplayText
    transcript: str  # Original transcript
    actions: Actions

    async def __aiter__(self):
        """遍历音频片段及其操作"""
        yield self.audio_path, self.display_text, self.transcript, self.actions

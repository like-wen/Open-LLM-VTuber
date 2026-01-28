from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any


class ImageSource(Enum):
    """不同图像来源的枚举"""

    CAMERA = "camera"
    SCREEN = "screen"
    CLIPBOARD = "clipboard"
    UPLOAD = "upload"


class TextSource(Enum):
    """不同文本来源的枚举"""

    INPUT = "input"  # Main user input/transcription
    CLIPBOARD = "clipboard"  # Text from clipboard


@dataclass
class ImageData:
    """
    表示来自各种来源的图像

    属性:
        source: 图像的来源
        data: Base64 编码的图像数据或 URL
        mime_type: 图像的 MIME 类型（例如 'image/jpeg', 'image/png'）
    """

    source: ImageSource
    data: str  # Base64 encoded or URL
    mime_type: str


@dataclass
class FileData:
    """
    表示用户上传的文件

    属性:
        name: 原始文件名
        data: Base64 编码的文件数据
        mime_type: 文件的 MIME 类型
    """

    name: str
    data: str  # Base64 encoded
    mime_type: str


@dataclass
class TextData:
    """
    表示来自各种来源的文本数据

    属性:
        source: 文本的来源
        content: str - 文本内容
        from_name: Optional[str] - 发送者/角色的名称
    """

    source: TextSource
    content: str
    from_name: Optional[str] = None


class BaseInput:
    """所有输入类型的基类"""

    pass


@dataclass
class BatchInput(BaseInput):
    """
    批量处理的输入类型，包含完整的转录和可选的媒体

    属性:
        texts: 来自不同来源的文本数据列表
        images: 可选的图像列表
        files: 可选的文件列表
        metadata: 特殊输入的元数据标志的可选字典
            - 'proactive_speak': 布尔标志，指示这是否是主动发言输入
            - 'skip_memory': 布尔标志，指示此输入是否应在 AI 的内部内存中跳过
            - 'skip_history': 布尔标志，指示此输入是否应在本地历史存储中跳过
    """

    texts: List[TextData]
    images: Optional[List[ImageData]] = None
    files: Optional[List[FileData]] = None
    metadata: Optional[Dict[str, Any]] = None

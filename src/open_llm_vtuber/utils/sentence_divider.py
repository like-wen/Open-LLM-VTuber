import re
from typing import List, Tuple, AsyncIterator, Optional, Union, Dict, Any
import pysbd
from loguru import logger
from langdetect import detect
from enum import Enum
from dataclasses import dataclass

# Constants for additional checks
COMMAS = [
    ",",
    "،",
    "，",
    "、",
    "፣",
    "၊",
    ";",
    "΄",
    "‛",
    "।",
    "﹐",
    "꓾",
    "⹁",
    "︐",
    "﹑",
    "､",
    "،",
]

END_PUNCTUATIONS = [".", "!", "?", "。", "！", "？", "...", "。。。"]
ABBREVIATIONS = [
    "Mr.",
    "Mrs.",
    "Dr.",
    "Prof.",
    "Inc.",
    "Ltd.",
    "Jr.",
    "Sr.",
    "e.g.",
    "i.e.",
    "vs.",
    "St.",
    "Rd.",
    "Dr.",
]

# Set of languages directly supported by pysbd
SUPPORTED_LANGUAGES = {
    "am",
    "ar",
    "bg",
    "da",
    "de",
    "el",
    "en",
    "es",
    "fa",
    "fr",
    "hi",
    "hy",
    "it",
    "ja",
    "kk",
    "mr",
    "my",
    "nl",
    "pl",
    "ru",
    "sk",
    "ur",
    "zh",
}


def detect_language(text: str) -> str:
    """
    检测文本语言并检查是否被 pysbd 支持。
    对于不支持的语言返回 None。
    """
    try:
        detected = detect(text)
        return detected if detected in SUPPORTED_LANGUAGES else None
    except Exception as e:
        logger.debug(f"语言检测失败，语言不被 pysdb 支持: {e}")
        return None


def is_complete_sentence(text: str) -> bool:
    """
    检查文本是否以句子结束标点结尾且不是缩写。

    参数:
        text: 要检查的文本

    返回:
        bool: 文本是否是完整句子
    """
    text = text.strip()
    if not text:
        return False

    if any(text.endswith(abbrev) for abbrev in ABBREVIATIONS):
        return False

    return any(text.endswith(punct) for punct in END_PUNCTUATIONS)


def contains_comma(text: str) -> bool:
    """
    检查文本是否包含任何逗号。

    参数:
        text: 要检查的文本

    返回:
        bool: 文本是否包含逗号
    """
    return any(comma in text for comma in COMMAS)


def comma_splitter(text: str) -> Tuple[str, str]:
    """
    处理文本并在第一个逗号处分割。
    返回分割的文本（包括逗号）和剩余文本。

    参数:
        text: 要分割的文本

    返回:
        Tuple[str, str]: (带逗号的分割文本, 剩余文本)
    """
    if not text:
        return [], ""

    for comma in COMMAS:
        if comma in text:
            split_text = text.split(comma, 1)
            # 返回带逗号的第一部分
            return split_text[0].strip() + comma, split_text[1].strip()
    return text, ""


def has_punctuation(text: str) -> bool:
    """
    检查文本是否是标点符号。

    参数:
        text: 要检查的文本

    返回:
        bool: 文本是否是标点符号
    """
    for punct in COMMAS + END_PUNCTUATIONS:
        if punct in text:
            return True
    return False


def contains_end_punctuation(text: str) -> bool:
    """
    检查文本是否包含任何句子结束标点。

    参数:
        text: 要检查的文本

    返回:
        bool: 文本是否包含结束标点
    """
    return any(punct in text for punct in END_PUNCTUATIONS)


def segment_text_by_regex(text: str) -> Tuple[List[str], str]:
    """
    使用正则表达式模式匹配将文本分割为完整句子。
    比 pysbd 更高效但准确性较低。

    参数:
        text: 要分割为句子的文本

    返回:
        Tuple[List[str], str]: (完整句子列表, 剩余不完整文本)
    """
    if not text:
        return [], ""

    complete_sentences = []
    remaining_text = text.strip()

    # 创建匹配以任何结束标点结尾的句子的模式
    escaped_punctuations = [re.escape(p) for p in END_PUNCTUATIONS]
    pattern = r"(.*?(?:[" + "|".join(escaped_punctuations) + r"]))"

    while remaining_text:
        match = re.search(pattern, remaining_text)
        if not match:
            break

        end_pos = match.end(1)
        potential_sentence = remaining_text[:end_pos].strip()

        # 如果句子以缩写结尾则跳过
        if any(potential_sentence.endswith(abbrev) for abbrev in ABBREVIATIONS):
            remaining_text = remaining_text[end_pos:].lstrip()
            continue

        complete_sentences.append(potential_sentence)
        remaining_text = remaining_text[end_pos:].lstrip()

    return complete_sentences, remaining_text


def segment_text_by_pysbd(text: str) -> Tuple[List[str], str]:
    """
    将文本分割为完整句子和剩余文本。
    对支持的语言使用 pysbd，对其他语言回退到正则表达式。

    参数:
        text: 要分割为句子的文本

    返回:
        Tuple[List[str], str]: (完整句子列表, 剩余不完整文本)
    """
    if not text:
        return [], ""

    try:
        # 检测语言
        lang = detect_language(text)

        if lang is not None:
            # 对支持的语言使用 pysbd
            segmenter = pysbd.Segmenter(language=lang, clean=False)
            sentences = segmenter.segment(text)

            if not sentences:
                return [], text

            # 处理除最后一句以外的所有句子
            complete_sentences = []
            for sent in sentences[:-1]:
                sent = sent.strip()
                if sent:
                    complete_sentences.append(sent)

            # 处理最后一句
            last_sent = sentences[-1].strip()
            if is_complete_sentence(last_sent):
                complete_sentences.append(last_sent)
                remaining = ""
            else:
                remaining = last_sent

        else:
            # 对不支持的语言使用正则表达式
            return segment_text_by_regex(text)

        logger.debug(
            f"处理的句子: {complete_sentences}, 剩余: {remaining}"
        )
        return complete_sentences, remaining

    except Exception as e:
        logger.error(f"句子分割错误: {e}")
        # 任何错误时回退到正则表达式
        return segment_text_by_regex(text)


class TagState(Enum):
    """文本中标签的状态"""

    START = "start"  # <tag>
    INSIDE = "inside"  # 标签之间的文本
    END = "end"  # </tag>
    SELF_CLOSING = "self"  # <tag/>
    NONE = "none"  # 无标签


@dataclass
class TagInfo:
    """关于标签的信息"""

    name: str
    state: TagState

    def __str__(self) -> str:
        """标签信息的字符串表示"""
        if self.state == TagState.NONE:
            return "none"
        return f"{self.name}:{self.state.value}"


@dataclass
class SentenceWithTags:
    """带有标签信息的句子，支持嵌套标签"""

    text: str
    tags: List[TagInfo]  # 从外层到内层的标签列表


class SentenceDivider:
    def __init__(
        self,
        faster_first_response: bool = True,
        segment_method: str = "pysbd",
        valid_tags: List[str] = None,
    ):
        """
        初始化 SentenceDivider。

        参数:
            faster_first_response: 是否在逗号处分割第一个句子
            segment_method: 分割句子的方法
            valid_tags: 要检测的有效标签名称列表
        """
        self.faster_first_response = faster_first_response
        self.segment_method = segment_method
        self.valid_tags = valid_tags or ["think"]
        self._is_first_sentence = True
        self._buffer = ""
        # 用栈替换 active_tags 字典以处理嵌套
        self._tag_stack = []

    def _get_current_tags(self) -> List[TagInfo]:
        """
        获取从外层到内层的所有当前活动标签。

        返回:
            List[TagInfo]: 活动标签列表
        """
        return [TagInfo(tag.name, TagState.INSIDE) for tag in self._tag_stack]

    def _get_current_tag(self) -> Optional[TagInfo]:
        """
        获取当前最内层的活动标签。

        返回:
            如果有活动标签则返回 TagInfo，否则返回 None
        """
        return self._tag_stack[-1] if self._tag_stack else None

    def _extract_tag(self, text: str) -> Tuple[Optional[TagInfo], str]:
        """
        从文本中提取第一个标签（如果存在）。
        通过维护标签栈来处理嵌套标签。

        参数:
            text: 要检查标签的文本

        返回:
            Tuple of (如果找到标签则返回 TagInfo 否则返回 None, 剩余文本)
        """
        # 查找任何标签的第一次出现
        first_tag = None
        first_pos = len(text)
        tag_type = None
        matched_tag = None

        # 检查自闭合标签
        for tag in self.valid_tags:
            pattern = f"<{tag}/>"
            match = re.search(pattern, text)
            if match and match.start() < first_pos:
                first_pos = match.start()
                first_tag = match
                tag_type = TagState.SELF_CLOSING
                matched_tag = tag

        # 检查开始标签
        for tag in self.valid_tags:
            pattern = f"<{tag}>"
            match = re.search(pattern, text)
            if match and match.start() < first_pos:
                first_pos = match.start()
                first_tag = match
                tag_type = TagState.START
                matched_tag = tag

        # 检查结束标签
        for tag in self.valid_tags:
            pattern = f"</{tag}>"
            match = re.search(pattern, text)
            if match and match.start() < first_pos:
                first_pos = match.start()
                first_tag = match
                tag_type = TagState.END
                matched_tag = tag

        if not first_tag:
            return None, text

        # 处理找到的标签
        if tag_type == TagState.START:
            # 将新标签推入栈
            self._tag_stack.append(TagInfo(matched_tag, TagState.START))
        elif tag_type == TagState.END:
            # 验证匹配的标签
            if not self._tag_stack or self._tag_stack[-1].name != matched_tag:
                logger.warning(f"不匹配的结束标签: {matched_tag}")
            else:
                self._tag_stack.pop()

        return (TagInfo(matched_tag, tag_type), text[first_tag.end() :].lstrip())

    async def _process_buffer(self) -> AsyncIterator[SentenceWithTags]:
        """
        处理当前缓冲区，产生带有标签的完整句子。
        现在这是一个异步生成器。
        它从 self._buffer 中消费已处理的部分。
        """
        processed_something = True  # 标记，用于循环直到无法再处理
        while processed_something:
            processed_something = False
            original_buffer_len = len(self._buffer)

            if not self._buffer.strip():
                break

            # 查找下一个标签位置
            next_tag_pos = len(self._buffer)
            tag_pattern_found = None
            for tag in self.valid_tags:
                patterns = [f"<{tag}>", f"</{tag}>", f"<{tag}/>"]
                for pattern in patterns:
                    pos = self._buffer.find(pattern)
                    if pos != -1 and pos < next_tag_pos:
                        next_tag_pos = pos
                        tag_pattern_found = pattern  # 存储找到的模式

            if next_tag_pos == 0:
                # 标签在缓冲区开头
                tag_info, remaining = self._extract_tag(self._buffer)
                if tag_info:
                    processed_text = self._buffer[
                        : len(self._buffer) - len(remaining)
                    ].strip()
                    # 产生标签本身，表示为 SentenceWithTags
                    yield SentenceWithTags(text=processed_text, tags=[tag_info])
                    self._buffer = remaining
                    processed_something = True
                    continue  # 重新开始处理剩余缓冲区的循环

            elif next_tag_pos < len(self._buffer):
                # 标签在中间 - 先处理标签前的文本
                text_before_tag = self._buffer[:next_tag_pos]
                current_tags = self._get_current_tags()
                processed_segment = ""

                # 处理标签前文本中的完整句子
                if contains_end_punctuation(text_before_tag):
                    sentences, remaining_before = self._segment_text(text_before_tag)
                    for sentence in sentences:
                        if sentence.strip():
                            yield SentenceWithTags(
                                text=sentence.strip(),
                                tags=current_tags or [TagInfo("", TagState.NONE)],
                            )
                    # 消费的部分包括句子 + 标签前剩余的内容
                    processed_segment = text_before_tag
                    self._buffer = self._buffer[len(processed_segment) :]
                    processed_something = True
                    continue  # 重新开始处理循环

                elif text_before_tag.strip() and tag_pattern_found:
                    # 没有句子结束，但存在内容 AND 我们在其后找到了标签模式。
                    # 我们可以产生这个段，因为标签提供了边界。
                    yield SentenceWithTags(
                        text=text_before_tag.strip(),
                        tags=current_tags or [TagInfo("", TagState.NONE)],
                    )
                    self._buffer = self._buffer[len(text_before_tag) :]
                    processed_something = True
                    continue  # 重新开始处理循环
                # --- 如果在 text_before_tag 后未找到标签，我们等待更多输入或结束标点 ---

                # 如果我们没有继续，则处理标签本身
                tag_info, remaining_after_tag = self._extract_tag(self._buffer)
                if tag_info:
                    processed_tag_text = self._buffer[
                        : len(self._buffer) - len(remaining_after_tag)
                    ].strip()
                    yield SentenceWithTags(text=processed_tag_text, tags=[tag_info])
                    self._buffer = remaining_after_tag
                    processed_something = True
                    continue  # 重新开始处理循环

            # 未找到标签或标签不在可处理段的开头/中间
            # 如果缓冲区已更改或存在标点，则处理普通文本
            if original_buffer_len > 0:
                current_tags = self._get_current_tags()

                # 如果启用，处理带逗号的第一句
                if (
                    self._is_first_sentence
                    and self.faster_first_response
                    and contains_comma(self._buffer)
                ):
                    sentence, remaining = comma_splitter(self._buffer)
                    if sentence.strip():
                        yield SentenceWithTags(
                            text=sentence.strip(),
                            tags=current_tags or [TagInfo("", TagState.NONE)],
                        )
                        self._buffer = remaining
                        self._is_first_sentence = False
                        processed_something = True
                        continue  # 重新开始处理循环

                # 基于结束标点处理普通句子
                if contains_end_punctuation(self._buffer):
                    sentences, remaining = self._segment_text(self._buffer)
                    if sentences:  # 仅当分割产生句子时处理
                        self._buffer = remaining
                        self._is_first_sentence = False
                        processed_something = True
                        for sentence in sentences:
                            if sentence.strip():
                                yield SentenceWithTags(
                                    text=sentence.strip(),
                                    tags=current_tags or [TagInfo("", TagState.NONE)],
                                )
                        continue  # 重新开始处理循环

            # 如果我们到达这里而没有处理任何内容，则跳出循环
            if not processed_something:
                break

    async def _flush_buffer(self) -> AsyncIterator[SentenceWithTags]:
        """
        在流结束时处理并产生缓冲区中的所有剩余内容。
        """
        logger.debug(f"刷新剩余缓冲区: '{self._buffer}'")
        # 首先，运行 _process_buffer 以产生任何标准句子/标签
        async for sentence in self._process_buffer():
            yield sentence

        # 处理标准结构后，如果有任何剩余内容，将其作为最终片段产生
        if self._buffer.strip():
            logger.debug(
                f"从缓冲区产生最终片段: '{self._buffer.strip()}'"
            )
            current_tags = self._get_current_tags()
            yield SentenceWithTags(
                text=self._buffer.strip(),
                tags=current_tags or [TagInfo("", TagState.NONE)],
            )
            self._buffer = ""  # 刷新后清除缓冲区

    async def process_stream(
        self, segment_stream: AsyncIterator[Union[str, Dict[str, Any]]]
    ) -> AsyncIterator[Union[SentenceWithTags, Dict[str, Any]]]:
        """
        处理令牌（字符串）和字典的流。
        产生带有标签的完整句子（SentenceWithTags）或直接产生字典。

        参数:
            segment_stream: 产生字符串或字典的异步迭代器。

        产生:
            Union[SentenceWithTags, Dict[str, Any]]: 完整句子/标签或原始字典。
        """
        self._full_response = []
        self.reset()  # 确保状态干净

        async for item in segment_stream:
            if isinstance(item, dict):
                # 在产生字典之前，处理并产生到目前为止形成的任何完整句子
                async for sentence in self._process_buffer():
                    self._full_response.append(
                        sentence.text
                    )  # 跟踪完整响应
                    yield sentence
                # 现在产生字典
                yield item
            elif isinstance(item, str):
                self._buffer += item
                # 随着字符串块的到达，增量处理缓冲区
                async for sentence in self._process_buffer():
                    self._full_response.append(
                        sentence.text
                    )  # 跟踪完整响应
                    yield sentence
            else:
                logger.warning(
                    f"SentenceDivider 收到意外类型: {type(item)}"
                )

        # 流结束后，刷新缓冲区中的任何剩余文本
        async for sentence in self._flush_buffer():
            self._full_response.append(sentence.text)
            yield sentence

    @property
    def complete_response(self) -> str:
        """获取到目前为止累积的完整响应"""
        return "".join(self._full_response)

    def _segment_text(self, text: str) -> Tuple[List[str], str]:
        """使用配置的方法分割文本"""
        if self.segment_method == "regex":
            return segment_text_by_regex(text)
        return segment_text_by_pysbd(text)

    def reset(self):
        """为新对话重置分割器状态"""
        self._is_first_sentence = True
        self._buffer = ""
        self._tag_stack = []

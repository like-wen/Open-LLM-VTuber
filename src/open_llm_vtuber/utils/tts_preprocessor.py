import re
import unicodedata
from loguru import logger
from ..translate.translate_interface import TranslateInterface


def tts_filter(
    text: str,
    remove_special_char: bool,
    ignore_brackets: bool,
    ignore_parentheses: bool,
    ignore_asterisks: bool,
    ignore_angle_brackets: bool,
    translator: TranslateInterface | None = None,
) -> str:
    """
    在 TTS 生成音频之前过滤或处理文本。
    此处的更改不会影响字幕或 LLM 的记忆。生成的音频是唯一受影响的内容。

    参数:
        text (str): 要过滤的文本。
        remove_special_char (bool): 是否删除特殊字符。
        ignore_brackets (bool): 是否忽略括号内的文本。
        ignore_parentheses (bool): 是否忽略圆括号内的文本。
        ignore_asterisks (bool): 是否忽略星号内的文本。
        ignore_angle_brackets (bool): 是否忽略尖括号内的文本。
        translator (TranslateInterface, optional):
            要使用的翻译器。如果为 None，我们将跳过翻译。默认为 None。

    返回:
        str: 过滤后的文本。
    """
    if ignore_asterisks:
        try:
            text = filter_asterisks(text)
        except Exception as e:
            logger.warning(f"Error ignoring asterisks: {e}")
            logger.warning(f"Text: {text}")
            logger.warning("Skipping...")

    if ignore_brackets:
        try:
            text = filter_brackets(text)
        except Exception as e:
            logger.warning(f"Error ignoring brackets: {e}")
            logger.warning(f"Text: {text}")
            logger.warning("Skipping...")
    if ignore_parentheses:
        try:
            text = filter_parentheses(text)
        except Exception as e:
            logger.warning(f"Error ignoring parentheses: {e}")
            logger.warning(f"Text: {text}")
            logger.warning("Skipping...")
    if ignore_angle_brackets:
        try:
            text = filter_angle_brackets(text)
        except Exception as e:
            logger.warning(f"Error ignoring angle brackets: {e}")
            logger.warning(f"Text: {text}")
            logger.warning("Skipping...")
    if remove_special_char:
        try:
            text = remove_special_characters(text)
        except Exception as e:
            logger.warning(f"Error removing special characters: {e}")
            logger.warning(f"Text: {text}")
            logger.warning("Skipping...")
    if translator:
        try:
            logger.info("Translating...")
            text = translator.translate(text)
            logger.info(f"Translated: {text}")
        except Exception as e:
            logger.critical(f"Error translating: {e}")
            logger.critical(f"Text: {text}")
            logger.warning("Skipping...")

    logger.debug(f"Filtered text: {text}")
    return text


def remove_special_characters(text: str) -> str:
    """
    过滤文本以删除所有非字母、非数字和非标点字符。

    参数:
        text (str): 要过滤的文本。

    返回:
        str: 过滤后的文本。
    """
    normalized_text = unicodedata.normalize("NFKC", text)

    def is_valid_char(char: str) -> bool:
        category = unicodedata.category(char)
        return (
            category.startswith("L")
            or category.startswith("N")
            or category.startswith("P")
            or char.isspace()
        )

    filtered_text = "".join(char for char in normalized_text if is_valid_char(char))
    return filtered_text


def _filter_nested(text: str, left: str, right: str) -> str:
    """
    处理嵌套符号的通用函数。

    参数:
        text (str): 要过滤的文本。
        left (str): 左侧符号（例如 '[' 或 '('）。
        right (str): 右侧符号（例如 ']' 或 ')'）。

    返回:
        str: 过滤后的文本。
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    if not text:
        return text

    result = []
    depth = 0
    for char in text:
        if char == left:
            depth += 1
        elif char == right:
            if depth > 0:
                depth -= 1
        else:
            if depth == 0:
                result.append(char)
    filtered_text = "".join(result)
    filtered_text = re.sub(r"\s+", " ", filtered_text).strip()
    return filtered_text


def filter_brackets(text: str) -> str:
    """
    过滤文本以删除方括号内的所有文本，处理嵌套情况。

    参数:
        text (str): 要过滤的文本。

    返回:
        str: 过滤后的文本。
    """
    return _filter_nested(text, "[", "]")


def filter_parentheses(text: str) -> str:
    """
    过滤文本以删除圆括号内的所有文本，处理嵌套情况。

    参数:
        text (str): 要过滤的文本。

    返回:
        str: 过滤后的文本。
    """
    return _filter_nested(text, "(", ")")


def filter_angle_brackets(text: str) -> str:
    """
    过滤文本以删除尖括号内的所有文本，处理嵌套情况。

    参数:
        text (str): 要过滤的文本。

    返回:
        str: 过滤后的文本。
    """
    return _filter_nested(text, "<", ">")


def filter_asterisks(text: str) -> str:
    """
    从字符串中删除任意长度星号（*、**、***等）包围的文本。

    参数:
        text: 输入字符串。

    返回:
        删除星号包围文本后的字符串。
    """
    # Handle asterisks of any length (*, **, ***, etc.)
    filtered_text = re.sub(r"\*{1,}((?!\*).)*?\*{1,}", "", text)

    # Clean up any extra spaces
    filtered_text = re.sub(r"\s+", " ", filtered_text).strip()

    return filtered_text

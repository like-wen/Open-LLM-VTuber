import json
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger


class StreamJSONDetector:
    """流式文本中实时 JSON 检测器。"""

    def __init__(self):
        self.buffer = ""  # Store text that has not been fully processed
        self.potential_jsons = []  # Store possible JSON starting positions
        self.completed_jsons = []  # Store completed JSON objects
        self.processed_ranges = []  # Store processed intervals [start, end]

    def process_chunk(self, chunk: str) -> List[Dict[str, Any]]:
        """处理单个文本块，返回在此块中找到的完整 JSON 对象列表。

        参数:
            chunk (str): 接收到的文本块

        返回:
            List[Dict[str, Any]]: 从当前块解析的完整 JSON 对象列表
        """
        # Add new chunk to buffer
        old_length = len(self.buffer)
        self.buffer += chunk

        # Update potential JSON starting positions
        self._find_potential_starts(old_length)

        # Try to parse potential JSON objects
        new_jsons = self._try_parse_jsons()

        return new_jsons

    def _find_potential_starts(self, start_from: int) -> None:
        """在缓冲区中查找新的潜在 JSON 起始位置。

        参数:
            start_from (int): 开始搜索的位置
        """
        for i in range(start_from, len(self.buffer)):
            if self.buffer[i] == "{" and not self._is_in_processed_range(i):
                self.potential_jsons.append(i)

    def _is_in_processed_range(self, pos: int) -> bool:
        """检查指定位置是否在已处理范围内。

        参数:
            pos (int): 要检查的位置

        返回:
            bool: 如果位置在已处理范围内则为 True，否则为 False
        """
        for start, end in self.processed_ranges:
            if start <= pos <= end:
                return True
        return False

    def _try_parse_jsons(self) -> List[Dict[str, Any]]:
        """尝试从当前缓冲区解析 JSON 对象。

        返回:
            List[Dict[str, Any]]: 新解析的 JSON 对象列表
        """
        new_jsons = []
        remaining_potential = []

        # Sort by starting position, process outermost JSON first
        self.potential_jsons.sort()

        for start_idx in self.potential_jsons:
            # Skip if this position is already within a processed range
            if self._is_in_processed_range(start_idx):
                continue

            result, end_idx = self._extract_json(start_idx)
            if result is not None:
                new_jsons.append(result)
                # Mark this range as processed
                self.processed_ranges.append((start_idx, end_idx))
                self.completed_jsons.append(result)
            else:
                # This JSON may not be complete yet, keep it
                remaining_potential.append(start_idx)

        self.potential_jsons = remaining_potential
        return new_jsons

    def _extract_json(self, start_idx: int) -> Tuple[Optional[Dict[str, Any]], int]:
        """尝试从给定位置提取完整的 JSON 对象。

        参数:
            start_idx (int): JSON 的潜在起始位置

        返回:
            Tuple[Optional[Dict[str, Any]], int]: 解析的 JSON 对象和结束位置，
                                               或者如果不完整则为 (None, -1)
        """
        stack = 1
        i = start_idx + 1

        while i < len(self.buffer) and stack > 0:
            if self.buffer[i] == "{":
                stack += 1
            elif self.buffer[i] == "}":
                stack -= 1
            i += 1

        # If complete JSON is found
        if stack == 0:
            json_str = self.buffer[start_idx:i]
            try:
                json_data = json.loads(json_str)
                return json_data, i - 1
            except json.JSONDecodeError:
                logger.warning(
                    f"JSON structure found but parsing failed: {json_str[:50]}..."
                )

        return None, -1

    def get_all_jsons(self) -> List[Dict[str, Any]]:
        """获取到目前为止解析的所有 JSON 对象。

        返回:
            List[Dict[str, Any]]: 所有解析的 JSON 对象列表
        """
        return self.completed_jsons

    def reset(self) -> None:
        """重置检测器状态，准备处理新流。"""
        self.buffer = ""
        self.potential_jsons = []
        self.completed_jsons = []
        self.processed_ranges = []


# Usage example
if __name__ == "__main__":
    # Simulate streaming text reception
    test_chunks = [
        "This is some plain text ",
        "Here comes JSON: {",
        '"name": "test", "values": [1, 2, ',
        '3]} This is text after JSON {"another": "json", ',
        '"nested": {"key": "value"}}',
    ]

    detector = StreamJSONDetector()

    for i, chunk in enumerate(test_chunks):
        logger.info(f"Processing chunk {i + 1}: {chunk}")
        new_jsons = detector.process_chunk(chunk)
        if new_jsons:
            logger.info(f"Complete JSON found in this chunk: {new_jsons}")

    logger.info(f"All detected JSONs: {detector.get_all_jsons()}")

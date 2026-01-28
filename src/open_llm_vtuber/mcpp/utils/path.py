"""Path utilities."""

from pathlib import Path
from loguru import logger


def validate_file(file_path: str | Path, suffix: str = ".json") -> Path:
    """检查文件路径是否有效。

    参数:
        file_path (str | Path): 文件路径。
        suffix (str): 期望的文件扩展名。默认为 '.json'。

    返回:
        Path: 如果有效则返回文件的绝对路径对象。

    异常:
        ValueError: 如果文件路径对于给定的后缀无效。
    """
    file_path = Path(file_path).absolute()
    if file_path.exists() and file_path.is_file() and file_path.suffix == suffix:
        return file_path
    logger.error(f"File '{file_path}' not a valid '{suffix}' file.")
    raise ValueError(f"File '{file_path}' not a valid '{suffix}' file.")

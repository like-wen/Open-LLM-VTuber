# config_manager/utils.py
import yaml
from pathlib import Path
from typing import Union, Dict, Any, TypeVar
from pydantic import BaseModel, ValidationError
import os
import re
import chardet
from loguru import logger

from .main import Config

T = TypeVar("T", bound=BaseModel)


def read_yaml(config_path: str) -> Dict[str, Any]:
    """
    读取指定的 YAML 配置文件，支持环境变量替换和编码猜测。将配置数据作为字典返回。

    参数:
        config_path: YAML 配置文件的路径。

    返回:
        配置数据作为字典。

    抛出:
        FileNotFoundError: 如果配置文件不存在。
        IOError: 如果无法读取配置文件。
    """

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    content = load_text_file_with_guess_encoding(config_path)
    if not content:
        raise IOError(f"Failed to read configuration file: {config_path}")

    # Replace environment variables
    pattern = re.compile(r"\$\{(\w+)\}")

    def replacer(match):
        env_var = match.group(1)
        return os.getenv(env_var, match.group(0))

    content = pattern.sub(replacer, content)

    try:
        return yaml.safe_load(content)
    except yaml.YAMLError as e:
        logger.critical(f"Error parsing YAML file: {e}")
        raise e


def validate_config(config_data: dict) -> Config:
    """
    根据 Config 模型验证配置数据。

    参数:
        config_data: 要验证的配置数据。

    返回:
        验证后的 Config 对象。

    抛出:
        ValidationError: 如果配置验证失败。
    """
    try:
        return Config(**config_data)
    except ValidationError as e:
        logger.critical(f"Error validating configuration: {e}")
        logger.error("Configuration data:")
        logger.error(config_data)
        raise e


def load_text_file_with_guess_encoding(file_path: str) -> str | None:
    """
    加载具有猜测编码的文本文件。

    参数:
    - file_path (str): 文本文件的路径。

    返回:
    - str: 文本文件的内容，如果发生错误则返回 None。
    """
    encodings = ["utf-8", "utf-8-sig", "gbk", "gb2312", "ascii", "cp936"]

    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as file:
                return file.read()
        except UnicodeDecodeError:
            continue
    # If common encodings fail, try chardet to guess the encoding
    try:
        with open(file_path, "rb") as file:
            raw_data = file.read()
        detected = chardet.detect(raw_data)
        if detected["encoding"]:
            return raw_data.decode(detected["encoding"])
    except Exception as e:
        logger.error(f"Error detecting encoding for config file {file_path}: {e}")
    return None


def save_config(config: BaseModel, config_path: Union[str, Path]):
    """
    将 Pydantic 模型保存到 YAML 配置文件。

    参数:
        config: 要保存的 Pydantic 模型。
        config_path: YAML 配置文件的路径。
    """
    config_file = Path(config_path)
    config_data = config.model_dump(
        by_alias=True, exclude_unset=True, exclude_none=True
    )

    try:
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f, allow_unicode=True)
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error writing YAML file: {e}")


def scan_config_alts_directory(config_alts_dir: str) -> list[dict]:
    """
    扫描 config_alts 目录并返回配置信息列表。
    每个配置信息包含文件名及其从配置中获取的显示名称。

    参数:
    - config_alts_dir (str): config_alts 目录的路径。

    返回:
    - list[dict]: 包含配置信息的字典列表:
        - filename: 实际的配置文件名
        - name: 从配置中获取的显示名称，如果未指定则回退到文件名
    """
    config_files = []

    # Add default config first
    default_config = read_yaml("conf.yaml")
    config_files.append(
        {
            "filename": "conf.yaml",
            "name": default_config.get("character_config", {}).get(
                "conf_name", "conf.yaml"
            )
            if default_config
            else "conf.yaml",
        }
    )

    # Scan other configs
    for root, _, files in os.walk(config_alts_dir):
        for file in files:
            if file.endswith(".yaml"):
                config: dict = read_yaml(os.path.join(root, file))
                config_files.append(
                    {
                        "filename": file,
                        "name": config.get("character_config", {}).get(
                            "conf_name", file
                        )
                        if config
                        else file,
                    }
                )
    logger.debug(f"Found config files: {config_files}")
    return config_files


def scan_bg_directory() -> list[str]:
    bg_files = []
    bg_dir = "backgrounds"
    for root, _, files in os.walk(bg_dir):
        for file in files:
            if file.endswith((".jpg", ".jpeg", ".png", ".gif")):
                bg_files.append(file)
    return bg_files

import abc
import os
import asyncio

from loguru import logger


class TTSInterface(metaclass=abc.ABCMeta):
    async def async_generate_audio(self, text: str, file_name_no_ext=None) -> str:
        """
        使用 TTS 异步生成语音音频文件。

        默认情况下，此方法在协程中运行同步的 generate_audio。
        子类可以重写此方法以提供真正的异步实现。

        text: str
            要朗读的文本
        file_name_no_ext (可选且已弃用): str
            不带文件扩展名的文件名

        返回:
        str: 生成的音频文件的路径

        """
        return await asyncio.to_thread(self.generate_audio, text, file_name_no_ext)

    @abc.abstractmethod
    def generate_audio(self, text: str, file_name_no_ext=None) -> str:
        """
        使用 TTS 生成语音音频文件。
        text: str
            要朗读的文本
        file_name_no_ext (可选且已弃用): str
            不带文件扩展名的文件名

        返回:
        str: 生成的音频文件的路径

        """
        raise NotImplementedError

    def remove_file(self, filepath: str, verbose: bool = True) -> None:
        """
        从文件系统中删除文件。

        这是一个单独的方法，而不是 `play_audio_file_local()` 的一部分，因为 `play_audio_file_local()` 不是播放音频文件的唯一方式。此方法将用于在音频文件播放后删除它。

        参数:
            filepath (str): 要删除的文件的路径。
            verbose (bool): 如果为 True，则向控制台打印消息。
        """
        if not os.path.exists(filepath):
            logger.warning(f"文件 {filepath} 不存在")
            return
        try:
            logger.debug(f"删除文件 {filepath}") if verbose else None
            os.remove(filepath)
        except Exception as e:
            logger.error(f"删除文件 {filepath} 失败: {e}")

    def generate_cache_file_name(self, file_name_no_ext=None, file_extension="wav"):
        """
        生成跨平台的缓存文件名。

        file_name_no_ext: str
            不带扩展名的文件名
        file_extension: str
            文件扩展名

        返回:
        str: 生成的缓存文件的路径
        """
        cache_dir = "cache"
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        if file_name_no_ext is None:
            file_name_no_ext = "temp"

        file_name = f"{file_name_no_ext}.{file_extension}"
        return os.path.join(cache_dir, file_name)

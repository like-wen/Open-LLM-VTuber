import abc
import numpy as np
import asyncio


class ASRInterface(metaclass=abc.ABCMeta):
    SAMPLE_RATE = 16000
    NUM_CHANNELS = 1
    SAMPLE_WIDTH = 2

    async def async_transcribe_np(self, audio: np.ndarray) -> str:
        """异步转录 numpy 数组格式的语音音频。

        默认情况下，此方法在协程中运行同步的 transcribe_np。
        子类可以重写此方法以提供真正的异步实现。

        参数:
            audio: 要转录的音频数据的 numpy 数组。

        返回:
            str: 转录结果。
        """
        if audio.dtype != np.float32:
            audio = audio.astype(np.float32)
        return await asyncio.to_thread(self.transcribe_np, audio)

    @abc.abstractmethod
    def transcribe_np(self, audio: np.ndarray) -> str:
        """转录 numpy 数组格式的语音音频并返回转录结果。

        参数:
            audio: 要转录的音频数据的 numpy 数组。
        """
        raise NotImplementedError

    def nparray_to_audio_file(
        self, audio: np.ndarray, sample_rate: int, file_path: str
    ) -> None:
        """将音频数据的 numpy 数组转换为 .wav 文件。

        参数:
            audio: 音频数据的 numpy 数组。
            sample_rate: 音频数据的采样率。
            file_path: 保存 .wav 文件的路径。
        """
        import wave

        # 确保音频在 [-1, 1] 范围内
        audio = np.clip(audio, -1, 1)
        # 将音频转换为 16 位 PCM
        audio_integer = (audio * 32767).astype(np.int16)

        with wave.open(file_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_integer.tobytes())

from __future__ import annotations

# src/open_llm_vtuber/tts/cartesia_tts.py
from pathlib import Path
from typing import Literal
import os

from loguru import logger
from open_llm_vtuber.config_manager.tts import CartesiaEmotions, CartesiaLanguages
from .tts_interface import TTSInterface

try:
    from cartesia import (
        Cartesia,
        OutputFormat_Mp3Params,
        OutputFormat_WavParams,
    )

    CARTESIA_AVAILABLE = True
except ImportError:
    CARTESIA_AVAILABLE = False
    logger.warning("cartesia not installed. Run: uv add cartesia")


CartesiaModels = Literal[
    "sonic-3", "sonic-2", "sonic-turbo", "sonic-multilingual", "sonic"
]


wav_output_format: OutputFormat_WavParams = {
    "container": "wav",
    "sample_rate": 44100,
    "encoding": "pcm_f32le",
}
mp3_output_format: OutputFormat_Mp3Params = {
    "container": "mp3",
    "sample_rate": 44100,
    "bit_rate": 128000,
}


class TTSEngine(TTSInterface):
    """
    使用 Cartesia TTS API 生成语音。
    API 参考: https://docs.cartesia.ai/use-an-sdk/python
    """

    def __init__(
        self,
        api_key: str,
        voice_id: str = "6ccbfb76-1fc6-48f7-b71d-91ac6298247b",
        model_id: CartesiaModels = "sonic-3",
        output_format: Literal["wav", "mp3"] = "wav",
        language: CartesiaLanguages = "en",
        emotion: CartesiaEmotions = "neutral",
        volume: float = 1.0,
        speed: float = 1.0,
    ):
        """
        初始化 Cartesia TTS 引擎。

        参数:
            api_key (str): Cartesia 服务的 API 密钥。
            voice_id (str): 来自 Cartesia 的语音 ID (例如，6ccbfb76-1fc6-48f7-b71d-91ac6298247b)。
            model_id (str): Cartesia 的模型 ID (例如，sonic-3)。
            language (CartesiaLanguages): 给定语音应说的语言 (例如，en)。
            volume (int): 生成的音量，范围从 0.5 到 2.0 (例如，1)。
            speed (int): 生成的速度，范围从 0.6 到 1.5 (例如，1)。
            emotion (CartesiaEmotions): 生成的情感指导 (例如，neutral)。
            output_format (str): 输出音频格式 (例如，mp3)。
        """
        if not CARTESIA_AVAILABLE:
            raise ImportError(
                "cartesia is required. Install with: pip install cartesia"
            )

        self.api_key = api_key
        self.voice_id = voice_id
        self.model_id = model_id
        self.output_format = output_format
        self.language = language
        self.emotion = emotion
        self.volume = volume
        self.speed = speed

        try:
            self.client = Cartesia(api_key=self.api_key)
            logger.info("Cartesia TTS Engine initialized successfully")
        except Exception as e:
            logger.critical(f"Failed to initialize Cartesia client: {e}")
            self.client = None
            raise e

    def generate_audio(self, text: str, file_name_no_ext: str | None = None) -> str:
        """
        使用 Cartesia TTS 生成语音音频文件。

        参数:
            text (str): 要合成的文本。
            file_name_no_ext (str, optional): 不带扩展名的文件名。默认为生成的名称。

        返回:
            str: 生成的音频文件的路径，如果生成失败则返回 None。
        """
        if not self.client:
            logger.error("Cartesia client not initialized. Cannot generate audio.")
            return "Cartesia client not initialized. Cannot generate audio."
        # Use the configured file extension
        file_name = self.generate_cache_file_name(file_name_no_ext, self.output_format)
        speech_file_path = Path(file_name)
        output_format = (
            wav_output_format if self.output_format == "wav" else mp3_output_format
        )
        try:
            logger.debug(
                f"Generating audio via Cartesia for text: '{text[:50]}...' with voice '{self.voice_id}' model '{self.model_id}'"
            )
            audio = self.client.tts.bytes(
                output_format=output_format,
                model_id=self.model_id,
                transcript=text,
                language=self.language,
                generation_config={
                    "volume": self.volume,
                    "speed": self.speed,
                    "emotion": self.emotion,
                },
                voice={
                    "mode": "id",
                    "id": self.voice_id,
                },
            )

            with open(speech_file_path, "wb") as f:
                for chunk in audio:
                    f.write(chunk)

            logger.info(
                f"Successfully generated audio file via Cartesia: {speech_file_path}"
            )
        except Exception as e:
            logger.critical(f"Error: Cartesia TTS unable to generate audio: {e}")
            # Clean up potentially incomplete file
            if speech_file_path.exists():
                try:
                    os.remove(speech_file_path)
                except OSError as rm_err:
                    logger.error(
                        f"Could not remove incomplete file {speech_file_path}: {rm_err}"
                    )
            raise e

        return str(speech_file_path)


# Code Used to Test Cartesia TTS Engine
# if __name__ == "__main__":
#     tts_engine = TTSEngine()
#     test_text = "Hello world! This is a test using Cartesia."
#     audio_path = tts_engine.generate_audio(test_text, "cartesia_test")
#     if audio_path:
#         print(f"Generated audio saved to: {audio_path}")
#     else:
#         print("Failed to generate audio.")

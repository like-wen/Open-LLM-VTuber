# src/open_llm_vtuber/tts/openai_tts.py
import os
import sys
from pathlib import Path

from loguru import logger
from openai import OpenAI  # Use the official OpenAI library

from .tts_interface import TTSInterface

# Add the current directory to sys.path for relative imports if needed
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)


class TTSEngine(TTSInterface):
    """
    使用与 OpenAI 兼容的 TTS API 端点生成语音。
    连接到由 `base_url` 指定的服务器。
    API 参考: https://platform.openai.com/docs/api-reference/audio/createSpeech (用于标准参数)
    """

    def __init__(
        self,
        model="kokoro",  # Default model based on user example
        voice="af_sky+af_bella",  # Default voice based on user example
        api_key="not-needed",  # Default for local/compatible servers that don't require auth
        base_url="http://localhost:8880/v1",  # Default to the specified endpoint
        file_extension: str = "mp3",  # Configurable file extension
        **kwargs,  # Allow passing additional args to OpenAI client
    ):
        """
        初始化 OpenAI TTS 引擎。

        参数:
            model (str): 要使用的 TTS 模型（例如，'tts-1', 'tts-1-hd'）。
            voice (str): 要使用的语音（例如，'alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'）。
            api_key (str, optional): TTS 服务的 API 密钥。默认为 "not-needed"。
            base_url (str, optional): 与 OpenAI 兼容的 TTS 端点的基本 URL。默认为 "http://localhost:8880/v1"。
        """
        self.model = model
        self.voice = voice
        self.file_extension = file_extension.lower()  # Use configured extension
        if self.file_extension not in ["mp3", "wav"]:
            logger.warning(
                f"Unsupported file extension '{self.file_extension}' configured for OpenAI TTS. Defaulting to 'mp3'."
            )
            self.file_extension = "mp3"
        self.new_audio_dir = "cache"
        self.temp_audio_file = "temp_openai"  # Use a different temp name

        if not os.path.exists(self.new_audio_dir):
            os.makedirs(self.new_audio_dir)

        try:
            # Initialize OpenAI client
            self.client = OpenAI(api_key=api_key, base_url=base_url, **kwargs)
            logger.info(
                f"OpenAI-compatible TTS Engine initialized, targeting endpoint: {base_url}"
            )
        except Exception as e:
            logger.critical(f"Failed to initialize OpenAI client: {e}")
            self.client = None  # Ensure client is None if init fails

    def generate_audio(self, text, file_name_no_ext=None, speed=1.0):
        """
        使用 OpenAI TTS 生成语音音频文件。

        参数:
            text (str): 要合成的文本。
            file_name_no_ext (str, optional): 不带扩展名的文件名。默认为生成的名称。
            speed (float): 语音的速度（0.25 到 4.0）。默认为 1.0。

        返回:
            str: 生成的音频文件的路径，如果生成失败则返回 None。
        """
        if not self.client:
            logger.error("OpenAI client not initialized. Cannot generate audio.")
            return None

        # Use the configured file extension
        file_name = self.generate_cache_file_name(file_name_no_ext, self.file_extension)
        speech_file_path = Path(file_name)

        try:
            logger.debug(
                f"Generating audio via {self.client.base_url} for text: '{text[:50]}...' with voice '{self.voice}' model '{self.model}'"
            )
            # Use with_streaming_response for potentially better handling of large audio files or network issues
            with (
                self.client.audio.speech.with_streaming_response.create(
                    model=self.model,  # Model name expected by the compatible server (e.g., "kokoro")
                    voice=self.voice,  # Voice name(s) expected by the compatible server (e.g., "af_sky+af_bella")
                    input=text,
                    response_format=self.file_extension,  # Use configured extension
                    speed=speed,
                ) as response
            ):
                # Stream the audio content to the file
                response.stream_to_file(speech_file_path)

            logger.info(
                f"Successfully generated audio file via compatible endpoint: {speech_file_path}"
            )

        except Exception as e:
            logger.critical(f"Error: OpenAI TTS unable to generate audio: {e}")
            # Clean up potentially incomplete file
            if speech_file_path.exists():
                try:
                    os.remove(speech_file_path)
                except OSError as rm_err:
                    logger.error(
                        f"Could not remove incomplete file {speech_file_path}: {rm_err}"
                    )
            return None

        return str(speech_file_path)


# Example usage (optional, for testing with the compatible endpoint)
# if __name__ == '__main__':
#     # Configure TTSEngine to use the specific model and voice from the example
#     # The base_url and api_key will use the defaults set in __init__
#     tts_engine = TTSEngine(model="kokoro", voice="af_sky+af_bella")
#     test_text = "Hello world! This is a test using the compatible endpoint."
#     audio_path = tts_engine.generate_audio(test_text, "compatible_endpoint_test")
#     if audio_path:
#         print(f"Generated audio saved to: {audio_path}")
#     else:
#         print("Failed to generate audio.")

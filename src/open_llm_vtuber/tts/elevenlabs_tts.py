# src/open_llm_vtuber/tts/elevenlabs_tts.py
import os
from pathlib import Path

from loguru import logger
from elevenlabs.client import ElevenLabs

from .tts_interface import TTSInterface


class TTSEngine(TTSInterface):
    """
    使用 ElevenLabs TTS API 生成语音。
    API 参考: https://elevenlabs.io/docs/api-reference/text-to-speech
    """

    def __init__(
        self,
        api_key: str,
        voice_id: str,
        model_id: str = "eleven_multilingual_v2",
        output_format: str = "mp3_44100_128",
        stability: float = 0.5,
        similarity_boost: float = 0.5,
        style: float = 0.0,
        use_speaker_boost: bool = True,
    ):
        """
        初始化 ElevenLabs TTS 引擎。

        参数:
            api_key (str): ElevenLabs 服务的 API 密钥。
            voice_id (str): 来自 ElevenLabs 的语音 ID (例如，JBFqnCBsd6RMkjVDRZzb)。
            model_id (str): ElevenLabs 的模型 ID (例如，eleven_multilingual_v2)。
            output_format (str): 输出音频格式 (例如，mp3_44100_128)。
            stability (float): 语音稳定性 (0.0 到 1.0)。
            similarity_boost (float): 语音相似度增强 (0.0 到 1.0)。
            style (float): 语音风格夸张程度 (0.0 到 1.0)。
            use_speaker_boost (bool): 为更好质量启用扬声器增强。
        """
        self.api_key = api_key
        self.voice_id = voice_id
        self.model_id = model_id
        self.output_format = output_format
        self.stability = stability
        self.similarity_boost = similarity_boost
        self.style = style
        self.use_speaker_boost = use_speaker_boost

        # Determine file extension from output format
        if "mp3" in output_format:
            self.file_extension = "mp3"
        elif "pcm" in output_format:
            self.file_extension = "wav"
        else:
            logger.warning(
                f"Unknown output format '{output_format}', defaulting to mp3 extension."
            )
            self.file_extension = "mp3"  # Default to mp3

        try:
            # Initialize ElevenLabs client
            self.client = ElevenLabs(api_key=api_key)
            logger.info("ElevenLabs TTS Engine initialized successfully")
        except Exception as e:
            logger.critical(f"Failed to initialize ElevenLabs client: {e}")
            self.client = None
            raise e

    def generate_audio(
        self, text: str, file_name_no_ext: str | None = None
    ) -> str | None:
        """
        使用 ElevenLabs TTS 生成语音音频文件。

        参数:
            text (str): 要合成的文本。
            file_name_no_ext (str, optional): 不带扩展名的文件名。默认为生成的名称。

        返回:
            str: 生成的音频文件的路径，如果生成失败则返回 None。
        """
        if not self.client:
            logger.error("ElevenLabs client not initialized. Cannot generate audio.")
            return None

        # Use the configured file extension
        file_name = self.generate_cache_file_name(file_name_no_ext, self.file_extension)
        speech_file_path = Path(file_name)

        try:
            logger.debug(
                f"Generating audio via ElevenLabs for text: '{text[:50]}...' with voice '{self.voice_id}' model '{self.model_id}'"
            )

            # Generate audio using ElevenLabs API
            audio = self.client.text_to_speech.convert(
                text=text,
                voice_id=self.voice_id,
                model_id=self.model_id,
                output_format=self.output_format,
                voice_settings={
                    "stability": self.stability,
                    "similarity_boost": self.similarity_boost,
                    "style": self.style,
                    "use_speaker_boost": self.use_speaker_boost,
                },
            )

            # Write the audio data to file
            with open(speech_file_path, "wb") as f:
                for chunk in audio:
                    f.write(chunk)

            logger.info(
                f"Successfully generated audio file via ElevenLabs: {speech_file_path}"
            )

        except Exception as e:
            logger.critical(f"Error: ElevenLabs TTS unable to generate audio: {e}")
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


# Example usage (optional, for testing)
# if __name__ == '__main__':
#     tts_engine = TTSEngine(
#         api_key="your_api_key",
#         voice_id="JBFqnCBsd6RMkjVDRZzb",
#         model_id="eleven_multilingual_v2"
#     )
#     test_text = "Hello world! This is a test using ElevenLabs."
#     audio_path = tts_engine.generate_audio(test_text, "elevenlabs_test")
#     if audio_path:
#         print(f"Generated audio saved to: {audio_path}")
#     else:
#         print("Failed to generate audio.")

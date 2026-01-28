import os
from typing import Optional
from TTS.api import TTS
from loguru import logger
import torch
from .tts_interface import TTSInterface


class TTSEngine(TTSInterface):
    """
    支持单说话人和多说话人模式的 CoquiTTS 引擎实现。
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        speaker_wav: Optional[str] = None,
        language: Optional[str] = "en",
        device: Optional[str] = None,
    ):
        """
        初始化 CoquiTTS 引擎。

        参数:
            model_name: 要使用的 TTS 模型名称。如果为 None，则使用默认模型。
            speaker_wav: 用于声音克隆的说话人 wav 文件路径。仅在多说话人模式下使用。
            language: 多语言模型的语言代码。默认为 "en"。
            device: 运行模型的设备（"cuda"、"cpu" 等）。如果为 None，则自动检测。
        """
        # Auto-detect device if not specified
        if device:
            self.device = device
        else:
            logger.info("coqui_tts: Using default device")
            self.device = "cuda" if torch.cuda.is_available() else "cpu"

        logger.info(f"coqui_tts: Using device: {device}")

        try:
            # Initialize TTS model
            if model_name:
                self.tts = TTS(model_name=model_name).to(self.device)
            else:
                # Use default model if none specified
                self.tts = TTS().to(self.device)

            self.speaker_wav = speaker_wav
            self.language = language

            # Check if model is multi-speaker
            self.is_multi_speaker = (
                hasattr(self.tts, "speakers") and self.tts.speakers is not None
            )

        except Exception as e:
            raise RuntimeError(f"Failed to initialize CoquiTTS model: {str(e)}")

    def generate_audio(self, text: str, file_name_no_ext: Optional[str] = None) -> str:
        """
        使用 CoquiTTS 生成语音音频文件。

        参数:
            text: 要合成的文本
            file_name_no_ext: 不带扩展名的输出文件名（可选）

        返回:
            生成的音频文件的路径
        """
        try:
            # Generate output path
            output_path = self.generate_cache_file_name(file_name_no_ext, "wav")

            # Generate speech based on speaker mode
            if self.is_multi_speaker and self.speaker_wav:
                # Multi-speaker mode with voice cloning
                self.tts.tts_to_file(
                    text=text,
                    speaker_wav=self.speaker_wav,
                    language=self.language,
                    file_path=output_path,
                )
            else:
                # Single speaker mode
                self.tts.tts_to_file(text=text, file_path=output_path)

            if not os.path.exists(output_path):
                raise FileNotFoundError(
                    f"Failed to generate audio file at {output_path}"
                )

            return output_path

        except Exception as e:
            raise RuntimeError(f"Failed to generate audio: {str(e)}")

    @staticmethod
    def list_available_models() -> list:
        """
        列出所有可用的 CoquiTTS 模型。

        返回:
            可用模型名称列表
        """
        try:
            return TTS().list_models()
        except Exception as e:
            raise RuntimeError(f"Failed to list available models: {str(e)}")

    def get_speaker_info(self) -> dict:
        """
        获取关于多说话人模型的可用说话人的信息。

        返回:
            包含说话人信息的字典
        """
        if not self.is_multi_speaker:
            return {"multi_speaker": False}

        try:
            return {
                "multi_speaker": True,
                "speakers": self.tts.speakers,
                "languages": self.tts.languages
                if hasattr(self.tts, "languages")
                else None,
            }
        except Exception as e:
            raise RuntimeError(f"Failed to get speaker information: {str(e)}")

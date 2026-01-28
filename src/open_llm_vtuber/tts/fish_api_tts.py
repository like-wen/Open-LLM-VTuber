from typing import Literal
from fish_audio_sdk import Session, TTSRequest
from loguru import logger
from .tts_interface import TTSInterface


class TTSEngine(TTSInterface):
    """
    调用 FishTTS API 服务的 Fish TTS。
    """

    file_extension: str = "wav"

    def __init__(
        self,
        api_key: str,
        reference_id="7f92f8afb8ec43bf81429cc1c9199cb1",
        latency: Literal["normal", "balanced"] = "balanced",
        base_url="https://api.fish.audio",
    ):
        """
        初始化 Fish TTS API。

        参数:
            api_key (str): Fish TTS API 的 API 密钥。

            reference_id (str): 要使用的语音的参考 ID。
                在 [Fish Audio 网站](https://fish.audio/) 上获取。

            latency (str): "normal" 或 "balanced"。balance 更快但质量较低。

            base_url (str): Fish TTS API 的基础 URL。

        """

        logger.info(
            f"\nFish TTS API initialized with api key: {api_key} baseurl: {base_url} reference_id: {reference_id}, latency: {latency}"
        )

        self.reference_id = reference_id
        self.latency = latency
        self.session = Session(apikey=api_key, base_url=base_url)

    def generate_audio(self, text, file_name_no_ext=None):
        file_name = self.generate_cache_file_name(file_name_no_ext, self.file_extension)

        try:
            with open(file_name, "wb") as f:
                for chunk in self.session.tts(
                    TTSRequest(
                        text=text, reference_id=self.reference_id, latency=self.latency
                    )
                ):
                    f.write(chunk)

        except Exception as e:
            logger.critical(f"\nError: Fish TTS API fail to generate audio: {e}")
            return None

        return file_name

from abc import ABC, abstractmethod


class VADInterface(ABC):
    @abstractmethod
    def detect_speech(self, audio_data: bytes):
        """
        检测音频数据中是否有人声活动。
        :param audio_data: 输入音频数据
        :return: 如果检测到人声活动，返回包含人类语音的音频字节序列
        """
        pass

import base64
from pydub import AudioSegment
from pydub.utils import make_chunks
from ..agent.output_types import Actions
from ..agent.output_types import DisplayText


def _get_volume_by_chunks(audio: AudioSegment, chunk_length_ms: int) -> list:
    """
    计算音频每个块的归一化音量（RMS）。

    参数:
        audio (AudioSegment): 要处理的音频段。
        chunk_length_ms (int): 每个音频块的长度（以毫秒为单位）。

    返回:
        list: 每个块的归一化音量。
    """
    chunks = make_chunks(audio, chunk_length_ms)
    volumes = [chunk.rms for chunk in chunks]
    max_volume = max(volumes)
    if max_volume == 0:
        raise ValueError("Audio is empty or all zero.")
    return [volume / max_volume for volume in volumes]


def prepare_audio_payload(
    audio_path: str | None,
    chunk_length_ms: int = 20,
    display_text: DisplayText = None,
    actions: Actions = None,
    forwarded: bool = False,
) -> dict[str, any]:
    """
    准备发送到广播端点的音频载荷。
    如果 audio_path 为 None，则返回一个 audio=None 的载荷用于静默显示。

    参数:
        audio_path (str | None): 要处理的音频文件路径，或者为 None 以进行静默显示
        chunk_length_ms (int): 每个音频块的长度（以毫秒为单位）
        display_text (DisplayText, optional): 与音频一起显示的文本
        actions (Actions, optional): 与音频相关的操作

    返回:
        dict: 要发送的音频载荷
    """
    if isinstance(display_text, DisplayText):
        display_text = display_text.to_dict()

    if not audio_path:
        # Return payload for silent display
        return {
            "type": "audio",
            "audio": None,
            "volumes": [],
            "slice_length": chunk_length_ms,
            "display_text": display_text,
            "actions": actions.to_dict() if actions else None,
            "forwarded": forwarded,
        }

    try:
        audio = AudioSegment.from_file(audio_path)
        audio_bytes = audio.export(format="wav").read()
    except Exception as e:
        raise ValueError(
            f"Error loading or converting generated audio file to wav file '{audio_path}': {e}"
        )
    audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
    volumes = _get_volume_by_chunks(audio, chunk_length_ms)

    payload = {
        "type": "audio",
        "audio": audio_base64,
        "volumes": volumes,
        "slice_length": chunk_length_ms,
        "display_text": display_text,
        "actions": actions.to_dict() if actions else None,
        "forwarded": forwarded,
    }

    return payload


# Example usage:
# payload, duration = prepare_audio_payload("path/to/audio.mp3", display_text="Hello", expression_list=[0,1,2])

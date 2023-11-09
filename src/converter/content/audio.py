import math

import ffmpeg

from content import SourceContent
from converter.schemas import Process
from style import AudioSystem, TimeUnit
from utils import VSMLManager


def create_audio_process(
    vsml_content: SourceContent,
    debug_mode: bool = False,
) -> Process:
    # sourceの取得
    audio_process = ffmpeg.input(vsml_content.src_path).audio

    style = vsml_content.style
    # audioのstyle対応
    if style.source_audio_system == AudioSystem.MONAURAL:
        audio_process = ffmpeg.filter(
            [audio_process, audio_process], "amerge", inputs=2
        )
    if (
        style.source_audio_system == AudioSystem.STEREO
        and style.audio_system == AudioSystem.MONAURAL
    ):
        # 一度MONAURALにマージした上で、他の音声との操作のためにSTEREOに複製する
        audio_process = ffmpeg.filter(audio_process, "amerge", inputs=1)
        audio_process = ffmpeg.filter(
            [audio_process, audio_process], "amerge", inputs=2
        )

    if style.audio_volume != 100:
        decibel = 20 * math.log10(style.audio_volume / 100)
        audio_process = ffmpeg.filter(
            audio_process, "volume", "{}dB".format(decibel)
        )

    # timeのstyle対応
    if style.object_length.unit in [TimeUnit.FRAME, TimeUnit.SECOND]:
        option = {}
        if style.object_length.unit == TimeUnit.FRAME:
            option = {
                "end": style.object_length.value / VSMLManager.get_root_fps()
            }
        if style.object_length.unit == TimeUnit.SECOND:
            option = {"end": style.object_length.value}
        audio_process = ffmpeg.filter(audio_process, "atrim", **option)
    if style.time_padding_start.unit in [TimeUnit.FRAME, TimeUnit.SECOND]:
        option = {}
        if style.time_padding_start.unit == TimeUnit.FRAME:
            option = {
                "delays": style.time_padding_start.value
                / VSMLManager.get_root_fps()
            }
        elif style.time_padding_start.unit == TimeUnit.SECOND:
            option = {"delays": style.time_padding_start.value}
        audio_process = ffmpeg.filter(
            audio_process,
            "adelay",
            all=1,
            **option,
        )
    if style.object_length.unit in [
        TimeUnit.FRAME,
        TimeUnit.SECOND,
    ] and style.time_padding_end.unit in [TimeUnit.FRAME, TimeUnit.SECOND]:
        option = {}
        if style.time_padding_end.unit == TimeUnit.FRAME:
            option = {
                "pad_dur": style.time_padding_end.value
                / VSMLManager.get_root_fps()
            }
        elif style.time_padding_end.unit == TimeUnit.SECOND:
            option = {"pad_dur": style.time_padding_end.value}
        audio_process = ffmpeg.filter(audio_process, "apad", **option)

    # processの作成
    return Process(None, audio_process, vsml_content.style)

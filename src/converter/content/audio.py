import math

import ffmpeg

from content import SourceContent
from converter.schemas import Process
from style import AudioSystem, TimeUnit


def create_audio_process(
    vsml_content: SourceContent,
    debug_mode: bool = False,
) -> Process:
    # sourceの取得
    audio_process = ffmpeg.input(vsml_content.src_path).audio

    # audioのstyle対応
    if vsml_content.style.source_audio_system == AudioSystem.MONAURAL:
        audio_process = ffmpeg.filter(
            [audio_process, audio_process], "amerge", inputs=2
        )
    if (
        vsml_content.style.source_audio_system == AudioSystem.STEREO
        and vsml_content.style.audio_system == AudioSystem.MONAURAL
    ):
        # 一度MONAURALにマージした上で、他の音声との操作のためにSTEREOに複製する
        audio_process = ffmpeg.filter(audio_process, "amerge", inputs=1)
        audio_process = ffmpeg.filter(
            [audio_process, audio_process], "amerge", inputs=2
        )

    if vsml_content.style.audio_volume != 100:
        decibel = 20 * math.log10(vsml_content.style.audio_volume / 100)
        audio_process = ffmpeg.filter(
            audio_process, "volume", "{}dB".format(decibel)
        )

    # timeのstyle対応
    object_length = vsml_content.style.object_length
    match object_length.unit:
        case TimeUnit.FRAME:
            ffmpeg.trim(
                audio_process,
                end_frame=object_length.value + 1,
            )
        case TimeUnit.SECOND:
            ffmpeg.trim(
                audio_process,
                end=object_length.value,
            )
    time_padding_start = vsml_content.style.time_padding_start
    match time_padding_start.unit:
        case TimeUnit.FRAME:
            ffmpeg.filter(
                "tpad",
                audio_process,
                start=time_padding_start.value,
            )
        case TimeUnit.SECOND:
            ffmpeg.filter(
                "tpad",
                audio_process,
                start_duration=time_padding_start.value,
            )
    if object_length.unit in [TimeUnit.FRAME, TimeUnit.SECOND]:
        time_padding_end = vsml_content.style.time_padding_end
        match time_padding_end.unit:
            case TimeUnit.FRAME:
                ffmpeg.filter(
                    "tpad",
                    audio_process,
                    start=time_padding_start.value,
                )
            case TimeUnit.SECOND:
                ffmpeg.filter(
                    "tpad",
                    audio_process,
                    start_duration=time_padding_start.value,
                )

    # processの作成
    return Process(None, audio_process, vsml_content.style)

import math

import ffmpeg

from content import SourceContent
from converter.schemas import Process
from converter.utils import get_background_process
from style import AudioSystem, GraphicUnit, TimeUnit
from utils import VSMLManager


def create_video_process(
    vsml_content: SourceContent,
    debug_mode: bool = False,
) -> Process:
    # sourceの取得
    source = ffmpeg.input(vsml_content.src_path)
    video_process = source.video
    audio_process = source.audio

    # videoのstyle対応
    # resize
    width = vsml_content.style.width
    height = vsml_content.style.height
    if width.unit != GraphicUnit.AUTO or height.unit != GraphicUnit.AUTO:
        video_process = ffmpeg.filter(
            video_process,
            "scale",
            width.get_pixel(-1),
            height.get_pixel(-1),
        )
    # padding and background-color
    source_width_px = (
        vsml_content.style.source_width.value
        if vsml_content.style.source_width is not None
        else 0.0
    )
    padding_left_px = vsml_content.style.padding_left.get_pixel()
    padding_right_px = vsml_content.style.padding_right.get_pixel()
    source_height_px = (
        vsml_content.style.source_height.value
        if vsml_content.style.source_height is not None
        else 0.0
    )
    padding_top_px = vsml_content.style.padding_top.get_pixel()
    padding_bottom_px = vsml_content.style.padding_bottom.get_pixel()
    width_px_with_padding = (
        width.get_pixel(source_width_px) + padding_left_px + padding_right_px
    )
    height_px_with_padding = (
        height.get_pixel(source_height_px) + padding_top_px + padding_bottom_px
    )
    if (
        source_width_px != width_px_with_padding
        or source_height_px != height_px_with_padding
    ):
        transparent_process = get_background_process(
            "{}x{}".format(width_px_with_padding, height_px_with_padding),
            vsml_content.style.background_color,
        )
        video_process = ffmpeg.overlay(
            transparent_process,
            video_process,
            x=padding_left_px,
            y=padding_top_px,
        )

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
                video_process,
                end_frame=object_length.value + 1,
            )
            ffmpeg.filter(
                "atrim",
                audio_process,
                end=object_length.value / VSMLManager.get_root_fps(),
            )
        case TimeUnit.SECOND:
            ffmpeg.trim(
                video_process,
                end=object_length.value,
            )
            ffmpeg.filter(
                "atrim",
                audio_process,
                end=object_length.value,
            )
    background_color = (
        vsml_content.style.background_color.value
        if vsml_content.style.background_color
        else "0x00000000"
    )
    time_padding_start = vsml_content.style.time_padding_start
    match time_padding_start.unit:
        case TimeUnit.FRAME:
            ffmpeg.filter(
                "tpad",
                video_process,
                start=time_padding_start.value,
                color=background_color,
            )
            ffmpeg.filter(
                "adelay",
                audio_process,
                delays=time_padding_start.value / VSMLManager.get_root_fps(),
                all=1,
            )
        case TimeUnit.SECOND:
            ffmpeg.filter(
                "tpad",
                video_process,
                start_duration=time_padding_start.value,
                color=background_color,
            )
            ffmpeg.filter(
                "adelay",
                audio_process,
                delays=time_padding_start.value,
                all=1,
            )
    if object_length.unit in [TimeUnit.FRAME, TimeUnit.SECOND]:
        time_padding_end = vsml_content.style.time_padding_end
        match time_padding_end.unit:
            case TimeUnit.FRAME:
                ffmpeg.filter(
                    "tpad",
                    video_process,
                    stop=time_padding_start.value,
                    color=background_color,
                )
                ffmpeg.filter(
                    "apad",
                    audio_process,
                    pad_dur=time_padding_start.value
                    / VSMLManager.get_root_fps(),
                )
            case TimeUnit.SECOND:
                ffmpeg.filter(
                    "tpad",
                    video_process,
                    stop_duration=time_padding_start.value,
                    color=background_color,
                )
                ffmpeg.filter(
                    "apad",
                    audio_process,
                    pad_dur=time_padding_start.value,
                )

    return Process(video_process, audio_process, vsml_content.style)

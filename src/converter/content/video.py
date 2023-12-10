import math

import ffmpeg

from content import SourceContent
from converter.schemas import Process
from converter.utils import get_background_process, get_graphical_process
from style import AudioSystem, GraphicUnit, TimeUnit
from utils import VSMLManager


def create_video_process(
    vsml_content: SourceContent,
    debug_mode: bool = False,
) -> Process:
    # sourceの取得
    source = get_graphical_process(
        vsml_content.src_path, vsml_content.exist_audio
    )
    video_process = source["video"]
    audio_process = source["audio"]

    style = vsml_content.style
    # videoのstyle対応
    # resize
    if (
        style.width.unit != GraphicUnit.AUTO
        or style.height.unit != GraphicUnit.AUTO
    ):
        video_process = ffmpeg.filter(
            video_process,
            "scale",
            style.width.get_pixel(-1),
            style.height.get_pixel(-1),
        )
    # padding and background-color
    padding_left_px = style.padding_left.get_pixel()
    padding_right_px = style.padding_right.get_pixel()
    padding_top_px = style.padding_top.get_pixel()
    padding_bottom_px = style.padding_bottom.get_pixel()
    if (
        padding_top_px != 0
        or padding_left_px != 0
        or padding_right_px != 0
        or padding_bottom_px != 0
    ):
        (
            width_with_padding,
            height_with_padding,
        ) = style.get_size_with_padding()
        transparent_process = get_background_process(
            "{}x{}".format(width_with_padding, height_with_padding),
            style.background_color,
        )
        video_process = ffmpeg.overlay(
            transparent_process,
            video_process,
            x=padding_left_px,
            y=padding_top_px,
        )

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
        video_option = {}
        audio_option = {}
        if style.object_length.unit == TimeUnit.FRAME:
            video_option = {"end_frame": style.object_length.value + 1}
            audio_option = {
                "end": style.object_length.value / VSMLManager.get_root_fps()
            }
        elif style.object_length.unit == TimeUnit.SECOND:
            video_option = {"end": style.object_length.value}
            audio_option = {"end": style.object_length.value}
        video_process = ffmpeg.trim(video_process, **video_option)
        audio_process = ffmpeg.filter(audio_process, "atrim", **audio_option)
    background_color = (
        style.background_color.value
        if style.background_color
        else "0x00000000"
    )
    if style.time_padding_start.unit in [TimeUnit.FRAME, TimeUnit.SECOND]:
        video_option = {}
        delays = int(
            style.time_padding_start.get_second(VSMLManager.get_root_fps())
            * 1000
        )
        if style.object_length.unit == TimeUnit.FRAME:
            video_option = {"start": style.time_padding_start.value}
        elif style.object_length.unit == TimeUnit.SECOND:
            video_option = {
                "start_duration": style.time_padding_start.value,
            }
        video_process = ffmpeg.filter(
            video_process, "tpad", color=background_color, **video_option
        )
        audio_process = ffmpeg.filter(
            audio_process,
            "adelay",
            all=1,
            delays=delays,
        )
    if style.object_length.unit in [
        TimeUnit.FRAME,
        TimeUnit.SECOND,
    ] and style.time_padding_end.unit in [TimeUnit.FRAME, TimeUnit.SECOND]:
        video_option = {}
        audio_option = {}
        if style.time_padding_end.unit == TimeUnit.FRAME:
            video_option = {
                "stop": style.time_padding_start.value,
            }
            audio_option = {
                "pad_dur": style.time_padding_start.value
                / VSMLManager.get_root_fps(),
            }
        elif style.time_padding_end.unit == TimeUnit.SECOND:
            video_option = {
                "stop_duration": style.time_padding_start.value,
            }
            audio_option = {
                "pad_dur": style.time_padding_start.value,
            }
        video_process = ffmpeg.filter(
            video_process, "tpad", color=background_color, **video_option
        )
        audio_process = ffmpeg.filter(audio_process, "apad", **audio_option)

    return Process(video_process, audio_process, vsml_content.style)

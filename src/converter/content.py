from typing import Any, Optional

from content import SourceContent
from style import Style
from utils import SourceType

from .ffmpeg import (
    audio_system_filter,
    audio_volume_filter,
    get_background_color_code,
    get_source_process,
    get_text_process,
    object_length_filter,
    set_background_filter,
    time_space_end_filter,
    time_space_start_filter,
    width_height_filter,
)
from .schemas import Process


def get_process_by_source(
    src_path: str, type: SourceType, exist_audio: bool, style: Style
) -> tuple[Optional[Any], Optional[Any]]:
    video_process = None
    audio_process = None
    match type:
        case SourceType.IMAGE:
            source = get_source_process(src_path, True, False, loop=1)
            video_process = source["video"].filter("setsar", "1/1")
        case SourceType.VIDEO:
            source = get_source_process(src_path, True, exist_audio)
            video_process = source["video"]
            audio_process = source["audio"]
        case SourceType.AUDIO:
            audio_process = get_source_process(src_path, False, True)["audio"]
        case SourceType.TEXT:
            video_process = get_text_process(
                src_path,
                style.get_width_with_padding(),
                style.get_height_with_padding(),
                style.padding_left,
                style.padding_top,
                style.background_color,
                style.font_family,
                style.font_weight,
                style.font_style,
                style.font_size,
                style.font_color,
                style.font_border_color,
                style.font_border_width,
            )
        case _:
            raise Exception()
    return video_process, audio_process


def create_source_process(
    vsml_content: SourceContent,
    debug_mode: bool = False,
) -> Process:
    # styleの取得
    style = vsml_content.style
    video_process, audio_process = get_process_by_source(
        vsml_content.src_path,
        vsml_content.type,
        vsml_content.exist_audio,
        style,
    )

    if video_process is not None and vsml_content.type != SourceType.TEXT:
        # videoのstyle対応
        # resize
        video_process = width_height_filter(
            style.width, style.height, video_process
        )
        # padding and background-color
        if (
            style.padding_top.is_zero_over()
            or style.padding_left.is_zero_over()
        ):
            video_process = set_background_filter(
                width=style.get_width_with_padding(),
                height=style.get_height_with_padding(),
                background_color=style.background_color,
                video_process=video_process,
                position_x=style.padding_left,
                position_y=style.padding_top,
                fit_video_process=True,
            )

    if audio_process is not None:
        # audioのstyle対応
        audio_process = audio_system_filter(
            style.source_audio_system, style.audio_system, audio_process
        )
        audio_process = audio_volume_filter(style.audio_volume, audio_process)

    # timeのstyle対応
    background_color_code = get_background_color_code(style.background_color)
    video_process, audio_process = object_length_filter(
        style.object_length, video_process, audio_process
    )
    video_process, audio_process = time_space_start_filter(
        style.time_padding_start,
        background_color_code,
        video_process,
        audio_process,
    )
    if style.object_length.has_specific_value():
        video_process, audio_process = time_space_end_filter(
            style.time_padding_end,
            background_color_code,
            video_process,
            audio_process,
        )

    return Process(video_process, audio_process, vsml_content.style)

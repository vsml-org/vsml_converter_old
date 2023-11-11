import ffmpeg

from content import SourceContent
from converter.schemas import Process
from converter.utils import get_background_process
from style import GraphicUnit, TimeUnit


def create_image_process(
    vsml_content: SourceContent,
    debug_mode: bool = False,
) -> Process:
    # video_processの処理
    video_process = ffmpeg.input(vsml_content.src_path, loop=1).video.filter(
        "setsar", "1/1"
    )

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
    padding_top_px = style.padding_top.get_pixel()
    padding_left_px = style.padding_left.get_pixel()
    padding_right_px = style.padding_right.get_pixel()
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

    # timeのstyle対応
    if style.object_length.unit in [TimeUnit.FRAME, TimeUnit.SECOND]:
        option = {}
        if style.object_length.unit == TimeUnit.FRAME:
            option = {"end_frame": style.object_length.value + 1}
        elif style.object_length.unit == TimeUnit.SECOND:
            option = {"end": style.object_length.value}
        video_process = ffmpeg.trim(video_process, **option)
    background_color = (
        style.background_color.value
        if style.background_color
        else "0x00000000"
    )
    if style.time_padding_start.unit in [TimeUnit.FRAME, TimeUnit.SECOND]:
        option = {}
        if style.time_padding_start.unit == TimeUnit.FRAME:
            option = {"start": style.time_padding_start.value}
        elif style.time_padding_start.unit == TimeUnit.SECOND:
            option = {"start_duration": style.time_padding_start.value}
        video_process = ffmpeg.filter(
            video_process,
            "tpad",
            color=background_color,
            **option,
        )
    if style.object_length.unit in [
        TimeUnit.FRAME,
        TimeUnit.SECOND,
    ] and style.time_padding_end.unit in [TimeUnit.FRAME, TimeUnit.SECOND]:
        option = {}
        if style.time_padding_end.unit == TimeUnit.FRAME:
            option = {"stop": style.time_padding_end.value}
        elif style.time_padding_end.unit == TimeUnit.SECOND:
            option = {"stop_duration": style.time_padding_end.value}
        video_process = ffmpeg.filter(
            video_process,
            "tpad",
            color=background_color,
            **option,
        )

    return Process(video_process, None, vsml_content.style)

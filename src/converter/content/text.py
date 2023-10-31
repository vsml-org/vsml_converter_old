import ffmpeg

from content import SourceContent
from converter.schemas import Process
from converter.utils import get_background_process
from style import TimeUnit


def create_text_process(
    vsml_content: SourceContent,
    debug_mode: bool = False,
) -> Process:
    # videoのstyle対応
    # padding and background-color
    style = vsml_content.style

    padding_left_px = style.padding_left.get_pixel()
    padding_top_px = style.padding_top.get_pixel()
    (
        width_with_padding,
        height_with_padding,
    ) = style.get_size_with_padding()
    transparent_process = get_background_process(
        "{}x{}".format(width_with_padding, height_with_padding),
        style.background_color,
    )
    # TODO: フォントファイルを指定する
    video_process = ffmpeg.drawtext(
        transparent_process,
        text=vsml_content.src_path,
        fontcolor=style.font_color,
        bordercolor=style.font_border_color,
        borderw=style.font_border_width,
        x=int(padding_left_px),
        y=int(padding_top_px),
    )

    # timeのstyle対応
    if style.object_length.unit in [TimeUnit.FRAME, TimeUnit.SECOND]:
        option = {}
        if style.object_length.unit == TimeUnit.FRAME:
            option = {"end_frame": style.object_length.value + 1}
        elif style.object_length.unit == TimeUnit.SECOND:
            option = {"end": style.object_length.value}
        ffmpeg.trim(video_process, **option)
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
        ffmpeg.filter(
            "tpad",
            video_process,
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
        ffmpeg.filter(
            "tpad",
            video_process,
            color=background_color,
            **option,
        )

    return Process(video_process, None, vsml_content.style)

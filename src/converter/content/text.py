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
    option: dict = {
        "x": padding_left_px,
        "y": padding_top_px,
    }
    if style.font_family is not None:
        option |= {
            "font": style.font_family,
        }
    if style.font_size is not None:
        option |= {
            "fontsize": style.font_size.get_pixel(),
        }
    if style.font_color is not None:
        option |= {
            "fontcolor": style.font_color.value,
        }
    if style.font_border_color is not None:
        option |= {
            "bordercolor": style.font_border_color.value,
        }
    if style.font_border_width is not None:
        option |= {
            "borderw": style.font_border_width,
        }

    video_process = ffmpeg.drawtext(
        transparent_process,
        text=vsml_content.src_path,
        **option,
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

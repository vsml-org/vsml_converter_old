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
    width = vsml_content.style.width
    padding_left_px = vsml_content.style.padding_left.get_pixel()
    padding_right_px = vsml_content.style.padding_right.get_pixel()
    height = vsml_content.style.height
    padding_top_px = vsml_content.style.padding_top.get_pixel()
    padding_bottom_px = vsml_content.style.padding_bottom.get_pixel()
    width_px_with_padding = (
        width.get_pixel(0) + padding_left_px + padding_right_px
    )
    height_px_with_padding = (
        height.get_pixel(0) + padding_top_px + padding_bottom_px
    )
    transparent_process = get_background_process(
        "{}x{}".format(width_px_with_padding, height_px_with_padding),
        vsml_content.style.background_color,
    )
    # TODO: フォントファイルを指定する
    video_process = ffmpeg.drawtext(
        transparent_process,
        text=vsml_content.src_path,
        fontcolor=vsml_content.style.font_color,
        bordercolor=vsml_content.style.font_border_color,
        borderw=vsml_content.style.font_border_width,
        x=int(padding_left_px),
        y=int(padding_top_px),
    )

    # timeのstyle対応
    object_length = vsml_content.style.object_length
    match object_length.unit:
        case TimeUnit.FRAME:
            ffmpeg.trim(
                video_process,
                end_frame=object_length.value + 1,
            )
        case TimeUnit.SECOND:
            ffmpeg.trim(
                video_process,
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
        case TimeUnit.SECOND:
            ffmpeg.filter(
                "tpad",
                video_process,
                start_duration=time_padding_start.value,
                color=background_color,
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
            case TimeUnit.SECOND:
                ffmpeg.filter(
                    "tpad",
                    video_process,
                    stop_duration=time_padding_start.value,
                    color=background_color,
                )

    return Process(video_process, None, vsml_content.style)

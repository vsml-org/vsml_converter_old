from typing import Optional

import ffmpeg

from converter.ffmpeg import (
    get_background_process,
    get_source_process,
    get_text_process,
    layering_filter,
    set_background_filter,
    width_height_filter,
)
from converter.schemas import Process
from style import GraphicValue, LayerMode, Order
from utils import SourceType
from vsml import SourceContent, VSMLContent, WrapContent


def create_preview_source_process(vsml_content: SourceContent) -> Process:
    style = vsml_content.style
    if vsml_content.type == SourceType.TEXT:
        video_process = get_text_process(
            vsml_content.src_path,
            style.get_width_with_padding(),
            style.get_height_with_padding(),
            style.padding_left,
            style.padding_top,
            style.background_color,
            style.using_font_path,
            style.font_size,
            style.font_color,
            style.font_border_color,
            style.font_border_width,
        )
    else:
        video_process = get_source_process(
            vsml_content.src_path,
            exist_video=True,
            exist_audio=False,
        )["video"]
    if vsml_content.type != SourceType.TEXT:
        video_process = width_height_filter(
            style.width, style.height, video_process
        )
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
    if vsml_content._second != -1 and vsml_content.tag_name == "vid":
        video_process = ffmpeg.trim(video_process, start=vsml_content._second)
    return Process(video_process, None, vsml_content.style)


def create_preview_wrap_process(
    child_processes: list[Process], vsml_content: WrapContent
) -> Process:
    style = vsml_content.style
    video_process = None
    width = style.get_width_with_padding()
    height = style.get_height_with_padding()
    if style.order == Order.SEQUENCE:
        if len(child_processes):
            video_process = child_processes[0].video
        else:
            video_process = get_background_process(
                "{}x{}".format(
                    width.get_pixel(),
                    height.get_pixel(),
                ),
                style.background_color,
            )

    elif style.order == Order.PARALLEL:
        video_process = get_background_process(
            "{}x{}".format(
                width.get_pixel(),
                height.get_pixel(),
            ),
            style.background_color,
        )
        is_single = style.layer_mode == LayerMode.SINGLE
        is_row = style.direction is None or style.direction.is_row()
        is_reverse = style.direction is None or style.direction.is_reverse
        current_graphic_length = (
            (
                width - style.padding_right
                if is_row
                else height - style.padding_bottom
            )
            if is_reverse
            else (style.padding_left if is_row else style.padding_top)
        )
        remain_margin = GraphicValue("0")

        for child_process in child_processes:
            child_style = child_process.style
            if child_process.video is not None:
                max_space = max(
                    (
                        child_style.margin_left
                        if is_row
                        else child_style.margin_top
                    ),
                    remain_margin,
                )
                child_graphic_length = (
                    child_style.get_width_with_padding()
                    if is_row
                    else child_style.get_height_with_padding()
                )

                current_graphic_length += (
                    -child_graphic_length if is_reverse else max_space
                )
                video_process = layering_filter(
                    video_process,
                    child_process.video,
                    (
                        current_graphic_length
                        if is_single and is_row
                        else style.padding_left + child_style.margin_left
                    ),
                    (
                        current_graphic_length
                        if is_single and not is_row
                        else style.padding_top + child_style.margin_top
                    ),
                )
                current_graphic_length += (
                    -max_space if is_reverse else child_graphic_length
                )
                remain_margin = (
                    child_style.margin_right
                    if is_row
                    else child_style.margin_bottom
                )
    else:
        raise Exception()
    return Process(video_process, None, style)


def create_preview_process(vsml_content: Optional[VSMLContent]) -> Process:
    if isinstance(vsml_content, SourceContent):
        process = create_preview_source_process(vsml_content)
    elif isinstance(vsml_content, WrapContent):
        child_processes = []
        for item in vsml_content.items:
            child_process = create_preview_process(item)
            if child_process is not None:
                child_processes.append(child_process)
        process = create_preview_wrap_process(child_processes, vsml_content)
    else:
        raise Exception()

    return process

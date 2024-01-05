from content import WrapContent
from converter.ffmpeg import (
    adjust_parallel_audio,
    audio_merge_filter,
    get_background_color_code,
    get_background_process,
    layering_filter,
    object_length_filter,
    time_space_end_filter,
    time_space_start_filter,
)
from converter.schemas import Process
from style import GraphicValue, LayerMode


def create_parallel_process(
    child_processes: list[Process],
    vsml_content: WrapContent,
    debug_mode: bool = False,
) -> Process:
    video_process = None
    audio_process = None

    style = vsml_content.style
    (
        width_px_with_padding,
        height_px_with_padding,
    ) = style.get_size_with_padding()

    background_color_code = get_background_color_code(style.background_color)
    if vsml_content.exist_video:
        video_process = get_background_process(
            "{}x{}".format(
                width_px_with_padding.get_pixel(),
                height_px_with_padding.get_pixel(),
            ),
            style.background_color,
        )
        video_process, _ = object_length_filter(
            style.object_length, video_process=video_process
        )

    is_row = style.direction is None or style.direction.is_row()
    is_reverse = style.direction is None or style.direction.is_reverse
    current_graphic_length = (
        (
            width_px_with_padding - style.padding_right
            if is_row
            else height_px_with_padding - style.padding_bottom
        )
        if is_reverse
        else (style.padding_left if is_row else style.padding_top)
    )

    remain_margin = GraphicValue("0")

    for child_process in child_processes:
        child_style = child_process.style
        child_process.video, child_process.audio = time_space_start_filter(
            child_style.time_margin_start,
            background_color_code,
            child_process.video,
            child_process.audio,
        )
        if not child_style.object_length.is_fit():
            child_process.video, child_process.audio = time_space_end_filter(
                child_style.time_margin_end,
                background_color_code,
                child_process.video,
                child_process.audio,
            )
        if child_process.video is not None:
            match style.layer_mode:
                case LayerMode.SINGLE:
                    (
                        child_width_with_padding,
                        child_height_with_padding,
                    ) = child_style.get_size_with_padding()
                    child_graphic_length = (
                        child_width_with_padding
                        if is_row
                        else child_height_with_padding
                    )
                    if is_reverse:
                        current_graphic_length -= child_graphic_length
                    else:
                        current_graphic_length += (
                            max(
                                child_style.margin_left,
                                remain_margin,
                            )
                            if is_row
                            else max(
                                child_style.margin_top,
                                remain_margin,
                            )
                        )
                    video_process = layering_filter(
                        video_process,
                        child_process.video,
                        current_graphic_length
                        if is_row
                        else style.padding_left + child_style.margin_left,
                        current_graphic_length
                        if not is_row
                        else style.padding_top + child_style.margin_top,
                    )
                    if is_reverse:
                        current_graphic_length -= (
                            max(
                                child_style.margin_left,
                                remain_margin,
                            )
                            if is_row
                            else max(
                                child_style.margin_top,
                                remain_margin,
                            )
                        )
                    else:
                        current_graphic_length += child_graphic_length

                    remain_margin = (
                        child_style.margin_right
                        if is_row
                        else child_style.margin_bottom
                    )
                case LayerMode.MULTI:
                    video_process = layering_filter(
                        video_process,
                        child_process.video,
                        style.padding_left + child_style.margin_left,
                        style.padding_top + child_style.margin_top,
                    )
                case _:
                    raise Exception()
        if child_process.audio is not None:
            audio_process = audio_merge_filter(
                audio_process, child_process.audio
            )
    if audio_process is not None:
        audio_process = adjust_parallel_audio(
            style.object_length, audio_process
        )
    video_process, audio_process = object_length_filter(
        style.object_length,
        video_process=video_process,
        audio_process=audio_process,
    )

    return Process(
        video_process,
        audio_process,
        vsml_content.style,
    )

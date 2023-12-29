from content import WrapContent
from converter.ffmpeg import (
    adjust_parallel_audio,
    audio_merge_filter,
    get_background_color_code,
    layering_filter,
    object_length_filter,
    time_space_end_filter,
    time_space_start_filter,
)
from converter.schemas import Process
from converter.utils import get_background_process
from style import GraphicValue, LayerMode, TimeUnit


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

    left_width = GraphicValue("0")
    remain_margin = GraphicValue("0")
    option_x = style.padding_left

    for child_process in child_processes:
        child_style = child_process.style
        child_process.video, child_process.audio = time_space_start_filter(
            child_style.time_margin_start,
            background_color_code,
            child_process.video,
            child_process.audio,
        )
        if style.object_length.unit != TimeUnit.FIT:
            child_process.video, child_process.audio = time_space_end_filter(
                child_style.time_margin_end,
                background_color_code,
                child_process.video,
                child_process.audio,
            )
        if child_process.video is not None:
            match style.layer_mode:
                case LayerMode.SINGLE:
                    max_margin = max(
                        child_style.margin_left,
                        remain_margin,
                    )
                    option_x = left_width + max_margin
                    video_process = layering_filter(
                        video_process,
                        child_process.video,
                        option_x,
                        style.padding_top + child_style.margin_top,
                    )
                    child_width, _ = child_style.get_size_with_padding()
                    left_width += max_margin + child_width
                    remain_margin = child_style.margin_right
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

    return Process(
        video_process,
        audio_process,
        vsml_content.style,
    )

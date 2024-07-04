from content import WrapContent
from converter.ffmpeg import (
    get_background_color_code,
    time_space_end_filter,
    time_space_start_filter,
)
from converter.schemas import Process
from style import Order

from .parallel import create_parallel_process
from .sequence import create_sequence_process


def create_wrap_process(
    child_processes: list[Process],
    vsml_content: WrapContent,
    debug_mode: bool = False,
) -> Process:
    match vsml_content.style.order:
        case Order.SEQUENCE:
            process = create_sequence_process(
                child_processes, vsml_content, debug_mode
            )
        case Order.PARALLEL:
            process = create_parallel_process(
                child_processes, vsml_content, debug_mode
            )
        case _:
            raise Exception()

    style = vsml_content.style
    background_color_code = get_background_color_code(style.background_color)
    process.video, process.audio = time_space_start_filter(
        style.time_padding_start,
        background_color_code,
        process.video,
        process.audio,
    )
    if style.duration.has_specific_value():
        process.video, process.audio = time_space_end_filter(
            style.time_padding_end,
            background_color_code,
            process.video,
            process.audio,
        )

    return process

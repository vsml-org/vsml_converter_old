import ffmpeg

from content import WrapContent
from converter.schemas import Process
from style import Order, TimeUnit
from utils import VSMLManager

from .parallel import create_parallel_process
from .sequence import create_sequence_process


def create_wrap_process(
    processes: list[Process],
    vsml_content: WrapContent,
    debug_mode: bool = False,
) -> Process:
    fps = VSMLManager.get_root_fps()
    style = vsml_content.style
    match vsml_content.style.order:
        case Order.SEQUENCE:
            process = create_sequence_process(
                processes, vsml_content, debug_mode
            )
        case Order.PARALLEL:
            process = create_parallel_process(
                processes, vsml_content, debug_mode
            )
        case _:
            raise Exception()

    background_color = (
        style.background_color.value
        if style.background_color
        else "0x00000000"
    )
    if style.time_padding_start.unit in [TimeUnit.FRAME, TimeUnit.SECOND]:
        video_option = {}
        audio_option = {}
        if style.time_padding_start.unit == TimeUnit.FRAME:
            video_option = {"start": style.time_padding_start.value}
            audio_option = {
                "delays": "{}s".format(
                    style.time_padding_start.get_second(fps)
                ),
            }
        elif style.time_padding_start.unit == TimeUnit.SECOND:
            video_option = {
                "start_duration": style.time_padding_start.get_second(fps),
            }
            audio_option = {
                "delays": "{}s".format(
                    style.time_padding_start.get_second(fps)
                ),
            }
        if process.video is not None:
            process.video = ffmpeg.filter(
                process.video, "tpad", color=background_color, **video_option
            )
        if process.audio is not None:
            process.audio = ffmpeg.filter(
                process.audio, "adelay", all=1, **audio_option
            )
    if style.object_length.unit in [
        TimeUnit.FRAME,
        TimeUnit.SECOND,
    ] and style.time_padding_end.unit in [TimeUnit.FRAME, TimeUnit.SECOND]:
        video_option = {}
        audio_option = {}
        if style.time_padding_end.unit == TimeUnit.FRAME:
            video_option = {
                "stop": style.time_padding_end.value,
            }
            audio_option = {
                "pad_dur": style.time_padding_end.get_second(fps),
            }
        elif style.time_padding_end.unit == TimeUnit.SECOND:
            video_option = {
                "stop_duration": style.time_padding_end.get_second(fps),
            }
            audio_option = {
                "pad_dur": style.time_padding_end.get_second(fps),
            }
        if process.video is not None:
            process.video = ffmpeg.filter(
                process.video, "tpad", color=background_color, **video_option
            )
        if process.audio is not None:
            process.audio = ffmpeg.filter(
                process.audio, "apad", **audio_option
            )
    return process

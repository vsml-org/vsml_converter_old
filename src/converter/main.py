from typing import Optional

from content import SourceContent, VSMLContent, WrapContent
from utils import VSMLManager
from vsml import VSML

from .content import create_source_process
from .ffmpeg import (
    export_video,
    get_background_process,
    duration_filter,
    set_background_filter,
    time_space_end_filter,
    time_space_start_filter,
)
from .schemas import Process
from .wrap import create_wrap_process


def create_process(
    vsml_content: VSMLContent,
    debug_mode: bool = False,
) -> Process:
    if isinstance(vsml_content, SourceContent):
        process = create_source_process(
            vsml_content,
            debug_mode,
        )
    elif isinstance(vsml_content, WrapContent):
        child_processes = []
        for item in vsml_content.items:
            child_process = create_process(item, debug_mode)
            if child_process is not None:
                child_processes.append(child_process)
        process = create_wrap_process(
            child_processes,
            vsml_content,
            debug_mode,
        )
    else:
        raise Exception()

    return process


def convert_video(
    vsml_data: VSML,
    out_filename: Optional[str],
    debug_mode: bool,
    overwrite: bool,
):
    out_filename = "video.mp4" if out_filename is None else out_filename

    process = create_process(vsml_data.content, debug_mode)
    style = vsml_data.content.style
    if process.video is None:
        black_video_process = get_background_process(VSMLManager.get_root_resolution().get_str())
        process.video, _ = duration_filter(style.duration, black_video_process, None)
    else:
        process.video = set_background_filter(
            background_color=style.background_color,
            resolution_text=VSMLManager.get_root_resolution().get_str(),
            video_process=process.video,
            fit_video_process=True,
        )
    process.video, process.audio = time_space_start_filter(
        style.time_margin_start,
        video_process=process.video,
        audio_process=process.audio,
    )
    if style.duration.has_specific_value():
        process.video, process.audio = time_space_end_filter(
            style.time_margin_end,
            video_process=process.video,
            audio_process=process.audio,
        )

    export_video(
        process.video, process.audio, out_filename, debug_mode, overwrite
    )

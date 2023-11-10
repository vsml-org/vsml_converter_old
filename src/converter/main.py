import time
from typing import Optional

import ffmpeg

from content import SourceContent, VSMLContent, WrapContent
from utils import VSMLManager
from vsml import VSML

from .content import create_source_process
from .schemas import Process
from .utils import get_background_process
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

    if debug_mode:
        # print(f"[new call detected]\ntype: {vsml_content.type}")
        print(process)

    return process


def convert_video(
    vsml_data: VSML,
    out_filename: Optional[str],
    debug_mode: bool,
    overwrite: bool,
):
    out_filename = "video.mp4" if out_filename is None else out_filename

    process = create_process(vsml_data.content, debug_mode)
    if process.video:
        fps = VSMLManager.get_root_fps()
        style = vsml_data.content.style
        source_object_length = (
            style.source_object_length.get_second(fps)
            if style.source_object_length
            else 0.0
        )
        bg_process = get_background_process(
            VSMLManager.get_root_resolution().get_str()
        )
        process.video = ffmpeg.overlay(bg_process, process.video, x=0, y=0)
        process.video = ffmpeg.trim(
            process.video,
            end=style.object_length.get_second(fps, source_object_length),
        )
    match (
        process.video,
        process.audio,
    ):
        case None, None:
            raise Exception()
        case _, None:
            process = process.video
        case None, _:
            process = process.audio
        case _:
            process = ffmpeg.concat(
                process.video,
                process.audio,
                v=1,
                a=1,
                n=1,
            )
    process = ffmpeg.output(
        process,
        out_filename,
        r=VSMLManager.get_root_fps(),
    )

    if debug_mode:
        print(vsml_data.content)
        ffmpeg.view(process)
        time.sleep(0.1)
        print("\n[[[command args]]]\n{}".format(ffmpeg.compile(process)))

    ffmpeg.run(
        process,
        overwrite_output=overwrite,
    )

import time
from typing import Optional
import ffmpeg
from content import VSMLContent, SourceContent, WrapContent
from vsml import VSML
from .content import create_source_process
from .schemas import Process
from .wrap import create_wrap_process

def create_process(vsml_content: VSMLContent, debug_mode: bool = False) -> Optional[Process]:
    if isinstance(vsml_content, SourceContent):
        process = create_source_process(vsml_content, debug_mode)
    elif isinstance(vsml_content, WrapContent):
        child_processes = []
        for item in vsml_content.items:
            child_process = create_process(item, debug_mode)
            if child_process:
                child_processes.append(child_process)
        process = create_wrap_process(child_processes, vsml_content, debug_mode)
    else:
        raise Exception()

    if debug_mode:
        # print(f'[new call detected]\ntype: {vsml_content.type}')
        print(process)

    return process

def convert_video(vsml_data: VSML, out_filename: Optional[str], debug_mode: bool, overwrite: bool):
    out_filename = 'video.mp4' if out_filename is None else out_filename

    process = create_process(vsml_data.content, debug_mode)
    if process is None:
        raise Exception()
    if process.duration is None:
        raise Exception()
    match (process.video, process.audio):
        case None, None:
            raise Exception()
        case _, None:
            process = process.video
        case None, _:
            process = process.audio
        case _:
            process = ffmpeg.concat(process.video, process.audio, v=1, a=1, n=1)
    process = ffmpeg.output(process, out_filename, r=vsml_data.fps)

    if debug_mode:
        print(vsml_data.content)
        ffmpeg.view(process)
        time.sleep(0.1)
        print(f'\n[[[command args]]]\n{ffmpeg.compile(process)}')

    ffmpeg.run(process, overwrite_output=overwrite)

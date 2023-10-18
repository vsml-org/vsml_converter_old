from typing import Optional
import ffmpeg
from content import WrapContent
from style.types import Order
from .schemas import Process

def create_sequence_process(processes: list[Process], vsml_content: WrapContent, debug_mode: bool = False) -> Process:
    video_process = None
    audio_process = None

    return Process(video_process, audio_process, None, None, None)

def create_parallel_process(processes: list[Process], vsml_content: WrapContent, debug_mode: bool = False) -> Process:
    video_process = None
    audio_process = None

    return Process(video_process, audio_process, None, None, None)

def create_wrap_process(processes: list[Process], vsml_content: WrapContent, debug_mode: bool = False) -> Optional[Process]:
    if vsml_content.style.order == Order.SEQUENCE:
        process = create_sequence_process(processes, vsml_content, debug_mode)
    elif vsml_content.style.order == Order.PARALLEL:
        process = create_parallel_process(processes, vsml_content, debug_mode)
    else:
        raise Exception()
    
    return process

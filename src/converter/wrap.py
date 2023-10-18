import ffmpeg
from typing import Optional
from content import VSMLContent
from .schemas import Process

def create_sequence_process(processes: list[Process], vsml_content: VSMLContent, debug_mode: bool = False) -> Process:
    video_process = None
    audio_process = None

    # Processにまとめてreturn
    return Process(video_process, audio_process, None, None, None)

def create_parallel_process(processes: list[Process], vsml_content: VSMLContent, debug_mode: bool = False) -> Process:
    video_process = None
    audio_process = None

    # Processにまとめてreturn
    return Process(video_process, audio_process, None, None, None)

def create_wrap_process(processes: list[Process], vsml_content: VSMLContent, debug_mode: bool = False) -> Optional[Process]:
    process = create_sequence_process(processes, vsml_content, debug_mode)
    
    return process

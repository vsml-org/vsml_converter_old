import ffmpeg
from content import SourceContent
from .schemas import Process

def create_source_process(vsml_content: SourceContent, debug_mode: bool = False) -> Process:
    video_process = None
    audio_process = None
    
    return Process(video_process, audio_process, None, None, None)

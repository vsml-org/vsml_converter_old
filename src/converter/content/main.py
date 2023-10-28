from content import SourceContent
from converter.schemas import Process
from utils import SourceType

from .audio import create_audio_process
from .image import create_image_process
from .text import create_text_process
from .video import create_video_process


def create_source_process(
    vsml_content: SourceContent,
    debug_mode: bool = False,
) -> Process:
    match vsml_content.type:
        case SourceType.IMAGE:
            process = create_image_process(vsml_content, debug_mode)
        case SourceType.VIDEO:
            process = create_video_process(vsml_content, debug_mode)
        case SourceType.AUDIO:
            process = create_audio_process(vsml_content, debug_mode)
        case SourceType.TEXT:
            process = create_text_process(vsml_content, debug_mode)
        case _:
            raise Exception()

    return process

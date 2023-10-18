from content import SourceContent
from utils import SourceType

from .schemas import Process


def create_source_process(
    vsml_content: SourceContent,
    debug_mode: bool = False,
) -> Process:
    video_process = None
    audio_process = None

    match vsml_content.type:
        case SourceType.IMAGE:
            pass
        case SourceType.VIDEO:
            pass
        case SourceType.AUDIO:
            pass
        case SourceType.TEXT:
            pass
        case _:
            pass

    return Process(
        video_process,
        audio_process,
        None,
        None,
        None,
    )

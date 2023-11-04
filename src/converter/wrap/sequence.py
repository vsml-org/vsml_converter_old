from content import WrapContent
from converter.schemas import Process


def create_sequence_process(
    processes: list[Process],
    vsml_content: WrapContent,
    debug_mode: bool = False,
) -> Process:
    video_process = None
    audio_process = None

    return Process(
        video_process,
        audio_process,
        vsml_content.style,
    )

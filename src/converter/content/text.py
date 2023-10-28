from content import SourceContent
from converter.schemas import Process


def create_text_process(
    vsml_content: SourceContent,
    debug_mode: bool = False,
) -> Process:
    return Process(None, None, vsml_content.style)

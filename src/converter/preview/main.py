from typing import Optional

import ffmpeg

from converter.ffmpeg import set_background_filter
from utils import VSMLManager
from vsml import VSML, WrapContent

from .content import pick_data
from .process import create_preview_process


def convert_image_from_frame(
    vsml_data: VSML, frame: int, output_path: Optional[str]
) -> None:
    output_path = "preview.png" if output_path is None else output_path
    second = frame / VSMLManager.get_root_fps()
    if second > vsml_data.content.style.duration.get_second():
        raise Exception()
    vsml_content_for_pick = None
    vsml_content = vsml_data.content
    if second >= vsml_content.style.time_margin_start.get_second():
        if second < vsml_content.style.time_padding_start.get_second():
            if isinstance(vsml_content, WrapContent):
                vsml_content.items = []
            vsml_content_for_pick = vsml_content
        else:
            vsml_content_for_pick = pick_data(vsml_content, second)

    process = create_preview_process(vsml_content_for_pick)
    process.video = set_background_filter(
        background_color=vsml_content.style.background_color,
        resolution_text=VSMLManager.get_root_resolution().get_str(),
        video_process=process.video,
        fit_video_process=True,
    )
    process = ffmpeg.output(process.video, output_path, vframes=1)
    process.run(overwrite_output=True)

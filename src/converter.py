import ffmpeg
from typing import Optional
from vsml import VSML, SortType

def convert_video(vsml_data: VSML, out_filename: Optional[str]):
    if out_filename is None:
        out_filename = 'video.mp4'
    
    if vsml_data.content is None:
        raise Exception()
    
    content = vsml_data.content
    match content.type:
        case SortType.SEQUENCE:
            pass
        case _:
            pass

    process = (
        ffmpeg.input(f'color=r={vsml_data.fps}:s={vsml_data.resolution}:d=1', f='lavfi')
            .output(out_filename)
    )
    process.run()

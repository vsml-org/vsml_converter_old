import ffmpeg

from content import SourceContent
from style import GraphicUnit, TimeUnit
from utils import SourceType

from .schemas import Process
from .utils import get_background_process


def create_source_process(
    vsml_content: SourceContent,
    debug_mode: bool = False,
) -> Process:
    video_process = None
    audio_process = None

    match vsml_content.type:
        case SourceType.IMAGE:
            # video_processの処理
            video_process = ffmpeg.input(
                vsml_content.src_path, loop=1
            ).video.filter("setsar", "1/1")

            width = vsml_content.style.width
            height = vsml_content.style.height
            if (
                width.unit != GraphicUnit.AUTO
                or height.unit != GraphicUnit.AUTO
            ):
                video_process = ffmpeg.filter(
                    video_process,
                    "scale",
                    width.get_pixel(-1),
                    height.get_pixel(-1),
                )

            source_width_px = (
                vsml_content.style.source_width.value
                if vsml_content.style.source_width is not None
                else 0.0
            )
            padding_left_px = vsml_content.style.padding_left.get_pixel()
            padding_right_px = vsml_content.style.padding_right.get_pixel()
            source_height_px = (
                vsml_content.style.source_height.value
                if vsml_content.style.source_height is not None
                else 0.0
            )
            padding_top_px = vsml_content.style.padding_top.get_pixel()
            padding_bottom_px = vsml_content.style.padding_bottom.get_pixel()
            width_px_with_padding = (
                width.get_pixel(source_width_px)
                + padding_left_px
                + padding_right_px
            )
            height_px_with_padding = (
                height.get_pixel(source_height_px)
                + padding_top_px
                + padding_bottom_px
            )

            if (
                source_width_px != width_px_with_padding
                or source_height_px != height_px_with_padding
            ):
                transparent_process = get_background_process(
                    "{}x{}".format(
                        width_px_with_padding, height_px_with_padding
                    ),
                    vsml_content.style.background_color,
                )
                video_process = ffmpeg.overlay(
                    transparent_process,
                    video_process,
                    x=padding_left_px,
                    y=padding_top_px,
                )

            object_length = vsml_content.style.object_length
            match object_length.unit:
                case TimeUnit.FRAME:
                    ffmpeg.trim(
                        video_process,
                        end_frame=object_length.value + 1,
                    )
                case TimeUnit.SECOND:
                    ffmpeg.trim(
                        video_process,
                        end=object_length.value,
                    )
            time_padding_start = vsml_content.style.time_padding_start
            match time_padding_start.unit:
                case TimeUnit.FRAME:
                    ffmpeg.filter(
                        "tpad",
                        video_process,
                        start=time_padding_start.value,
                    )
                case TimeUnit.SECOND:
                    ffmpeg.filter(
                        "tpad",
                        video_process,
                        start_duration=time_padding_start.value,
                    )
            if object_length.unit in [TimeUnit.FRAME, TimeUnit.SECOND]:
                time_padding_end = vsml_content.style.time_padding_end
                match time_padding_end.unit:
                    case TimeUnit.FRAME:
                        ffmpeg.filter(
                            "tpad",
                            video_process,
                            start=time_padding_start.value,
                        )
                    case TimeUnit.SECOND:
                        ffmpeg.filter(
                            "tpad",
                            video_process,
                            start_duration=time_padding_start.value,
                        )

        case SourceType.VIDEO:
            pass
        case SourceType.AUDIO:
            pass
        case SourceType.TEXT:
            pass
        case _:
            raise Exception()

    return Process(video_process, audio_process, vsml_content.style)

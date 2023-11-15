import ffmpeg

from content import WrapContent
from converter.schemas import Process
from converter.utils import get_background_process
from style import LayerMode, TimeUnit
from utils import VSMLManager


def create_parallel_process(
    processes: list[Process],
    vsml_content: WrapContent,
    debug_mode: bool = False,
) -> Process:
    fps = VSMLManager.get_root_fps()

    video_process = None
    audio_process = None

    style = vsml_content.style
    (
        width_px_with_padding,
        height_px_with_padding,
    ) = style.get_size_with_padding()

    background_color = (
        style.background_color.value
        if style.background_color
        else "0x00000000"
    )
    if vsml_content.exist_video:
        background_process = get_background_process(
            "{}x{}".format(width_px_with_padding, height_px_with_padding),
            style.background_color,
        )
        if style.object_length.unit in [TimeUnit.FRAME, TimeUnit.SECOND]:
            option = {}
            if style.object_length.unit == TimeUnit.FRAME:
                option = {"end_frame": style.object_length.value + 1}
            elif style.object_length.unit == TimeUnit.SECOND:
                option = {"end": style.object_length.value}
            background_process = ffmpeg.trim(
                background_process,
                **option,
            )
        video_process = background_process

    # 時間的長さがない場合processはNoneとなる
    # 時間的長さがある場合
    if style.object_length.unit != TimeUnit.FIT:
        audio_max_length = 0
        left_width = 0
        remain_margin = 0
        for process in processes:
            # 映像の合成
            if process.video:
                if process.style.time_margin_start.unit in [
                    TimeUnit.FRAME,
                    TimeUnit.SECOND,
                ]:
                    option = {}
                    if process.style.time_margin_start.unit == TimeUnit.FRAME:
                        option = {
                            "start": process.style.time_margin_start.unit
                        }
                    elif (
                        process.style.time_margin_start.unit == TimeUnit.SECOND
                    ):
                        second = process.style.time_margin_start.get_second(
                            fps
                        )
                        option = {"start_duration": second}
                    process.video = ffmpeg.filter(
                        process.video,
                        "tpad",
                        color=background_color,
                        **option,
                    )
                if process.style.time_margin_end.unit in [
                    TimeUnit.FRAME,
                    TimeUnit.SECOND,
                ]:
                    option = {}
                    if process.style.time_margin_end.unit == TimeUnit.FRAME:
                        option = {"stop": process.style.time_margin_end.unit}
                    elif process.style.time_margin_end.unit == TimeUnit.SECOND:
                        second = process.style.time_margin_end.get_second(fps)
                        option = {"stop_duration": second}
                    process.video = ffmpeg.filter(
                        process.video,
                        "tpad",
                        color=background_color,
                        **option,
                    )
                option = {
                    "x": style.padding_left.get_pixel(),
                    "y": style.padding_top.get_pixel()
                    + process.style.margin_top.get_pixel(),
                }
                match style.layer_mode:
                    case LayerMode.SINGLE:
                        max_margin = max(
                            process.style.margin_left.get_pixel(),
                            remain_margin,
                        )
                        option["x"] += left_width + max_margin
                        video_process = ffmpeg.overlay(
                            video_process,
                            process.video,
                            eof_action="pass",
                            **option,
                        )
                        left_width += (
                            max_margin
                            + process.style.padding_left.get_pixel()
                            + process.style.width.get_pixel()
                            + process.style.padding_right.get_pixel()
                        )
                        remain_margin = process.style.margin_right.get_pixel()
                    case LayerMode.MULTI:
                        option["x"] += process.style.margin_left.get_pixel()
                        video_process = ffmpeg.overlay(
                            video_process,
                            process.video,
                            eof_action="pass",
                            **option,
                        )
                    case _:
                        raise Exception()

            # 音声の合成
            if process.audio:
                if process.style.time_margin_start.unit in [
                    TimeUnit.FRAME,
                    TimeUnit.SECOND,
                ]:
                    second = process.style.time_margin_start.get_second(fps)
                    process.audio = ffmpeg.filter(
                        process.audio,
                        "adelay",
                        all=1,
                        delays="{}s".format(second),
                    )
                if process.style.time_margin_end.unit in [
                    TimeUnit.FRAME,
                    TimeUnit.SECOND,
                ]:
                    second = process.style.time_margin_end.get_second(fps)
                    process.audio = ffmpeg.filter(
                        process.audio,
                        "apad",
                        pad_dur=second,
                    )
                if audio_process is None:
                    audio_process = process.audio
                else:
                    audio_process = ffmpeg.filter(
                        [audio_process, process.audio], "amix"
                    )
                if process.style.object_length:
                    audio_max_length = min(
                        style.object_length.get_second(fps),
                        max(
                            audio_max_length,
                            process.style.object_length.get_second(fps),
                        ),
                    )
        remain_audio_length = (
            style.object_length.get_second(fps) - audio_max_length
        )
        if remain_audio_length > 0 and audio_process:
            audio_process = ffmpeg.filter(
                audio_process,
                "apad",
                pad_dur=remain_audio_length,
            )

    return Process(
        video_process,
        audio_process,
        vsml_content.style,
    )

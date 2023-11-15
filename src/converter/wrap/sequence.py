import ffmpeg

from content import WrapContent
from converter.schemas import Process
from style import TimeUnit
from utils import VSMLManager


def create_sequence_process(
    processes: list[Process],
    vsml_content: WrapContent,
    debug_mode: bool = False,
) -> Process:
    video_process = None
    audio_process = None
    video_margin = 0
    audio_margin = 0

    fps = VSMLManager.get_root_fps()

    style = vsml_content.style

    background_color = (
        style.background_color.value
        if style.background_color
        else "0x00000000"
    )
    remain_time_margin = 0
    for child_process in processes:
        child_style = child_process.style

        if child_style.time_margin_start.unit in [
            TimeUnit.SECOND,
            TimeUnit.FRAME,
        ]:
            if child_process.video is not None:
                video_option = {}
                if child_style.time_margin_start.unit == TimeUnit.SECOND:
                    video_option = {
                        "start_duration": max(
                            child_style.time_margin_start.value,
                            remain_time_margin,
                        )
                    }
                if child_style.time_margin_start.unit == TimeUnit.FRAME:
                    remain_frame = remain_time_margin * fps
                    video_option = {
                        "start": max(
                            child_style.time_margin_start.value, remain_frame
                        )
                    }
                child_process.video = ffmpeg.filter(
                    child_process.video,
                    "tpad",
                    color=background_color,
                    **video_option,
                )
            else:
                delays = child_style.time_margin_start.get_second(fps)
                video_margin += max(delays, remain_time_margin)
            if child_process.audio is not None:
                delays = child_style.time_margin_start.get_second(fps)
                child_process.audio = ffmpeg.filter(
                    child_process.audio,
                    "adelay",
                    all=1,
                    delays="{}s".format(max(delays, remain_time_margin)),
                )
            else:
                delays = child_style.time_margin_start.get_second(fps)
                audio_margin += max(delays, remain_time_margin)

        if child_style.time_margin_end.unit in [
            TimeUnit.SECOND,
            TimeUnit.FRAME,
        ]:
            remain_time_margin = child_style.time_margin_end.get_second(fps)

        if child_process.video is not None:
            if video_margin > 0:
                child_process.video = ffmpeg.filter(
                    child_process.video,
                    "tpad",
                    color=background_color,
                    start_duration=video_margin,
                )
                video_margin = 0
            if video_process is None:
                video_process = child_process.video
            else:
                video_process = ffmpeg.concat(
                    video_process, child_process.video, v=1, a=0
                )
        else:
            video_margin += child_style.object_length.get_second(fps)
        if child_process.audio is not None:
            if audio_margin > 0:
                child_process.audio = ffmpeg.filter(
                    child_process.audio,
                    "adelay",
                    all=1,
                    delays="{}s".format(audio_margin),
                )
                audio_margin = 0
            if audio_process is None:
                audio_process = child_process.audio
            else:
                audio_process = ffmpeg.concat(
                    audio_process, child_process.audio, v=0, a=1
                )
        else:
            audio_margin += child_style.object_length.get_second(fps)
        if (
            child_style.object_length.unit == TimeUnit.FIT
            and child_style.source_object_length is None
        ):
            if video_process is not None and child_process.video is None:
                video_process = ffmpeg.filter(
                    video_process, "tpad", stop=-1, color=background_color
                )
            if audio_process is not None and child_process.audio is None:
                audio_process = ffmpeg.filter(
                    audio_process, "apad", pad_len=-1
                )
            video_margin = 0
            audio_margin = 0
            break

    # 余った時間マージンを追加する
    if video_process:
        if video_margin or remain_time_margin:
            video_process = ffmpeg.filter(
                video_process,
                "tpad",
                stop_duration=video_margin + remain_time_margin,
            )
    if audio_process:
        if audio_margin or remain_time_margin:
            audio_process = ffmpeg.filter(
                audio_process,
                "apad",
                pad_dur=audio_margin + remain_time_margin,
            )

    return Process(
        video_process,
        audio_process,
        vsml_content.style,
    )

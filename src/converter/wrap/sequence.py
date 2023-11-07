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
    # TODO: time_marginが重なるときに前のendと次のstartのmaxを取って1つ分のtime_marginを取る
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
                        "start_duration": child_style.time_margin_start.value
                    }
                if child_style.time_margin_start.unit == TimeUnit.FRAME:
                    video_option = {
                        "start": child_style.time_margin_start.value
                    }
                child_process.video = ffmpeg.filter(
                    child_process.video,
                    "tpad",
                    color=background_color,
                    **video_option,
                )
            if child_process.audio is not None:
                delays = child_style.time_margin_start.get_second(fps)
                child_process.audio = ffmpeg.filter(
                    child_process.audio,
                    "adelay",
                    delays=delays,
                )

        if child_style.time_margin_end.unit in [
            TimeUnit.SECOND,
            TimeUnit.FRAME,
        ]:
            if child_process.video is not None:
                video_option = {}
                if child_style.time_margin_end.unit == TimeUnit.SECOND:
                    video_option = {
                        "stop_duration": child_style.time_margin_end.value
                    }
                if child_style.time_margin_end.unit == TimeUnit.FRAME:
                    video_option = {"stop": child_style.time_margin_end.value}
                child_process.video = ffmpeg.filter(
                    child_process.video,
                    "tpad",
                    color=background_color,
                    **video_option,
                )
            if child_process.audio is not None:
                duration = child_style.time_margin_end.get_second(fps)
                child_process.audio = ffmpeg.filter(
                    child_process.audio,
                    "apad",
                    pad_dur=duration,
                )
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
                    color=background_color,
                    delays=audio_margin,
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
            # TODO: imageやtextなど長さ無限のもので、
            # video/audioの一方しか無いときに、もう一方の
            # 長さが無限になっていない
            video_margin = 0
            audio_margin = 0
            break

    # 余った時間マージンを追加する
    if video_margin and video_process:
        video_process = ffmpeg.filter(
            video_process, "tpad", stop_duration=video_margin
        )
    if audio_margin and audio_process:
        audio_process = ffmpeg.filter(
            audio_process, "apad", pad_dur=audio_margin
        )

    return Process(
        video_process,
        audio_process,
        vsml_content.style,
    )

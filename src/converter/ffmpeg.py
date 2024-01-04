# import time
import math
from typing import Any, Optional

import ffmpeg

from style import AudioSystem, Color, GraphicValue, TimeValue
from utils import VSMLManager

origin_background_processes = {}
origin_graphic_processes: dict[str, dict[str, Any]] = {}


def get_background_process(
    resolution_text: str, background_color: Optional[Color] = None
) -> Any:
    global origin_background_process
    key = "{}/{}".format(
        resolution_text,
        "transparent" if background_color is None else background_color.value,
    )
    origin_background_process = origin_background_processes.get(key)
    if origin_background_process is None:
        origin_background_process = ffmpeg.input(
            "rgbtestsrc=s={}".format(resolution_text),
            f="lavfi",
        )
        if background_color is None:
            origin_background_process = ffmpeg.filter(
                origin_background_process, "geq", a=0, r=0, g=0, b=0
            )
        else:
            origin_background_process = ffmpeg.filter(
                origin_background_process,
                "geq",
                a=background_color.a_value,
                r=background_color.r_value,
                g=background_color.g_value,
                b=background_color.b_value,
            )
    background_processes = origin_background_process.split()
    origin_background_processes[key] = background_processes[1]
    return background_processes[0]


def get_source_process(
    src_path: str, exist_video: bool, exist_audio: bool, **option
) -> dict[str, Any]:
    global origin_graphic_processes
    origin_graphic_process = origin_graphic_processes.get(src_path)
    if origin_graphic_process is None:
        process = ffmpeg.input(src_path, **option)
        origin_graphic_process = {
            "video": process.video if exist_video else None,
            "audio": process.audio if exist_audio else None,
        }
    video_graphic_processes = (
        origin_graphic_process["video"].split()
        if origin_graphic_process["video"] is not None
        else (None, None)
    )
    audio_graphic_processes = (
        origin_graphic_process["audio"].asplit()
        if origin_graphic_process["audio"] is not None
        else (None, None)
    )
    origin_graphic_processes[src_path] = {
        "video": video_graphic_processes[1],
        "audio": audio_graphic_processes[1],
    }
    return {
        "video": video_graphic_processes[0],
        "audio": audio_graphic_processes[0],
    }


def get_background_color_code(
    background_color: Optional[Color],
) -> str:
    return (
        background_color.value
        if background_color is not None
        else "0x00000000"
    )


def width_height_filter(
    width: GraphicValue,
    height: GraphicValue,
    video_process: Any,
) -> Any:
    if video_process is not None:
        if not (width.is_auto() and height.is_auto()):
            video_process = ffmpeg.filter(
                video_process,
                "scale",
                width.get_pixel(-1),
                height.get_pixel(-1),
            )
    return video_process


def audio_system_filter(
    source_audio_system: Optional[AudioSystem],
    audio_system: Optional[AudioSystem],
    audio_process: Any,
) -> Any:
    if audio_process is not None:
        if source_audio_system == AudioSystem.MONAURAL:
            audio_process = ffmpeg.filter(
                [audio_process, audio_process], "amerge", inputs=2
            )
        if (
            source_audio_system == AudioSystem.STEREO
            and audio_system == AudioSystem.MONAURAL
        ):
            # 一度MONAURALにマージした上で、他の音声との操作のためにSTEREOに複製する
            audio_process = ffmpeg.filter(audio_process, "amerge", inputs=1)
            audio_process = ffmpeg.filter(
                [audio_process, audio_process], "amerge", inputs=2
            )
    return audio_process


def audio_volume_filter(
    audio_volume: float,
    audio_process: Any,
) -> Any:
    if audio_process is not None:
        if audio_volume != 100:
            decibel = 20 * math.log10(audio_volume / 100)
            audio_process = ffmpeg.filter(
                audio_process, "volume", "{}dB".format(decibel)
            )
    return audio_process


def object_length_filter(
    object_length: TimeValue,
    video_process: Optional[Any] = None,
    audio_process: Optional[Any] = None,
) -> tuple[Any, Any]:
    if object_length.has_specific_value():
        length_second = object_length.get_second()
        if video_process is not None:
            video_process = ffmpeg.trim(video_process, end=length_second)
        if audio_process is not None:
            audio_process = ffmpeg.filter(
                audio_process,
                "atrim",
                end=length_second,
            )
    elif object_length.is_fit():
        if video_process is not None:
            video_process = ffmpeg.filter(
                video_process, "loop", loop=-1, size=32767, start=0
            )
        if audio_process is not None:
            audio_process = ffmpeg.filter(
                audio_process, "aloop", loop=-1, size=2147483647, start=0
            )
    return video_process, audio_process


def time_space_start_filter(
    time_space_start: TimeValue,
    background_color_code: Optional[str] = None,
    video_process: Optional[Any] = None,
    audio_process: Optional[Any] = None,
) -> tuple[Any, Any]:
    if time_space_start.has_specific_value():
        space_second = time_space_start.get_second()
        if video_process is not None:
            option = (
                {"color": background_color_code}
                if background_color_code is not None
                else {}
            )
            video_process = ffmpeg.filter(
                video_process,
                "tpad",
                start_duration=space_second,
                **option,
            )
        if audio_process is not None:
            delays = int(space_second * 1000)
            audio_process = ffmpeg.filter(
                audio_process,
                "adelay",
                all=1,
                delays=delays,
            )
    return video_process, audio_process


def time_space_end_filter(
    time_space_end: TimeValue,
    background_color_code: Optional[str] = None,
    video_process: Optional[Any] = None,
    audio_process: Optional[Any] = None,
) -> tuple[Any, Any]:
    if time_space_end.has_specific_value():
        space_second = time_space_end.get_second()
        if video_process is not None:
            option = (
                {"color": background_color_code}
                if background_color_code is not None
                else {}
            )
            video_process = ffmpeg.filter(
                video_process,
                "tpad",
                stop_duration=space_second,
                **option,
            )
        if audio_process is not None:
            audio_process = ffmpeg.filter(
                audio_process,
                "apad",
                pad_dur=space_second,
            )
    return video_process, audio_process


def concat_filter(
    base_process: Optional[Any], merging_process: Any, is_video: bool = True
) -> Any:
    if base_process is None:
        return merging_process
    else:
        return ffmpeg.concat(
            base_process, merging_process, v=int(is_video), a=int(not is_video)
        )


def audio_merge_filter(
    base_audio_process: Optional[Any],
    merging_audio_process: Any,
) -> Any:
    if base_audio_process is None:
        return merging_audio_process
    else:
        return ffmpeg.filter(
            [base_audio_process, merging_audio_process],
            "amix",
            normalize=False,
        )


def get_text_process(
    sentence: str,
    width: GraphicValue,
    height: GraphicValue,
    padding_left: GraphicValue,
    padding_top: GraphicValue,
    background_color: Optional[Color],
    font_family: Optional[str],
    font_size: Optional[GraphicValue],
    font_color: Optional[Color],
    font_border_color: Optional[Color],
    font_border_width: Optional[int],
) -> Any:
    option: dict = {
        "x": padding_left.get_pixel(),
        "y": padding_top.get_pixel(),
    }
    transparent_process = get_background_process(
        "{}x{}".format(
            width.get_pixel(),
            height.get_pixel(),
        ),
        background_color,
    )
    if font_family is not None:
        option |= {
            "font": font_family,
        }
    if font_size is not None:
        option |= {
            "fontsize": font_size.get_pixel(),
        }
    if font_color is not None:
        option |= {
            "fontcolor": font_color.value,
        }
    if font_border_color is not None:
        option |= {
            "bordercolor": font_border_color.value,
        }
    if font_border_width is not None:
        option |= {
            "borderw": font_border_width,
        }

    return ffmpeg.drawtext(
        transparent_process,
        text=sentence,
        **option,
    )


def adjust_parallel_audio(
    object_length: TimeValue,
    audio_process: Any,
) -> Any:
    option = {}
    if object_length.is_fit():
        option = {"whole_len": -1.0}
    else:
        option = {"whole_dur": object_length.get_second()}

    return ffmpeg.filter(
        audio_process,
        "apad",
        **option,
    )


def adjust_fit_sequence(
    background_color_code: str, video_process: Any, audio_process: Any
) -> tuple[Any, Any]:
    if video_process is not None:
        video_process = ffmpeg.filter(
            video_process, "tpad", stop=-1, color=background_color_code
        )
    if audio_process is not None:
        audio_process = ffmpeg.filter(audio_process, "apad", pad_len=-1)
    return video_process, audio_process


def set_background_filter(
    width: Optional[GraphicValue] = None,
    height: Optional[GraphicValue] = None,
    background_color: Optional[Color] = None,
    resolution_text: Optional[str] = None,
    video_process: Optional[Any] = None,
    fit_video_process: bool = False,
    position_x: Optional[GraphicValue] = None,
    position_y: Optional[GraphicValue] = None,
) -> Any:
    resolution = ""
    if resolution_text is not None:
        resolution = resolution_text
    elif width is not None and height is not None:
        resolution = "{}x{}".format(
            width.get_pixel(),
            height.get_pixel(),
        )
    else:
        raise Exception()
    background_process = get_background_process(resolution, background_color)

    return layering_filter(
        background_process,
        video_process,
        position_x,
        position_y,
        fit_video_process,
    )


def layering_filter(
    base_video_process: Optional[Any],
    merging_video_process: Any,
    position_x: Optional[GraphicValue] = None,
    position_y: Optional[GraphicValue] = None,
    fit_shorter: bool = False,
) -> Any:
    option = {}
    if position_x is not None:
        option |= {"x": position_x.get_pixel()}
    if position_y is not None:
        option |= {"y": position_y.get_pixel()}

    if base_video_process is None:
        return merging_video_process
    elif merging_video_process is None:
        return base_video_process
    else:
        return ffmpeg.overlay(
            base_video_process,
            merging_video_process,
            eof_action="pass",
            shortest=fit_shorter,
            **option,
        )


def export_video(
    video_process: Optional[Any],
    audio_process: Optional[Any],
    out_filename: str,
    debug_mode: bool,
    overwrite: bool,
):
    match (
        video_process,
        audio_process,
    ):
        case None, None:
            raise Exception()
        case _, None:
            process = video_process
        case None, _:
            process = audio_process
        case _:
            process = ffmpeg.concat(
                video_process,
                audio_process,
                v=1,
                a=1,
                n=1,
            )
    process = ffmpeg.output(
        process,
        out_filename,
        r=VSMLManager.get_root_fps(),
    )

    if debug_mode:
        # ffmpeg.view(process)
        # time.sleep(0.1)
        print("\n[[[command args]]]\n{}".format(ffmpeg.compile(process)))

    ffmpeg.run(
        process,
        overwrite_output=overwrite,
    )

import math
from typing import Any, Optional

import ffmpeg

from style import (
    AudioSystem,
    Color,
    GraphicUnit,
    GraphicValue,
    TimeUnit,
    TimeValue,
)

from .utils import get_background_process


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
        if width.unit != GraphicUnit.AUTO or height.unit != GraphicUnit.AUTO:
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
    if object_length.unit in [TimeUnit.FRAME, TimeUnit.SECOND]:
        if video_process is not None:
            option = {}
            if object_length.unit == TimeUnit.FRAME:
                option = {"end_frame": object_length.value + 1}
            elif object_length.unit == TimeUnit.SECOND:
                option = {"end": object_length.value}
            video_process = ffmpeg.trim(video_process, **option)
        if audio_process is not None:
            audio_end = object_length.get_second()
            audio_process = ffmpeg.filter(
                audio_process,
                "atrim",
                end=audio_end,
            )
    elif object_length.unit == TimeUnit.FIT:
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
    if time_space_start.unit in [TimeUnit.FRAME, TimeUnit.SECOND]:
        if video_process is not None:
            option = {}
            if time_space_start.unit == TimeUnit.FRAME:
                option = {"start": time_space_start.value}
            elif time_space_start.unit == TimeUnit.SECOND:
                option = {
                    "start_duration": time_space_start.value,
                }
            video_process = ffmpeg.filter(
                video_process,
                "tpad",
                color=background_color_code,
                **option,
            )
        if audio_process is not None:
            delays = int(time_space_start.get_second() * 1000)
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
    if time_space_end.unit in [TimeUnit.FRAME, TimeUnit.SECOND]:
        if video_process is not None:
            option = {}
            if time_space_end.unit == TimeUnit.FRAME:
                option = {
                    "stop": time_space_end.value,
                }
            elif time_space_end.unit == TimeUnit.SECOND:
                option = {
                    "stop_duration": time_space_end.value,
                }
            video_process = ffmpeg.filter(
                video_process, "tpad", color=background_color_code, **option
            )
        if audio_process is not None:
            pad_dur = time_space_end.get_second()
            audio_process = ffmpeg.filter(
                audio_process, "apad", pad_dur=pad_dur
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


def adjust_parallel_audio(
    object_length: TimeValue,
    audio_process: Any,
) -> Any:
    option = {}
    if object_length.unit == TimeUnit.FIT:
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
    width: GraphicValue,
    height: GraphicValue,
    background_color: Optional[Color],
    video_process: Optional[Any] = None,
    fit_video_process: bool = False,
    position_x: Optional[GraphicValue] = None,
    position_y: Optional[GraphicValue] = None,
) -> Any:
    background_process = get_background_process(
        "{}x{}".format(
            width.get_pixel(),
            height.get_pixel(),
        ),
        background_color,
    )
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

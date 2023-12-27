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
from utils import VSMLManager


def get_background_color_code(
    background_color: Optional[Color],
) -> str:
    return background_color.value if background_color else "0x00000000"


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
            audio_end = object_length.get_second(VSMLManager.get_root_fps())
            audio_process = ffmpeg.filter(
                audio_process,
                "atrim",
                end=audio_end,
            )
    return video_process, audio_process


def time_padding_start_filter(
    time_padding_start: TimeValue,
    background_color_code: Optional[str] = None,
    video_process: Optional[Any] = None,
    audio_process: Optional[Any] = None,
) -> tuple[Any, Any]:
    if time_padding_start.unit in [TimeUnit.FRAME, TimeUnit.SECOND]:
        if video_process is not None:
            option = {}
            if time_padding_start.unit == TimeUnit.FRAME:
                option = {"start": time_padding_start.value}
            elif time_padding_start.unit == TimeUnit.SECOND:
                option = {
                    "start_duration": time_padding_start.value,
                }
            video_process = ffmpeg.filter(
                video_process,
                "tpad",
                color=background_color_code,
                **option,
            )
        if audio_process is not None:
            delays = int(
                time_padding_start.get_second(VSMLManager.get_root_fps())
                * 1000
            )
            audio_process = ffmpeg.filter(
                audio_process,
                "adelay",
                all=1,
                delays=delays,
            )
    return video_process, audio_process


def time_padding_end_filter(
    time_padding_end: TimeValue,
    background_color_code: Optional[str] = None,
    video_process: Optional[Any] = None,
    audio_process: Optional[Any] = None,
) -> tuple[Any, Any]:
    if time_padding_end.unit in [TimeUnit.FRAME, TimeUnit.SECOND]:
        if video_process is not None:
            option = {}
            if time_padding_end.unit == TimeUnit.FRAME:
                option = {
                    "stop": time_padding_end.value,
                }
            elif time_padding_end.unit == TimeUnit.SECOND:
                option = {
                    "stop_duration": time_padding_end.value,
                }
            video_process = ffmpeg.filter(
                video_process, "tpad", color=background_color_code, **option
            )
        if audio_process is not None:
            pad_dur = time_padding_end.get_second(VSMLManager.get_root_fps())
            audio_process = ffmpeg.filter(
                audio_process, "apad", pad_dur=pad_dur
            )
    return video_process, audio_process
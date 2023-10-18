import re
from typing import Optional

from .types import (
    AudioSystem,
    Color,
    GraphicValue,
    Order,
    TimeValue,
)


def time_parser(
    value: str,
) -> Optional[TimeValue]:
    try:
        return TimeValue(value)
    except ValueError:
        return


def double_time_parser(
    value: str,
) -> Optional[tuple[TimeValue, TimeValue]]:
    value_list = re.split(r"\s+", value)
    match len(value_list):
        case 1:
            try:
                time_value = TimeValue(value_list[0])
                return (
                    time_value,
                    time_value,
                )
            except ValueError:
                return
        case 2:
            try:
                return (
                    TimeValue(value_list[0]),
                    TimeValue(value_list[1]),
                )
            except ValueError:
                return
        case _:
            return


def graphic_parser(
    value: str,
) -> Optional[GraphicValue]:
    try:
        return GraphicValue(value)
    except ValueError:
        return


def multi_graphic_parser(
    value: str,
) -> Optional[tuple[GraphicValue, GraphicValue, GraphicValue, GraphicValue,]]:
    value_list = re.split(r"\s+", value)
    match len(value_list):
        case 1:
            try:
                graphic_value = GraphicValue(value_list[0])
                return (
                    graphic_value,
                    graphic_value,
                    graphic_value,
                    graphic_value,
                )
            except ValueError:
                return
        case 2:
            try:
                graphic_value = (
                    GraphicValue(value_list[0]),
                    GraphicValue(value_list[1]),
                )
                return (
                    graphic_value[0],
                    graphic_value[1],
                    graphic_value[0],
                    graphic_value[1],
                )
            except ValueError:
                return
        case 3:
            try:
                graphic_value = (
                    GraphicValue(value_list[0]),
                    GraphicValue(value_list[1]),
                    GraphicValue(value_list[2]),
                )
                return (
                    graphic_value[0],
                    graphic_value[1],
                    graphic_value[2],
                    graphic_value[1],
                )
            except ValueError:
                return
        case 4:
            try:
                return (
                    GraphicValue(value_list[0]),
                    GraphicValue(value_list[1]),
                    GraphicValue(value_list[2]),
                    GraphicValue(value_list[3]),
                )
            except ValueError:
                return
        case _:
            return


def pixel_parser(
    value: str,
) -> Optional[int]:
    if value[-2:] == "px":
        return int(value[:-2])


def font_weight_parser(
    value: str,
) -> Optional[bool]:
    match value:
        case "bold":
            return True
        case "normal":
            return False


def font_style_parser(
    value: str,
) -> Optional[bool]:
    match value:
        case "italic":
            return True
        case "normal":
            return False


def order_parser(
    value: str,
) -> Optional[Order]:
    match value:
        case "sequence":
            return Order.SEQUENCE
        case "parallel":
            return Order.PARALLEL


def audio_system_parser(
    value: str,
) -> Optional[AudioSystem]:
    match value:
        case "monaural":
            return AudioSystem.MONAURAL
        case "stereo":
            return AudioSystem.STEREO


def color_parser(
    value: str,
) -> Optional[Color]:
    try:
        return Color(value)
    except ValueError:
        return


def percentage_parser(
    value: str,
) -> Optional[float]:
    if value[-1:] == "%":
        return int(value[:-1])


def color_and_pixel_parser(
    value: str,
) -> Optional[tuple[Color, int]]:
    value_list = re.split(r"\s+", value)
    if len(value_list) == 2:
        pixel = pixel_parser(value_list[0])
        if pixel is not None:
            try:
                return (
                    Color(value_list[1]),
                    pixel,
                )
            except Exception:
                return
        else:
            pixel = pixel_parser(value_list[1])
            if pixel is not None:
                try:
                    return (
                        Color(value_list[0]),
                        pixel,
                    )
                except Exception:
                    return

from __future__ import annotations

from typing import Optional

import ffmpeg
from lxml.etree import _Attrib

from style import GraphicUnit, TimeUnit
from utils import TagInfoTree, VSMLManager

from .styling_parser import (
    audio_system_parser,
    color_and_pixel_parser,
    color_parser,
    double_time_parser,
    font_style_parser,
    font_weight_parser,
    graphic_parser,
    multi_graphic_parser,
    order_parser,
    percentage_parser,
    pixel_parser,
    time_parser,
)
from .types import AudioSystem, Color, GraphicValue, Order, TimeValue


class Style:
    # style param
    # time param
    object_length: TimeValue = TimeValue("fit")
    time_margin_start: TimeValue
    time_margin_end: TimeValue
    time_padding_start: TimeValue
    time_padding_end: TimeValue
    order: Optional[Order] = None
    # visual param
    width: GraphicValue = GraphicValue("auto")
    height: GraphicValue = GraphicValue("auto")
    margin_top: GraphicValue
    margin_left: GraphicValue
    margin_right: GraphicValue
    margin_bottom: GraphicValue
    padding_top: GraphicValue
    padding_left: GraphicValue
    padding_right: GraphicValue
    padding_bottom: GraphicValue
    background_color: Optional[Color] = None
    # audio param
    audio_volume: float = 100
    audio_system: Optional[AudioSystem] = None  # inherit
    # text tag param
    font_color: Optional[Color] = None  # inherit
    font_border_color: Optional[Color] = None  # inherit
    font_border_width: Optional[int] = None  # inherit
    font_family: Optional[str] = None  # inherit
    font_size: Optional[GraphicValue] = None  # inherit
    font_weight: Optional[bool] = None  # inherit
    font_style: Optional[bool] = None  # inherit

    # 各タグのデフォルトparam
    def __init__(
        self,
        tag_name: str,
        parent_param: Optional[Style],
        source_value: str,
        style_tree: dict[str, str],
        attrib: _Attrib,
    ) -> None:
        # inheriting
        if parent_param is not None:
            if parent_param.audio_system is not None:
                self.audio_system = parent_param.audio_system
            if parent_param.font_color is not None:
                self.font_color = parent_param.font_color
            if parent_param.font_border_color is not None:
                self.font_border_color = parent_param.font_border_color
            if parent_param.font_border_width is not None:
                self.font_border_width = parent_param.font_border_width
            if parent_param.font_family is not None:
                self.font_family = parent_param.font_family
            if parent_param.font_size is not None:
                self.font_size = parent_param.font_size
            if parent_param.font_weight is not None:
                self.font_weight = parent_param.font_weight
            if parent_param.font_style is not None:
                self.font_style = parent_param.font_style

        source_object_length = None
        source_width = None
        source_height = None
        match tag_name:
            case "cont":
                self.order = Order.SEQUENCE
            case "wrp":
                self.order = Order.SEQUENCE
            case "seq":
                self.order = Order.SEQUENCE
            case "rect":
                self.order = Order.SEQUENCE
            case "prl":
                self.order = Order.PARALLEL
            case "layer":
                self.order = Order.PARALLEL
            case "vid":
                meta = ffmpeg.probe(source_value)
                (
                    object_length,
                    meta_video,
                    meta_audio,
                ) = self._get_info_from_meta(meta)
                if object_length is None or meta_video is None:
                    raise Exception()
                source_object_length = TimeValue("{}s".format(object_length))
                self.object_length = TimeValue("source")
                source_width = graphic_parser(meta_video["width"] + "px")
                source_height = graphic_parser(meta_video["height"] + "px")
                if meta_audio is not None:
                    audio_system = (
                        AudioSystem.STEREO
                        if meta_audio.get("channel_layout") == "stereo"
                        else AudioSystem.MONAURAL
                    )
                    self.audio_system = (
                        self.audio_system
                        if self.audio_system == AudioSystem.MONAURAL
                        else audio_system
                    )
            case "aud":
                meta = ffmpeg.probe(source_value)
                (
                    object_length,
                    meta_video,
                    meta_audio,
                ) = self._get_info_from_meta(meta)
                if object_length is None or meta_audio is None:
                    raise Exception()
                source_object_length = TimeValue("{}s".format(object_length))
                self.object_length = TimeValue("source")
                audio_system = (
                    AudioSystem.STEREO
                    if meta_audio.get("channel_layout") == "stereo"
                    else AudioSystem.MONAURAL
                )
                self.audio_system = (
                    self.audio_system
                    if self.audio_system == AudioSystem.MONAURAL
                    else audio_system
                )
            case "img":
                meta = ffmpeg.probe(source_value)
                (
                    object_length,
                    meta_video,
                    meta_audio,
                ) = self._get_info_from_meta(meta)
                if meta_video is None:
                    raise Exception()
                source_width = graphic_parser(meta_video["width"] + "px")
                source_height = graphic_parser(meta_video["height"] + "px")
            case "txt":
                self.font_color = (
                    self.font_color if self.font_color else Color("white")
                )
                self.font_family = (
                    self.font_family if self.font_family else "MS Gothic"
                )
                self.font_size = (
                    self.font_size if self.font_size else GraphicValue("30px")
                )
                # TODO: ここGlyphを使用してサイズを計算する
                source_width = graphic_parser("100px")
                source_height = graphic_parser("100px")
            case _:
                raise Exception()

        # set styling_sheet param
        for (
            param,
            value,
        ) in style_tree.items():
            match param:
                case "object-length":
                    parse_value = time_parser(value)
                    if parse_value is not None:
                        self.object_length = parse_value
                case "time-margin":
                    parse_value = double_time_parser(value)
                    if parse_value is not None:
                        (
                            self.time_margin_start,
                            self.time_margin_end,
                        ) = parse_value
                case "time-margin-start":
                    parse_value = time_parser(value)
                    if parse_value is not None:
                        self.time_margin_start = parse_value
                case "time-margin-end":
                    parse_value = time_parser(value)
                    if parse_value is not None:
                        self.time_margin_end = parse_value
                case "time-padding":
                    parse_value = double_time_parser(value)
                    if parse_value is not None:
                        (
                            self.time_padding_start,
                            self.time_padding_end,
                        ) = parse_value
                case "time-padding-start":
                    parse_value = time_parser(value)
                    if parse_value is not None:
                        self.time_padding_start = parse_value
                case "time-padding-end":
                    parse_value = time_parser(value)
                    if parse_value is not None:
                        self.time_padding_end = parse_value
                case "order":
                    parse_value = order_parser(value)
                    if parse_value is not None:
                        self.order = parse_value
                case "width":
                    parse_value = graphic_parser(value)
                    if parse_value is not None:
                        self.width = parse_value
                case "height":
                    parse_value = graphic_parser(value)
                    if parse_value is not None:
                        self.height = parse_value
                case "margin":
                    parse_value = multi_graphic_parser(value)
                    if parse_value is not None:
                        (
                            self.margin_top,
                            self.margin_right,
                            self.margin_bottom,
                            self.margin_left,
                        ) = parse_value
                case "margin-top":
                    parse_value = graphic_parser(value)
                    if parse_value is not None:
                        self.margin_top = parse_value
                case "margin-right":
                    parse_value = graphic_parser(value)
                    if parse_value is not None:
                        self.margin_right = parse_value
                case "margin-bottom":
                    parse_value = graphic_parser(value)
                    if parse_value is not None:
                        self.margin_bottom = parse_value
                case "margin-left":
                    parse_value = graphic_parser(value)
                    if parse_value is not None:
                        self.margin_left = parse_value
                case "padding":
                    parse_value = multi_graphic_parser(value)
                    if parse_value is not None:
                        (
                            self.padding_top,
                            self.padding_right,
                            self.padding_bottom,
                            self.padding_left,
                        ) = parse_value
                case "padding-top":
                    parse_value = graphic_parser(value)
                    if parse_value is not None:
                        self.padding_top = parse_value
                case "padding-right":
                    parse_value = graphic_parser(value)
                    if parse_value is not None:
                        self.padding_right = parse_value
                case "padding-bottom":
                    parse_value = graphic_parser(value)
                    if parse_value is not None:
                        self.padding_bottom = parse_value
                case "padding-left":
                    parse_value = graphic_parser(value)
                    if parse_value is not None:
                        self.padding_left = parse_value
                case "background-color":
                    parse_value = color_parser(value)
                    if parse_value is not None:
                        self.background_color = parse_value
                case "audio-volume":
                    parse_value = percentage_parser(value)
                    if parse_value is not None:
                        self.audio_volume = parse_value
                case "audio-system":
                    parse_value = audio_system_parser(value)
                    if parse_value is not None:
                        self.audio_system = parse_value
                case "font-color":
                    parse_value = color_parser(value)
                    if parse_value is not None:
                        self.background_color = parse_value
                case "font-border":
                    parse_value = color_and_pixel_parser(value)
                    if parse_value is not None:
                        (
                            self.font_border_color,
                            self.font_border_width,
                        ) = parse_value
                case "font-border-color":
                    parse_value = color_parser(value)
                    if parse_value is not None:
                        self.background_color = parse_value
                case "font-border-width":
                    parse_value = pixel_parser(value)
                    if parse_value is not None:
                        self.font_border_width = parse_value
                case "font-family":
                    self.font_family = value
                case "font-size":
                    parse_value = graphic_parser(value)
                    if parse_value is not None:
                        self.font_size = parse_value
                case "font-weight":
                    parse_value = font_weight_parser(value)
                    if parse_value is not None:
                        self.font_border_width = parse_value
                case "font-style":
                    parse_value = font_style_parser(value)
                    if parse_value is not None:
                        self.font_border_width = parse_value
                case _:
                    continue

        # set attrib style param
        match tag_name:
            case "rect":
                background_color = attrib.get("color")
                if background_color is not None:
                    self.background_color = Color(background_color)
            case _:
                pass

        # calculate param
        if source_object_length is not None:
            match self.object_length.unit:
                case TimeUnit.SOURCE:
                    self.object_length = source_object_length
                case TimeUnit.PERCENT:
                    if (
                        parent_param is not None
                        and parent_param.object_length is not None
                        and parent_param.object_length.unit
                        in [TimeUnit.SECOND, TimeUnit.FRAME]
                    ):
                        self.object_length.value = (
                            parent_param.object_length.value
                            * self.object_length.value
                            / 100
                        )
                        self.object_length.unit = (
                            parent_param.object_length.unit
                        )
                    else:
                        self.object_length = source_object_length
        if source_width is not None:
            match self.width.unit:
                case GraphicUnit.AUTO:
                    self.width = source_width
                case GraphicUnit.PERCENT:
                    if (
                        parent_param is not None
                        and parent_param.width is not None
                        and parent_param.width.unit == GraphicUnit.PIXEL
                    ):
                        self.width.value = (
                            parent_param.width.value * self.width.value / 100
                        )
                        self.width.unit = parent_param.width.unit
                    else:
                        self.width = source_width
                case GraphicUnit.RESOLUTION_WIDTH:
                    self.width.value = (
                        VSMLManager.get_root_resolution().width
                        * self.width.value
                        / 100
                    )
                    self.width.unit = GraphicUnit.PIXEL
                case GraphicUnit.RESOLUTION_HEIGHT:
                    self.width.value = (
                        VSMLManager.get_root_resolution().height
                        * self.width.value
                        / 100
                    )
                    self.width.unit = GraphicUnit.PIXEL
                case GraphicUnit.RESOLUTION_MIN:
                    self.width.value = (
                        VSMLManager.get_root_resolution().get_min()
                        * self.width.value
                        / 100
                    )
                    self.width.unit = GraphicUnit.PIXEL
                case GraphicUnit.RESOLUTION_MAX:
                    self.width.value = (
                        VSMLManager.get_root_resolution().get_max()
                        * self.width.value
                        / 100
                    )
                    self.width.unit = GraphicUnit.PIXEL

        if source_height is not None:
            match self.height.unit:
                case GraphicUnit.AUTO:
                    self.height = source_height
                case GraphicUnit.PERCENT:
                    if (
                        parent_param is not None
                        and parent_param.height is not None
                        and parent_param.height.unit == GraphicUnit.PIXEL
                    ):
                        self.height.value = (
                            parent_param.height.value * self.height.value / 100
                        )
                        self.height.unit = parent_param.height.unit
                    else:
                        self.height = source_height
                case GraphicUnit.RESOLUTION_WIDTH:
                    self.height.value = (
                        VSMLManager.get_root_resolution().width
                        * self.height.value
                        / 100
                    )
                    self.height.unit = GraphicUnit.PIXEL
                case GraphicUnit.RESOLUTION_HEIGHT:
                    self.height.value = (
                        VSMLManager.get_root_resolution().height
                        * self.height.value
                        / 100
                    )
                    self.height.unit = GraphicUnit.PIXEL
                case GraphicUnit.RESOLUTION_MIN:
                    self.height.value = (
                        VSMLManager.get_root_resolution().get_min()
                        * self.height.value
                        / 100
                    )
                    self.height.unit = GraphicUnit.PIXEL
                case GraphicUnit.RESOLUTION_MAX:
                    self.height.value = (
                        VSMLManager.get_root_resolution().get_max()
                        * self.height.value
                        / 100
                    )
                    self.height.unit = GraphicUnit.PIXEL

    def _get_info_from_meta(
        self, meta: dict
    ) -> tuple[Optional[str], Optional[dict], Optional[dict],]:
        duration = meta.get("format", {}).get("duration", None)
        meta_video = None
        meta_audio = None
        stream_info = meta.get("streams", [])
        for stream in stream_info:
            if meta_video is None and stream.get("codec_type") == "video":
                meta_video = stream
                continue
            if meta_audio is None and stream.get("codec_type") == "audio":
                meta_audio = stream
                continue
            if meta_video is not None and meta_audio is not None:
                break
        return (
            duration,
            meta_video,
            meta_audio,
        )

    def __repr__(self) -> str:
        return str(vars(self))


def pickup_style(
    style_tree: dict[str, dict[str, str]],
    tag_name: str,
    class_name: list[str],
    id_name: Optional[str],
    parent_info_tree: Optional[TagInfoTree] = None,
) -> dict[str, str]:
    picked_up_style = {}
    for (
        selectors,
        style,
    ) in style_tree.items():
        checking_selector = selectors.split(" ")
        checking_selector.reverse()
        target_selector = checking_selector.pop(0)
        match target_selector[0]:
            case ".":
                if target_selector[1:] not in class_name:
                    continue
            case "#":
                if target_selector[1:] != id_name:
                    continue
            case _:
                if target_selector != tag_name:
                    continue

        if len(checking_selector) == 0:
            picked_up_style |= style
            continue

        info_tree = parent_info_tree
        while info_tree:
            target_selector = checking_selector[0]
            match target_selector[0]:
                case ".":
                    if target_selector[1:] in class_name:
                        checking_selector.pop(0)
                case "#":
                    if target_selector[1:] == id_name:
                        checking_selector.pop(0)
                case _:
                    if target_selector == tag_name:
                        checking_selector.pop(0)
            info_tree = info_tree.parent

        if len(checking_selector) == 0:
            picked_up_style |= style
            continue
    return picked_up_style

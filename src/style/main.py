from __future__ import annotations

from typing import Optional

from ffmpeg import probe as ffprobe
from lxml.etree import _Attrib

from utils import TagInfoTree, VSMLManager

from .calculator import graphic_calculator, time_calculator
from .styling_parser import (
    audio_system_parser,
    color_and_pixel_parser,
    color_parser,
    direction_parser,
    double_time_parser,
    font_style_parser,
    font_weight_parser,
    graphic_parser,
    layer_mode_parser,
    multi_graphic_parser,
    order_parser,
    percentage_parser,
    pixel_parser,
    time_parser,
)
from .types import (
    AudioSystem,
    Color,
    DirectionInfo,
    GraphicValue,
    LayerMode,
    Order,
    TimeValue,
)


class Style:
    # style param
    # time param
    object_length: TimeValue
    time_margin_start: TimeValue
    time_margin_end: TimeValue
    time_padding_start: TimeValue
    time_padding_end: TimeValue
    order: Optional[Order]
    # visual param
    width: GraphicValue
    height: GraphicValue
    layer_mode: Optional[LayerMode]
    direction: Optional[DirectionInfo]
    margin_top: GraphicValue
    margin_left: GraphicValue
    margin_right: GraphicValue
    margin_bottom: GraphicValue
    padding_top: GraphicValue
    padding_left: GraphicValue
    padding_right: GraphicValue
    padding_bottom: GraphicValue
    background_color: Optional[Color]
    # audio param
    audio_volume: float  # inherit
    audio_system: Optional[AudioSystem]  # inherit
    # text tag param
    font_color: Optional[Color]  # inherit
    font_border_color: Optional[Color]  # inherit
    font_border_width: Optional[int]  # inherit
    font_family: Optional[str]  # inherit
    font_size: Optional[GraphicValue]  # inherit
    font_weight: Optional[bool]  # inherit
    font_style: Optional[bool]  # inherit
    # source value
    source_object_length: Optional[TimeValue]
    source_width: Optional[GraphicValue]
    source_height: Optional[GraphicValue]
    source_audio_system: Optional[AudioSystem]

    # 各タグのデフォルトparam
    def __init__(
        self,
        tag_name: str,
        parent_param: Optional[Style],
        source_value: str,
        style_tree: dict[str, str],
        attrib: _Attrib,
    ) -> None:
        # initializing
        self.object_length = TimeValue("fit")
        self.time_margin_start = TimeValue("fit")
        self.time_margin_end = TimeValue("fit")
        self.time_padding_start = TimeValue("fit")
        self.time_padding_end = TimeValue("fit")
        self.order = None
        self.width = GraphicValue("auto")
        self.height = GraphicValue("auto")
        self.layer_mode = None
        self.direction = None
        self.margin_top = GraphicValue("auto")
        self.margin_left = GraphicValue("auto")
        self.margin_right = GraphicValue("auto")
        self.margin_bottom = GraphicValue("auto")
        self.padding_top = GraphicValue("auto")
        self.padding_left = GraphicValue("auto")
        self.padding_right = GraphicValue("auto")
        self.padding_bottom = GraphicValue("auto")
        self.background_color = None
        self.audio_volume = 100
        self.audio_system = None
        self.font_color = None
        self.font_border_color = None
        self.font_border_width = None
        self.font_family = None
        self.font_size = None
        self.font_weight = None
        self.font_style = None
        self.source_object_length = None
        self.source_width = None
        self.source_height = None
        self.source_audio_system = None

        # inheriting
        if parent_param is not None:
            if parent_param.audio_volume is not None:
                self.audio_volume = parent_param.audio_volume
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

        match tag_name:
            case "cont":
                self.order = Order.SEQUENCE
                self.layer_mode = LayerMode.MULTI
                self.direction = DirectionInfo("row")
            case "wrp":
                self.order = Order.SEQUENCE
                self.layer_mode = LayerMode.MULTI
                self.direction = DirectionInfo("row")
            case "seq":
                self.order = Order.SEQUENCE
                self.layer_mode = LayerMode.MULTI
                self.direction = DirectionInfo("row")
            case "rect":
                self.order = Order.SEQUENCE
                self.layer_mode = LayerMode.MULTI
                self.direction = DirectionInfo("row")
            case "prl":
                self.order = Order.PARALLEL
                self.layer_mode = LayerMode.MULTI
                self.direction = DirectionInfo("row")
            case "layer":
                self.order = Order.PARALLEL
                self.layer_mode = LayerMode.SINGLE
                self.direction = DirectionInfo("row")
            case "vid":
                meta = ffprobe(source_value)
                (
                    object_length,
                    meta_video,
                    meta_audio,
                ) = self._get_info_from_meta(meta)
                if object_length is None or meta_video is None:
                    raise Exception()
                self.object_length = TimeValue("source")
                self.source_object_length = TimeValue(
                    "{}s".format(object_length)
                )
                width = meta_video["width"]
                height = meta_video["height"]
                self.source_width = graphic_parser(f"{width}px")
                self.source_height = graphic_parser(f"{height}px")
                if meta_audio is not None:
                    channel_layout = meta_audio.get("channel_layout")
                    match channel_layout:
                        case "stereo":
                            self.source_audio_system = AudioSystem.STEREO
                        case "monaural":
                            self.source_audio_system = AudioSystem.STEREO
                    if self.audio_system == AudioSystem.STEREO:
                        self.audio_system = self.audio_system
            case "aud":
                meta = ffprobe(source_value)
                (
                    object_length,
                    meta_video,
                    meta_audio,
                ) = self._get_info_from_meta(meta)
                if object_length is None or meta_audio is None:
                    raise Exception()
                self.object_length = TimeValue("source")
                self.source_object_length = TimeValue(
                    "{}s".format(object_length)
                )
                channel_layout = meta_audio.get("channel_layout")
                match channel_layout:
                    case "stereo":
                        self.source_audio_system = AudioSystem.STEREO
                    case "monaural":
                        self.source_audio_system = AudioSystem.STEREO
                if self.audio_system == AudioSystem.STEREO:
                    self.audio_system = self.audio_system
            case "img":
                meta = ffprobe(source_value)
                (
                    object_length,
                    meta_video,
                    meta_audio,
                ) = self._get_info_from_meta(meta)
                if meta_video is None:
                    raise Exception()
                width = meta_video["width"]
                height = meta_video["height"]
                self.source_width = graphic_parser(f"{width}px")
                self.source_height = graphic_parser(f"{height}px")
            case "txt":
                if self.font_color is None:
                    self.font_color = Color("white")
                if self.font_size is None:
                    self.font_size = GraphicValue("30px")
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
                case "direction":
                    parse_value = direction_parser(value)
                    if parse_value is not None:
                        self.direction = parse_value
                case "width":
                    parse_value = graphic_parser(value)
                    if parse_value is not None:
                        self.width = parse_value
                case "height":
                    parse_value = graphic_parser(value)
                    if parse_value is not None:
                        self.height = parse_value
                case "layer-mode":
                    parse_value = layer_mode_parser(value)
                    if parse_value is not None:
                        self.layer_mode = parse_value
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
                        self.font_color = parse_value
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
                        self.font_weight = parse_value
                case "font-style":
                    parse_value = font_style_parser(value)
                    if parse_value is not None:
                        self.font_style = parse_value
                case _:
                    continue

        # set attrib style param
        match tag_name:
            case "rect":
                background_color = attrib.get("color")
                if background_color is not None:
                    self.background_color = Color(background_color)
            case "txt":
                if self.font_size is not None:
                    text_lines = source_value.split(r"\n")
                    self.source_width = graphic_parser(
                        "{}px".format(
                            max(map(len, text_lines))
                            * self.font_size.get_pixel()
                        )
                    )
                    self.source_height = graphic_parser(
                        "{}px".format(
                            len(text_lines) * self.font_size.get_pixel()
                        )
                    )
            case _:
                pass

        # calculate param
        parent_object_length = (
            parent_param.object_length
            if (
                parent_param is not None
                and parent_param.object_length.has_specific_value()
            )
            else None
        )
        self.object_length = time_calculator(
            self.object_length,
            parent_object_length,
            self.source_object_length,
        )
        self.time_margin_start = time_calculator(
            self.time_margin_start,
            parent_object_length,
        )
        self.time_margin_end = time_calculator(
            self.time_margin_end,
            parent_object_length,
        )
        self.time_padding_start = time_calculator(
            self.time_padding_start,
            parent_object_length,
        )
        self.time_padding_end = time_calculator(
            self.time_padding_end,
            parent_object_length,
        )

        parent_width = (
            VSMLManager.get_root_resolution().width
            if parent_param is None
            else (
                parent_param.width.value
                if parent_param.width.has_specific_value()
                else None
            )
        )
        parent_height = (
            VSMLManager.get_root_resolution().height
            if parent_param is None
            else (
                parent_param.height.value
                if parent_param.height.has_specific_value()
                else None
            )
        )
        self.width = graphic_calculator(
            self.width, parent_width, self.source_width
        )
        self.height = graphic_calculator(
            self.height, parent_height, self.source_height
        )
        self.margin_left = graphic_calculator(self.margin_left, parent_width)
        self.margin_right = graphic_calculator(self.margin_right, parent_width)
        self.margin_top = graphic_calculator(self.margin_top, parent_height)
        self.margin_bottom = graphic_calculator(
            self.margin_bottom, parent_height
        )
        self.padding_left = graphic_calculator(self.padding_left, parent_width)
        self.padding_right = graphic_calculator(
            self.padding_right, parent_width
        )
        self.padding_top = graphic_calculator(self.padding_top, parent_height)
        self.padding_bottom = graphic_calculator(
            self.padding_bottom, parent_height
        )

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

    def get_size_with_padding(self) -> tuple[GraphicValue, GraphicValue]:
        width = self.get_width()
        height = self.get_height()
        width_with_padding = width + self.padding_left + self.padding_right
        height_with_padding = height + self.padding_top + self.padding_bottom
        return width_with_padding, height_with_padding

    def get_object_length_with_padding(self) -> TimeValue:
        object_length = self.get_object_length()
        return object_length + self.time_padding_start + self.time_padding_end

    def get_object_length(self) -> TimeValue:
        return (
            self.source_object_length
            if (
                self.source_object_length is not None
                and not self.object_length.is_fit()
            )
            else self.object_length
        )

    def get_width(self) -> GraphicValue:
        return (
            self.source_width
            if (self.width.is_auto() and self.source_width is not None)
            else self.width
        )

    def get_height(self) -> GraphicValue:
        return (
            self.source_height
            if (self.height.is_auto() and self.source_height is not None)
            else self.height
        )


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

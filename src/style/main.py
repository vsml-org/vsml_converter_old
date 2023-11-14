from __future__ import annotations

from typing import Optional

import ffmpeg
from lxml.etree import _Attrib

from utils import TagInfoTree, VSMLManager

from .styling_parser import (
    audio_system_parser,
    color_and_pixel_parser,
    color_parser,
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
    GraphicUnit,
    GraphicValue,
    LayerMode,
    Order,
    TimeUnit,
    TimeValue,
)


class Style:
    # style param
    # time param
    object_length: TimeValue = TimeValue("fit")
    time_margin_start: TimeValue = TimeValue("fit")
    time_margin_end: TimeValue = TimeValue("fit")
    time_padding_start: TimeValue = TimeValue("fit")
    time_padding_end: TimeValue = TimeValue("fit")
    order: Optional[Order] = None
    # visual param
    width: GraphicValue = GraphicValue("auto")
    height: GraphicValue = GraphicValue("auto")
    layer_mode: Optional[LayerMode] = None
    margin_top: GraphicValue = GraphicValue("auto")
    margin_left: GraphicValue = GraphicValue("auto")
    margin_right: GraphicValue = GraphicValue("auto")
    margin_bottom: GraphicValue = GraphicValue("auto")
    padding_top: GraphicValue = GraphicValue("auto")
    padding_left: GraphicValue = GraphicValue("auto")
    padding_right: GraphicValue = GraphicValue("auto")
    padding_bottom: GraphicValue = GraphicValue("auto")
    background_color: Optional[Color] = None
    # audio param
    audio_volume: float = 100  # inherit
    audio_system: Optional[AudioSystem] = None  # inherit
    # text tag param
    font_color: Optional[Color] = None  # inherit
    font_border_color: Optional[Color] = None  # inherit
    font_border_width: Optional[int] = None  # inherit
    font_family: Optional[str] = None  # inherit
    font_size: Optional[GraphicValue] = None  # inherit
    font_weight: Optional[bool] = None  # inherit
    font_style: Optional[bool] = None  # inherit
    # source value
    source_object_length: Optional[TimeValue] = None
    source_width: Optional[GraphicValue] = None
    source_height: Optional[GraphicValue] = None
    source_audio_system: Optional[AudioSystem] = None

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
            case "wrp":
                self.order = Order.SEQUENCE
                self.layer_mode = LayerMode.MULTI
            case "seq":
                self.order = Order.SEQUENCE
                self.layer_mode = LayerMode.MULTI
            case "rect":
                self.order = Order.SEQUENCE
                self.layer_mode = LayerMode.MULTI
            case "prl":
                self.order = Order.PARALLEL
                self.layer_mode = LayerMode.MULTI
            case "layer":
                self.order = Order.PARALLEL
                self.layer_mode = LayerMode.SINGLE
            case "vid":
                meta = ffmpeg.probe(source_value)
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
                meta = ffmpeg.probe(source_value)
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
                meta = ffmpeg.probe(source_value)
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
        if self.object_length.unit == TimeUnit.PERCENT:
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
                self.object_length.unit = parent_param.object_length.unit

        match self.width.unit:
            case GraphicUnit.PERCENT:
                if parent_param is None:
                    self.width.value = int(
                        VSMLManager.get_root_resolution().width
                        * self.width.value
                        / 100
                    )
                    # PIXEL
                    self.width.unit = GraphicUnit.PIXEL
                elif (
                    parent_param.width is not None
                    and parent_param.width.unit == GraphicUnit.PIXEL
                ):
                    self.width.value = int(
                        parent_param.width.value * self.width.value / 100
                    )
                    # PIXEL
                    self.width.unit = parent_param.width.unit
                else:
                    if self.source_width is None:
                        # AUTO
                        self.width.unit = GraphicUnit.AUTO
                    else:
                        # PIXEL
                        self.width = self.source_width
            case GraphicUnit.RESOLUTION_WIDTH:
                self.width.value = int(
                    VSMLManager.get_root_resolution().width
                    * self.width.value
                    / 100
                )
                # PIXEL
                self.width.unit = GraphicUnit.PIXEL
            case GraphicUnit.RESOLUTION_HEIGHT:
                self.width.value = int(
                    VSMLManager.get_root_resolution().height
                    * self.width.value
                    / 100
                )
                # PIXEL
                self.width.unit = GraphicUnit.PIXEL
            case GraphicUnit.RESOLUTION_MIN:
                self.width.value = int(
                    VSMLManager.get_root_resolution().get_min()
                    * self.width.value
                    / 100
                )
                # PIXEL
                self.width.unit = GraphicUnit.PIXEL
            case GraphicUnit.RESOLUTION_MAX:
                self.width.value = int(
                    VSMLManager.get_root_resolution().get_max()
                    * self.width.value
                    / 100
                )
                # PIXEL
                self.width.unit = GraphicUnit.PIXEL

        match self.height.unit:
            case GraphicUnit.PERCENT:
                if parent_param is None:
                    self.height.value = int(
                        VSMLManager.get_root_resolution().height
                        * self.height.value
                        / 100
                    )
                    # PIXEL
                    self.width.unit = GraphicUnit.PIXEL
                elif (
                    parent_param.height is not None
                    and parent_param.height.unit == GraphicUnit.PIXEL
                ):
                    self.height.value = int(
                        parent_param.height.value * self.height.value / 100
                    )
                    # PIXEL
                    self.height.unit = parent_param.height.unit
                else:
                    if self.source_height is None:
                        # AUTO
                        self.height.unit = GraphicUnit.AUTO
                    else:
                        # PIXEL
                        self.height = self.source_height
            case GraphicUnit.RESOLUTION_WIDTH:
                self.height.value = int(
                    VSMLManager.get_root_resolution().width
                    * self.height.value
                    / 100
                )
                # PIXEL
                self.height.unit = GraphicUnit.PIXEL
            case GraphicUnit.RESOLUTION_HEIGHT:
                self.height.value = int(
                    VSMLManager.get_root_resolution().height
                    * self.height.value
                    / 100
                )
                # PIXEL
                self.height.unit = GraphicUnit.PIXEL
            case GraphicUnit.RESOLUTION_MIN:
                self.height.value = int(
                    VSMLManager.get_root_resolution().get_min()
                    * self.height.value
                    / 100
                )
                # PIXEL
                self.height.unit = GraphicUnit.PIXEL
            case GraphicUnit.RESOLUTION_MAX:
                self.height.value = int(
                    VSMLManager.get_root_resolution().get_max()
                    * self.height.value
                    / 100
                )
                # PIXEL
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

    def get_size_with_padding(self) -> tuple[int, int]:
        source_width_px = 0
        source_height_px = 0
        if self.source_width is not None:
            source_width_px = self.source_width.get_pixel()
        if self.source_height is not None:
            source_height_px = self.source_height.get_pixel()
        padding_left_px = self.padding_left.get_pixel()
        padding_right_px = self.padding_right.get_pixel()
        padding_top_px = self.padding_top.get_pixel()
        padding_bottom_px = self.padding_bottom.get_pixel()
        width_px_with_padding = (
            self.width.get_pixel(source_width_px)
            + padding_left_px
            + padding_right_px
        )
        height_px_with_padding = (
            self.height.get_pixel(source_height_px)
            + padding_top_px
            + padding_bottom_px
        )
        return width_px_with_padding, height_px_with_padding


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

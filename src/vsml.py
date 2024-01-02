from typing import Optional

from lxml.etree import _Element

import definition
from content import SourceContent, VSMLContent, WrapContent, get_source_value
from style import (
    GraphicUnit,
    GraphicValue,
    LayerMode,
    Order,
    Style,
    TimeUnit,
    TimeValue,
    pickup_style,
)
from utils import TagInfoTree, VSMLManager, WidthHeight
from vss import convert_prop_val_to_dict, convert_vss_dict


class WrapObjectTimeInfo:
    children_is_fit: bool
    whole_object_length: TimeValue
    last_time_margin: TimeValue

    def __init__(
        self,
        children_is_fit: bool,
        whole_object_length: TimeValue,
        last_time_margin: TimeValue,
    ):
        self.children_is_fit = children_is_fit
        self.whole_object_length = whole_object_length
        self.last_time_margin = last_time_margin

    def include_last_margin(self):
        self.whole_object_length += self.last_time_margin


class WrapObjectGraphicInfo:
    whole_length: GraphicValue
    last_margin: GraphicValue

    def __init__(
        self,
        whole_length: GraphicValue,
        last_margin: GraphicValue,
    ):
        self.whole_length = whole_length
        self.last_margin = last_margin

    def include_last_margin(self):
        self.whole_length += self.last_margin


class VSML:
    content: VSMLContent

    def __init__(self, vsml: _Element):
        # meta, contentの取得
        children = list(vsml)
        metaElement, contentElement = (
            (None, children[0]) if len(children) == 1 else children
        )

        style_tree = {}
        # metaデータの操作
        if metaElement is not None:
            style_tree = element_to_style(metaElement)

        # contentデータの操作
        VSMLManager.set_root_resolution(
            WidthHeight.from_str(contentElement.attrib["resolution"])
        )
        VSMLManager.set_root_fps(float(contentElement.attrib["fps"]))
        content = element_to_content(contentElement, style_tree)
        if content is None:
            raise Exception()
        self.content = content


def element_to_style(
    meta_element: _Element,
) -> dict[str, dict[str, str]]:
    style_tree = {}
    for styleElement in meta_element:
        src_path = styleElement.get("src", None)
        if src_path is not None and src_path != "":
            with open(
                VSMLManager.get_root_path() + src_path,
                "r",
            ) as style_src:
                style_tree |= convert_vss_dict(style_src.read())
        else:
            if styleElement.text is not None and styleElement.text != "":
                style_tree |= convert_vss_dict(styleElement.text)
    return style_tree


def get_style_from_attribute(style_str: Optional[str]) -> dict[str, str]:
    style_dict = {}
    if style_str is not None:
        for prop_val_str in style_str.split(";"):
            style_dict |= convert_prop_val_to_dict(prop_val_str)
    return style_dict


def element_to_content(
    vsml_element: _Element,
    style_tree: dict[str, dict[str, str]],
    parent_info_tree: Optional[TagInfoTree] = None,
    parent_param: Optional[Style] = None,
    count: int = 0,
) -> VSMLContent:
    tag_name = vsml_element.tag
    classes_name = vsml_element.attrib.get("class", "").split(" ")
    id_name = vsml_element.attrib.get("id")
    source_value = (
        get_source_value(vsml_element)
        if tag_name in definition.CONTENT_TAG
        else ""
    )

    # styleの取得
    picked_up_style_tree = pickup_style(
        style_tree,
        tag_name,
        classes_name,
        id_name,
        parent_info_tree,
    ) | get_style_from_attribute(vsml_element.attrib.get("style"))
    style = Style(
        tag_name,
        parent_param,
        source_value,
        picked_up_style_tree,
        vsml_element.attrib,
    )

    # vsml_elementがSourceContentの場合
    if tag_name in definition.CONTENT_TAG:
        vsml_content = SourceContent(
            vsml_element,
            source_value,
            style,
        )

    # vsml_elementがWrapContentの場合
    elif tag_name in definition.WRAP_TAG:
        # 子要素の取得
        vsml_element_children = list(vsml_element)

        vsml_content = WrapContent(vsml_element, style)
        tag_info_tree = TagInfoTree(
            tag_name,
            classes_name,
            id_name,
            parent_info_tree,
        )

        wrap_object_time_info = WrapObjectTimeInfo(
            children_is_fit=(
                style.order == Order.PARALLEL
                or len(vsml_element_children) == 0
            ),
            whole_object_length=TimeValue("0"),
            last_time_margin=TimeValue("0"),
        )
        calc_object_length = None
        # 親要素に時間指定がないとき
        if style.object_length.unit == TimeUnit.FIT:
            # シーケンス(時間的逐次)
            if style.order == Order.SEQUENCE:
                calc_object_length = calc_catenating_object_length
            # パラレル(時間的並列)
            elif style.order == Order.PARALLEL:
                calc_object_length = calc_piling_object_length
        wrap_object_horizontal_info = WrapObjectGraphicInfo(
            whole_length=GraphicValue("0"),
            last_margin=GraphicValue("0"),
        )
        wrap_object_vertical_info = WrapObjectGraphicInfo(
            whole_length=GraphicValue("0"),
            last_margin=GraphicValue("0"),
        )
        calc_width = None
        calc_height = None
        # シングルレイヤ(横並び)モード
        if (
            style.order == Order.PARALLEL
            and style.layer_mode == LayerMode.SINGLE
        ):
            calc_width = calc_catenating_graphic_length
            calc_height = calc_piling_graphic_length
        # マルチレイヤ(奥行き並び)モード
        else:
            calc_width = calc_piling_graphic_length
            calc_height = calc_piling_graphic_length

        for vsml_element_child in vsml_element_children:
            # 子要素Elementの作成と配列への追加
            child_content = element_to_content(
                vsml_element_child,
                style_tree,
                tag_info_tree,
                style,
                count + 1,
            )
            vsml_content.items.append(child_content)

            # exist情報の更新
            vsml_content.exist_video = (
                vsml_content.exist_video or child_content.exist_video
            )
            vsml_content.exist_audio = (
                vsml_content.exist_audio or child_content.exist_audio
            )

            child_style = child_content.style
            # 時間計算
            child_object_length = child_style.get_object_length()
            if calc_object_length is not None:
                calc_object_length(
                    wrap_object_time_info,
                    child_style.object_length.unit == TimeUnit.FIT,
                    child_style.time_margin_start,
                    child_style.time_padding_start,
                    child_object_length,
                    child_style.time_padding_end,
                    child_style.time_margin_end,
                )

            # 幅、高さ計算
            child_width = child_style.get_width()
            child_height = child_style.get_height()
            if child_content.exist_video:
                if calc_width is not None:
                    calc_width(
                        wrap_object_horizontal_info,
                        child_style.margin_left,
                        child_style.padding_left,
                        child_width,
                        child_style.padding_right,
                        child_style.margin_right,
                    )
                if calc_height is not None:
                    calc_height(
                        wrap_object_vertical_info,
                        child_style.margin_top,
                        child_style.padding_top,
                        child_height,
                        child_style.padding_bottom,
                        child_style.margin_bottom,
                    )

        wrap_object_time_info.include_last_margin()
        wrap_object_horizontal_info.include_last_margin()
        wrap_object_vertical_info.include_last_margin()

        # wrapのobject_lengthがデフォルト値(FIT)かつ、子要素全体が時間的長さを持つ場合
        if (
            style.object_length.unit == TimeUnit.FIT
            and not wrap_object_time_info.children_is_fit
        ):
            # 親のobject_lengthを更新
            style.object_length = wrap_object_time_info.whole_object_length
        if vsml_content.exist_video:
            # 親のwidth, heightを更新
            if style.width.unit == GraphicUnit.AUTO:
                style.width = wrap_object_horizontal_info.whole_length
            if style.height.unit == GraphicUnit.AUTO:
                style.height = wrap_object_vertical_info.whole_length

    else:
        raise Exception()

    return vsml_content


def calc_catenating_object_length(
    wrap_object_info: WrapObjectTimeInfo,
    child_is_fit: bool,
    time_margin_start: TimeValue,
    time_padding_start: TimeValue,
    child_object_length: TimeValue,
    time_padding_end: TimeValue,
    time_margin_end: TimeValue,
):
    wrap_object_info.children_is_fit = (
        wrap_object_info.children_is_fit or child_is_fit
    )
    wrap_object_info.whole_object_length += (
        max(
            time_margin_start,
            wrap_object_info.last_time_margin,
        )
        + time_padding_start
        + child_object_length
        + time_padding_end
    )
    wrap_object_info.last_time_margin = time_margin_end


def calc_piling_object_length(
    wrap_object_info: WrapObjectTimeInfo,
    child_is_fit: bool,
    time_margin_start: TimeValue,
    time_padding_start: TimeValue,
    child_object_length: TimeValue,
    time_padding_end: TimeValue,
    time_margin_end: TimeValue,
):
    wrap_object_info.children_is_fit = (
        wrap_object_info.children_is_fit and child_is_fit
    )
    wrap_object_info.whole_object_length = max(
        wrap_object_info.whole_object_length,
        (
            time_margin_start
            + time_padding_start
            + child_object_length
            + time_padding_end
            + time_margin_end
        ),
    )


def calc_catenating_graphic_length(
    wrap_object_info: WrapObjectGraphicInfo,
    margin_start: GraphicValue,
    padding_start: GraphicValue,
    child_graphic_length: GraphicValue,
    padding_end: GraphicValue,
    margin_end: GraphicValue,
):
    wrap_object_info.whole_length += (
        max(
            margin_start,
            wrap_object_info.last_margin,
        )
        + padding_start
        + child_graphic_length
        + padding_end
    )
    wrap_object_info.last_margin = margin_end


def calc_piling_graphic_length(
    wrap_object_info: WrapObjectGraphicInfo,
    margin_start: GraphicValue,
    padding_start: GraphicValue,
    child_graphic_length: GraphicValue,
    padding_end: GraphicValue,
    margin_end: GraphicValue,
):
    child_length_with_space = (
        max(
            margin_start,
            wrap_object_info.last_margin,
        )
        + padding_start
        + child_graphic_length
        + padding_end
        + margin_end
    )
    wrap_object_info.whole_length = max(
        wrap_object_info.whole_length,
        child_length_with_space,
    )

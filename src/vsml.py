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

    source_value = ""
    if tag_name in definition.CONTENT_TAG:
        source_value = get_source_value(vsml_element)

    # styleの取得
    picked_up_style_tree = pickup_style(
        style_tree,
        tag_name,
        classes_name,
        id_name,
        parent_info_tree,
    )
    picked_up_style_tree |= get_style_from_attribute(
        vsml_element.attrib.get("style")
    )
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

        fps = VSMLManager.get_root_fps()
        children_object_length = 0.0
        child_object_length_is_fit = (
            style.order == Order.PARALLEL or len(vsml_element_children) == 0
        )
        last_time_margin = 0.0
        children_width = 0
        last_margin_horizontal = 0
        children_height = 0
        last_margin_vertical = 0

        for vsml_element_child in vsml_element_children:
            child_content = element_to_content(
                vsml_element_child,
                style_tree,
                tag_info_tree,
                style,
                count + 1,
            )
            vsml_content.exist_video = (
                vsml_content.exist_video or child_content.exist_video
            )
            vsml_content.exist_audio = (
                vsml_content.exist_audio or child_content.exist_audio
            )
            child_style = child_content.style
            child_source_object_length = (
                child_style.source_object_length.value
                if child_style.source_object_length
                else 0.0
            )
            child_source_width = (
                child_style.source_width.value
                if child_style.source_width
                else 0
            )
            child_source_height = (
                child_style.source_height.value
                if child_style.source_height
                else 0
            )

            # 時間計算
            if style.object_length.unit == TimeUnit.FIT:
                # シーケンス(時間的逐次)
                if style.order == Order.SEQUENCE:
                    # 時間の制限がない(FIT)場合親もFITにする
                    if child_style.object_length.unit == TimeUnit.FIT:
                        child_object_length_is_fit = True
                    # FITでないとき
                    if not child_object_length_is_fit:
                        children_object_length += (
                            max(
                                child_style.time_margin_start.get_second(fps),
                                last_time_margin,
                            )
                            + child_style.time_padding_start.get_second(fps)
                            + child_style.object_length.get_second(
                                fps, child_source_object_length
                            )
                            + child_style.time_padding_end.get_second(fps)
                        )
                        last_time_margin = (
                            child_style.time_margin_end.get_second(fps)
                        )
                # パラレル(時間的並列)
                elif style.order == Order.PARALLEL:
                    if child_style.object_length.unit != TimeUnit.FIT:
                        child_object_length_is_fit = False
                    child_object_length = (
                        child_style.time_margin_start.get_second(fps)
                        + child_style.time_padding_start.get_second(fps)
                        + child_style.object_length.get_second(
                            fps, child_source_object_length
                        )
                        + child_style.time_padding_end.get_second(fps)
                        + child_style.time_margin_end.get_second(fps)
                    )
                    children_object_length = max(
                        children_object_length, child_object_length
                    )

            if child_content.exist_video:
                # シングルレイヤ(横並び)モード
                if (
                    style.order == Order.PARALLEL
                    and style.layer_mode == LayerMode.SINGLE
                ):
                    # 幅計算
                    children_width += (
                        max(
                            child_style.margin_left.get_pixel(),
                            last_margin_horizontal,
                        )
                        + child_style.padding_left.get_pixel()
                        + child_style.width.get_pixel(child_source_width)
                        + child_style.padding_right.get_pixel()
                    )
                    last_margin_horizontal = (
                        child_style.margin_right.get_pixel()
                    )

                    # 高さ計算
                    child_height = (
                        max(
                            child_style.margin_top.get_pixel(),
                            last_margin_vertical,
                        )
                        + child_style.padding_top.get_pixel()
                        + child_style.height.get_pixel(child_source_height)
                        + child_style.padding_bottom.get_pixel()
                        + child_style.margin_bottom.get_pixel()
                    )
                    children_height = max(children_height, child_height)
                # マルチレイヤ(奥行き並び)モード
                else:
                    # 幅計算
                    child_width = (
                        max(
                            child_style.margin_left.get_pixel(),
                            last_margin_horizontal,
                        )
                        + child_style.padding_left.get_pixel()
                        + child_style.width.get_pixel(child_source_width)
                        + child_style.padding_right.get_pixel()
                        + child_style.margin_right.get_pixel()
                    )
                    children_width = max(children_width, child_width)

                    # 高さ計算
                    child_height = (
                        max(
                            child_style.margin_top.get_pixel(),
                            last_margin_vertical,
                        )
                        + child_style.padding_top.get_pixel()
                        + child_style.height.get_pixel(child_source_height)
                        + child_style.padding_bottom.get_pixel()
                        + child_style.margin_bottom.get_pixel()
                    )
                    children_height = max(children_height, child_height)

            vsml_content.items.append(child_content)

        # FITでないとき
        if (
            style.object_length.unit == TimeUnit.FIT
            and not child_object_length_is_fit
        ):
            # シーケンスのとき
            if style.order == Order.SEQUENCE:
                children_object_length += last_time_margin
            # 親のobject_lengthを更新
            style.object_length = TimeValue(
                "{}s".format(children_object_length)
            )
        if vsml_content.exist_video:
            # シングルレイヤ(横並び)モード
            if (
                style.order == Order.PARALLEL
                and style.layer_mode == LayerMode.SINGLE
            ):
                children_width += last_margin_horizontal
                children_height += last_margin_vertical
            # 親のwidth, heightを更新
            if style.width.unit == GraphicUnit.AUTO:
                style.width = GraphicValue("{}px".format(children_width))
            if style.height.unit == GraphicUnit.AUTO:
                style.height = GraphicValue("{}px".format(children_height))

    else:
        raise Exception()

    return vsml_content

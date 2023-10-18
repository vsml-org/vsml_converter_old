from typing import Optional

from lxml.etree import _Element

import definition
from content import SourceContent, VSMLContent, WrapContent, get_source_value
from style import Style, pickup_style
from utils import TagInfoTree, VSMLManager, WidthHeight
from vss import convert_vss_dict


class VSML:
    fps: int
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
        self.fps = int(contentElement.attrib["fps"])
        content = element_to_content(contentElement, style_tree)
        if content is None:
            raise Exception()
        self.content = content


def element_to_style(meta_element: _Element) -> dict[str, dict[str, str]]:
    style_tree = {}
    for styleElement in meta_element:
        src_path = styleElement.get("src", None)
        if src_path:
            with open(VSMLManager.get_root_path() + src_path, "r") as style_src:
                style_tree |= convert_vss_dict(style_src.read())
        else:
            if styleElement.text:
                style_tree |= convert_vss_dict(styleElement.text)

    return style_tree


def element_to_content(
    vsml_element: _Element,
    style_tree: dict[str, dict[str, str]],
    parent_info_tree: Optional[TagInfoTree] = None,
    parent_param: Optional[Style] = None,
    count: int = 0,
) -> VSMLContent:
    # 子要素の取得
    vsml_element_children = list(vsml_element)

    tag_name = vsml_element.tag
    classes_name = vsml_element.attrib.get("class", "").split(" ")
    id_name = vsml_element.attrib.get("id")

    source_value = ""
    if tag_name in definition.CONTENT_TAG:
        source_value = get_source_value(vsml_element)

    # styleの取得
    picked_up_style_tree = pickup_style(
        style_tree, tag_name, classes_name, id_name, parent_info_tree
    )
    style = Style(
        tag_name, parent_param, source_value, picked_up_style_tree, vsml_element.attrib
    )

    # vsml_elementがSourceContentの場合
    if tag_name in definition.CONTENT_TAG:
        vsml_content = SourceContent(vsml_element, source_value, style)
    # vsml_elementがWrapContentの場合
    elif tag_name in definition.WRAP_TAG:
        vsml_content = WrapContent(vsml_element, style)
        tag_info_tree = TagInfoTree(tag_name, classes_name, id_name, parent_info_tree)
        for vsml_element_child in vsml_element_children:
            vsml_content.items.append(
                element_to_content(
                    vsml_element_child, style_tree, tag_info_tree, style, count + 1
                )
            )
    else:
        raise Exception()

    return vsml_content

import re

from lxml.etree import _Element, tostring

from style import Style
from utils import SourceType, VSMLManager


def get_source_value(
    vsml_element: _Element,
) -> str:
    tag_name = vsml_element.tag
    match tag_name:
        case "vid" | "aud" | "img":
            src_path = vsml_element.get("src", None)
            if src_path is None:
                raise Exception()
            return VSMLManager.get_root_path() + src_path
        case "txt":
            txt_child = tostring(
                vsml_element,
                method="c14n2",
            ).decode()
            txt_child = re.sub(
                r"^.*?<txt.*?>",
                "",
                txt_child,
            )
            txt_child = re.sub(
                r"</txt>",
                "",
                txt_child,
            )
            txt_child = re.sub(
                r"\n\s*?",
                "",
                txt_child,
            )
            txt_child = re.sub(
                r"<br></br>",
                "\\n",
                txt_child,
            )
            return txt_child.strip()
        case _:
            raise Exception()


class VSMLContent:
    tag_name: str
    style: Style
    exist_video: bool = False
    exist_audio: bool = False

    def __init__(
        self,
        tag_name: str,
        style: Style,
    ) -> None:
        self.tag_name = tag_name
        self.style = style

    def __repr__(self) -> str:
        return str(vars(self))


class WrapContent(VSMLContent):
    items: list[VSMLContent]

    def __init__(
        self,
        vsml_element: _Element,
        style: Style,
    ) -> None:
        super().__init__(vsml_element.tag, style)
        self.items = []

    def __repr__(self) -> str:
        items_str = "["
        for item in self.items:
            items_str += item.__repr__() + ","
        items_str = items_str[:-1]
        items_str += "]"

        return "{{'tag_name': '{}', 'style': {}, 'items': {}}}".format(
            self.tag_name, self.style, items_str
        )


class SourceContent(VSMLContent):
    type: SourceType
    src_path: str

    def __init__(
        self,
        vsml_element: _Element,
        src_path: str,
        style: Style,
    ) -> None:
        super().__init__(vsml_element.tag, style)
        self.src_path = src_path
        match vsml_element.tag:
            case "img":
                self.type = SourceType.IMAGE
                self.exist_video = True
            case "vid":
                self.type = SourceType.VIDEO
                self.exist_video = True
                self.exist_audio = True
            case "aud":
                self.type = SourceType.AUDIO
                self.exist_audio = True
            case "txt":
                self.type = SourceType.TEXT
                self.exist_video = True
            case _:
                raise Exception()

    def __repr__(self) -> str:
        return str(vars(self))

import re
from typing import Optional, Any
from enum import Enum
from lxml.etree import tostring, _Element

class SortType(Enum):
    SEQUENCE = 'sequence'
    PARALLEL = 'parallel'

class SourceContentType(Enum):
    VIDEO = 'video'
    AUDIO = 'audio'
    IMAGE = 'image'
    TEXT = 'text'
    INVALID = 'invalid'

class VSMLContent:
    tag_name: str
    type: Any

    def __init__(self, vsml_element: _Element) -> None:
        self.tag_name = vsml_element.tag

class WrapContent(VSMLContent):
    type: SortType
    items: list[VSMLContent]
    
    def __init__(self, vsml_element: _Element) -> None:
        super().__init__(vsml_element)
        # typeの決定
        match vsml_element.tag:
            case 'cont' | 'seq' | 'wrp':
                self.type = SortType.SEQUENCE
            case 'prl' | 'rect' | 'layer':
                self.type = SortType.PARALLEL
            case _:
                raise Exception()
        # itemsの作成
        self.items = []

class SourceContent(VSMLContent):
    type: SourceContentType
    src: str

    def __init__(self, vsml_element: _Element, root_path: str) -> None:
        super().__init__(vsml_element)
        source_path = vsml_element.get('src', None)
        if source_path is None:
            if vsml_element.tag != 'txt':
                self.type = SourceContentType.INVALID
                return
            # typeの決定
            self.type = SourceContentType.TEXT
            # srcの保持
            self.src = self.__txt_convert(vsml_element)
        else:
            # typeの決定
            match vsml_element.tag:
                case 'vid':
                    self.type = SourceContentType.VIDEO
                case 'aud':
                    self.type = SourceContentType.AUDIO
                case 'img':
                    self.type = SourceContentType.IMAGE
                case _:
                    raise Exception()
            # srcの保持
            self.src = root_path + source_path

    @staticmethod
    def __txt_convert(vsml_content: _Element) -> str:
        txt_child = tostring(vsml_content, method='c14n2').decode()
        txt_child = re.sub(r'^.*?<txt.*?>', '', txt_child)
        txt_child = re.sub(r'</txt>', '', txt_child)
        txt_child = re.sub(r'\n\s*?', '', txt_child)
        txt_child = re.sub(r'<br></br>', '\n', txt_child)
        return txt_child.strip()

class VSML:
    resolution: str
    fps: str
    content: Optional[VSMLContent]
    root_path: str

    def __init__(self, vsml: _Element, root_path: str):
        self.root_path = root_path
        children = list(vsml)

        # metaデータの操作
        style_data_str = ''
        if len(children) > 1:
            meta = children[0]
            for style in meta:
                src_path = style.get('src', None)
                if src_path:
                    with open(root_path + src_path, 'r') as style_src:
                        style_data_str += style_src.read()
                else:
                    if style.text:
                        style_data_str += style.text

        # contentデータの操作
        contentElement = children[-1]
        self.resolution = contentElement.attrib['resolution']
        self.fps = contentElement.attrib['fps']
        self.content = self.__convert_element(contentElement)

    def __convert_element(self, vsml_element: _Element) -> Optional[VSMLContent]:
        vsml_content: Optional[VSMLContent]
        vsml_element_children = list(vsml_element)
        if len(vsml_element_children) > 0 and vsml_element.tag != 'txt':
            vsml_content = WrapContent(vsml_element)
            for vsml_element_child in vsml_element_children:
                vsml_content_child = self.__convert_element(vsml_element_child)
                if vsml_content_child is not None and vsml_content_child.type != SourceContentType.INVALID:
                    vsml_content.items.append(vsml_content_child)
        else:
            vsml_content = SourceContent(vsml_element, self.root_path)
        return vsml_content
    

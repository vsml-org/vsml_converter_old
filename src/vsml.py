import re
from typing import Optional, Union
from enum import Enum
from lxml.etree import tostring, _Element
from utils import WidthHeight, VSMLManager

class SortType(Enum):
    SEQUENCE = 'sequence'
    PARALLEL = 'parallel'

class SourceContentType(Enum):
    VIDEO = 'video'
    AUDIO = 'audio'
    IMAGE = 'image'
    TEXT = 'text'

# TODO: paramをちゃんと拡張する
class VSMLContent:
    tag_name: str
    param: str
    type: Union[SortType, SourceContentType]

    def __init__(self, vsml_element: _Element) -> None:
        self.param = ''
        self.tag_name = vsml_element.tag

class WrapContent(VSMLContent):
    type: SortType
    items: list[VSMLContent]
    
    def __str__(self) -> str:
        item_str = ',\n'.join([str(item) for item in self.items])
        return f'type: {self.type}\nitems: [\n{item_str}\n]'

    def __init__(self, vsml_element: _Element) -> None:
        super().__init__(vsml_element)
        # typeの決定
        match self.tag_name:
            case 'cont' | 'seq' | 'wrp' | 'rect':
                self.type = SortType.SEQUENCE
                if self.tag_name == 'rect':
                    self.param = 'gray'
            case 'prl' | 'layer':
                self.type = SortType.PARALLEL
            case _:
                raise Exception()
        # itemsの作成
        self.items = []

class SourceContent(VSMLContent):
    type: SourceContentType
    src: str

    def __str__(self) -> str:
        return f'type: {self.type} src: {self.src}'

    def __init__(self, vsml_element: _Element) -> None:
        super().__init__(vsml_element)
        source_path = vsml_element.get('src', None)
        # srcがある場合(txt以外)
        if source_path:
            # typeの決定
            match self.tag_name:
                case 'vid':
                    self.type = SourceContentType.VIDEO
                case 'aud':
                    self.type = SourceContentType.AUDIO
                case 'img':
                    self.type = SourceContentType.IMAGE
                case _:
                    raise Exception()
            # srcの保持
            self.src = VSMLManager.get_root_path() + source_path
        # srcがない場合(txtのみ)
        elif self.tag_name == 'txt':
            # typeの決定
            self.type = SourceContentType.TEXT
            # srcの保持
            self.src = self.__get_text_source(vsml_element)
        else:
            raise Exception()

    @staticmethod
    def __get_text_source(vsml_content: _Element) -> str:
        txt_child = tostring(vsml_content, method='c14n2').decode()
        txt_child = re.sub(r'^.*?<txt.*?>', '', txt_child)
        txt_child = re.sub(r'</txt>', '', txt_child)
        txt_child = re.sub(r'\n\s*?', '', txt_child)
        txt_child = re.sub(r'<br></br>', '\\n', txt_child)
        return txt_child.strip()

class VSML:
    resolution: WidthHeight
    fps: int
    content: VSMLContent

    def __init__(self, vsml: _Element):
        # meta, contentの取得
        children = list(vsml)
        metaElement, contentElement = (None, children[0]) if len(children) == 1 else children

        # metaデータの操作
        style_data_str = ''
        if metaElement is not None:
            for styleElement in metaElement:
                src_path = styleElement.get('src', None)
                if src_path:
                    with open(VSMLManager.get_root_path() + src_path, 'r') as style_src:
                        style_data_str += style_src.read()
                else:
                    if styleElement.text:
                        style_data_str += styleElement.text

        # contentデータの操作
        self.resolution = WidthHeight.from_str(contentElement.attrib['resolution'])
        self.fps = int(contentElement.attrib['fps'])
        content = element_to_content(contentElement)
        if content is None:
            raise Exception()
        self.content = content

def element_to_content(vsml_element: _Element) -> Optional[VSMLContent]:
    # 子要素の取得
    vsml_element_children = list(vsml_element)

    # vsml_elementがSourceContentの場合
    if len(vsml_element_children) == 0 or vsml_element.tag == 'txt':
        vsml_content = SourceContent(vsml_element)
    # vsml_elementがWrapContentの場合
    else:
        vsml_content = WrapContent(vsml_element)
        for vsml_element_child in vsml_element_children:
            # 子要素を再帰的にこの関数にわたす
            vsml_content_child = element_to_content(vsml_element_child)
            # 無効なタグ以外はitemsに追加する
            if vsml_content_child:
                vsml_content.items.append(vsml_content_child)
        # itemsが存在しないWrapContentは無効なタグとする
        # if not vsml_content.items:
        #     return None

    return vsml_content

import re
from typing import Optional, Union
from enum import Enum
from lxml.etree import tostring, _Element
from utils import WidthHeight, VSMLManager, AudioSystem, Position
import ffmpeg
from vss import convert_vss_dict

WRAP_TAG = ['cont', 'wrp', 'seq', 'prl', 'rect', 'layer']
CONTENT_TAG = ['vid', 'aud', 'img', 'txt']

class SortType(Enum):
    SEQUENCE = 'sequence'
    PARALLEL = 'parallel'

    def __repr__(self) -> str:
        return f"'SortType.{self.name}'"

class SourceType(Enum):
    VIDEO = 'video'
    AUDIO = 'audio'
    IMAGE = 'image'
    TEXT = 'text'

    def __repr__(self) -> str:
        return f"'SourceType.{self.name}'"

class VSMLContent:
    tag_name: str
    type: Union[SortType, SourceType]
    duration: Optional[float] = None
    resolution: Optional[WidthHeight] = None
    start_position: Optional[Position] = None
    background_color: Optional[str] = None

    def __init__(self, vsml_element: _Element) -> None:
        self.tag_name = vsml_element.tag

    def __repr__(self) -> str:
        return str(vars(self))

class WrapContent(VSMLContent):
    type: SortType
    items: list[VSMLContent] = []

    def __init__(self, vsml_element: _Element) -> None:
        super().__init__(vsml_element)
        # typeの決定
        match self.tag_name:
            case 'cont' | 'seq' | 'wrp':
                self.type = SortType.SEQUENCE
            case 'rect':
                self.type = SortType.SEQUENCE
                bg_color = vsml_element.get('color', 'white')
                self.background_color = bg_color
            case 'prl' | 'layer':
                self.type = SortType.PARALLEL
            case _:
                raise Exception()
    
    def init_with_items(self):
        duration = 0
        self.start_position = Position(0, 0)
        end_position = Position(0, 0)

        for item in self.items:
            if item.duration:
                match self.type:
                    case SortType.SEQUENCE:
                        duration += item.duration
                    case SortType.PARALLEL:
                        duration = max(duration, item.duration)

            if item.resolution and item.start_position:
                self.start_position.x = min(self.start_position.x, item.start_position.x)
                self.start_position.y = min(self.start_position.y, item.start_position.y)
                end_position.x = max(
                    end_position.x,
                    item.start_position.x + item.resolution.width
                )
                end_position.y = max(
                    end_position.y,
                    item.start_position.y+item.resolution.height
                )
        if duration:
            self.duration = duration
        if self.start_position == Position(0, 0) and end_position == Position(0, 0):
            self.start_position = None
        else:
            self.resolution = WidthHeight(
                end_position.x - self.start_position.x,
                end_position.y - self.start_position.y
            )

class SourceContent(VSMLContent):
    type: SourceType
    src: str
    audio_system: Optional[AudioSystem] = None
    font_size: Optional[int] = None
    color: Optional[str] = None
    font_path: Optional[str] = None

    def __init__(self, vsml_element: _Element) -> None:
        super().__init__(vsml_element)
        source_path = vsml_element.get('src', None)

        # srcがある場合(txt以外)
        if source_path:
            self.src = VSMLManager.get_root_path() + source_path
            meta = ffmpeg.probe(self.src)
            duration, meta_video, meta_audio = SourceContent.__get_streams_and_duration_from_probe_meta(meta)
            match self.tag_name:
                case 'vid':
                    if meta_video is None:
                        raise Exception()
                    self.start_position = Position(0, 0)
                    self.type = SourceType.VIDEO
                    self.resolution = WidthHeight(meta_video['width'], meta_video['height'])
                    if meta_audio is not None:
                        self.audio_system = AudioSystem.STEREO if meta_audio.get('channel_layout') == 'stereo' else AudioSystem.MONAURAL
                    if duration:
                        self.duration = float(duration)
                case 'aud':
                    if meta_audio is None:
                        raise Exception()
                    self.type = SourceType.AUDIO
                    self.audio_system = AudioSystem.STEREO if meta_audio.get('channel_layout') == 'stereo' else AudioSystem.MONAURAL
                    if duration:
                        self.duration = float(duration)
                case 'img':
                    if meta_video is None:
                        raise Exception()
                    self.start_position = Position(0, 0)
                    self.type = SourceType.IMAGE
                    self.resolution = WidthHeight(meta_video['width'], meta_video['height'])
                case _:
                    raise Exception()

        # srcがない場合(txtのみ)
        elif self.tag_name == 'txt':
            self.type = SourceType.TEXT
            self.src = SourceContent.__get_text_source(vsml_element)
            self.start_position = Position(0, 0)
            self.resolution = SourceContent.__get_resolution_from_src(self.src)
            self.font_size = 80
            self.color = 'white'
            self.font_path = '/mnt/c/Windows/Fonts/msgothic.ttc'

        else:
            raise Exception()

    @staticmethod
    def __get_resolution_from_src(text: str) -> WidthHeight:
        # TODO: WidthHeightの計算を見直す
        # harfbuzz
        row_str_list = text.split('\n')
        col_count = max(map(len, row_str_list))
        row_count = len(row_str_list)
        return WidthHeight(80 * col_count, 80 * row_count)

    @staticmethod
    def __get_streams_and_duration_from_probe_meta(meta: dict) -> tuple[Optional[float], Optional[dict], Optional[dict]]:
        duration = meta.get('format', {}).get('duration', None)
        meta_video = None
        meta_audio = None
        stream_info = meta.get('streams', [])
        for stream in stream_info:
            if meta_video is None and stream.get('codec_type') == 'video':
                meta_video = stream
                continue
            if meta_audio is None and stream.get('codec_type') == 'audio':
                meta_audio = stream
                continue
            if meta_video is not None and meta_audio is not None:
                break
        return (duration, meta_video, meta_audio)

    @staticmethod
    def __get_text_source(vsml_content: _Element) -> str:
        txt_child = tostring(vsml_content, method='c14n2').decode()
        txt_child = re.sub(r'^.*?<txt.*?>', '', txt_child)
        txt_child = re.sub(r'</txt>', '', txt_child)
        txt_child = re.sub(r'\n\s*?', '', txt_child)
        txt_child = re.sub(r'<br></br>', '\\n', txt_child)
        return txt_child.strip()

class VSML:
    fps: int
    content: VSMLContent
    style_tree: dict[str, dict[str, str]] = {}

    def __init__(self, vsml: _Element):
        # meta, contentの取得
        children = list(vsml)
        metaElement, contentElement = (None, children[0]) if len(children) == 1 else children

        # metaデータの操作
        if metaElement is not None:
            for styleElement in metaElement:
                src_path = styleElement.get('src', None)
                if src_path:
                    with open(VSMLManager.get_root_path() + src_path, 'r') as style_src:
                        self.style_tree = self.style_tree | convert_vss_dict(style_src.read())
                else:
                    if styleElement.text:
                        self.style_tree = self.style_tree | convert_vss_dict(styleElement.text)

        # contentデータの操作
        VSMLManager.set_root_resolution(WidthHeight.from_str(contentElement.attrib['resolution']))
        self.fps = int(contentElement.attrib['fps'])
        content = element_to_content(contentElement)
        if content is None:
            raise Exception()
        self.content = content

def element_to_content(vsml_element: _Element) -> VSMLContent:
    # 子要素の取得
    vsml_element_children = list(vsml_element)

    # vsml_elementがSourceContentの場合
    if vsml_element.tag in CONTENT_TAG:
        vsml_content = SourceContent(vsml_element)
    # vsml_elementがWrapContentの場合
    elif vsml_element.tag in WRAP_TAG:
        vsml_content = WrapContent(vsml_element)
        vsml_content.items = [element_to_content(vsml_element_child) for vsml_element_child in vsml_element_children]
        vsml_content.init_with_items()
    else:
        raise Exception()

    return vsml_content

import ffmpeg
from vsml import SourceContent, SourceType
from .schemas import Process
from .utils import get_transparent_process
from utils import WidthHeight, AudioSystem, VSMLManager

def create_source_process(vsml_content: SourceContent, debug_mode: bool = False) -> Process:
    match vsml_content.type:
        case SourceType.IMAGE:
            # video_processの処理
            transparent_process = get_transparent_process(VSMLManager.get_root_resolution().get_str())
            video_process = ffmpeg.input(vsml_content.src, loop=1).video.filter('setsar', '1/1')
            video_process = ffmpeg.overlay(transparent_process, video_process)
            # processの作成
            process = Process(video_process, None, None, vsml_content.resolution, vsml_content.start_position)

        case SourceType.AUDIO:
            # sourceの取得
            audio_process = ffmpeg.input(vsml_content.src).audio
            # audio_processの処理
            if vsml_content.audio_system == AudioSystem.MONAURAL:
                audio_process = ffmpeg.filter([audio_process, audio_process], 'amerge', inputs=2)
            # processの作成
            process = Process(None, audio_process, vsml_content.duration, None, None)

        case SourceType.VIDEO:
            # sourceの取得
            source = ffmpeg.input(vsml_content.src)
            # video_processの処理
            transparent_process = get_transparent_process(VSMLManager.get_root_resolution().get_str())
            video_process = ffmpeg.overlay(transparent_process, source.video).trim(start=0, end=vsml_content.duration)
            # audio_processの処理
            audio_process = None
            if vsml_content.audio_system:
                audio_process = source.audio 
                if vsml_content.audio_system == AudioSystem.MONAURAL:
                    audio_process = ffmpeg.filter([audio_process, audio_process], 'amerge', inputs=2)
            # processの作成
            process = Process(video_process, audio_process, vsml_content.duration, vsml_content.resolution, vsml_content.start_position)

        case SourceType.TEXT:
            # video_processの処理
            transparent_process = get_transparent_process(VSMLManager.get_root_resolution().get_str())
            video_process = ffmpeg.drawtext(
                transparent_process, text=vsml_content.src,
                fontfile=vsml_content.font_path, fontsize=vsml_content.font_size, fontcolor=vsml_content.color
            )
            # processの作成
            process = Process(video_process, None, None, vsml_content.resolution, vsml_content.start_position)

        case _:
            raise Exception()

    return process

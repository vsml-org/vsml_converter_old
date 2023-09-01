import ffmpeg
from typing import Optional
from vsml import SourceContent, SourceContentType
from .schemas import Process
from .utils import get_transparent_process
from utils import WidthHeight, Position

def create_source_process(vsml_content: SourceContent, resolution: WidthHeight, debug_mode: bool = False) -> Optional[Process]:
    match vsml_content.type:
        case SourceContentType.IMAGE:
            meta = ffmpeg.probe(vsml_content.src)
            transparent_process = get_transparent_process(resolution.get_str())
            source = ffmpeg.input(vsml_content.src, loop=1).video.filter('setsar', '1/1')
            source = ffmpeg.overlay(transparent_process, source)
            process = Process(
                source, None, None,
                WidthHeight(meta['streams'][0]['width'], meta['streams'][0]['width']), Position(0, 0)
            )

        case SourceContentType.AUDIO:
            isMono = False

            meta = ffmpeg.probe(vsml_content.src)
            for stream in meta.get('streams', []):
                if stream.get('codec_type') == 'audio':
                    isMono = stream.get('channel_layout') != 'stereo'
                    break

            source = ffmpeg.input(vsml_content.src).audio
            if isMono:
                source = ffmpeg.filter([source, source], 'amerge', inputs=2)

            duration = meta.get('format', {}).get('duration', None)
            if duration is not None:
                duration = float(duration)

            process = Process(None, source, duration, None, None)

        case SourceContentType.VIDEO:
            existVideo = False
            existAudio = False
            isMono = False

            meta = ffmpeg.probe(vsml_content.src)
            for stream in meta.get('streams', []):
                if stream.get('codec_type') == 'video':
                    existVideo = True
                if stream.get('codec_type') == 'audio':
                    existAudio = True
                    isMono = stream.get('channel_layout') == 'stereo'
            if not existVideo:
                raise Exception()

            source = ffmpeg.input(vsml_content.src)
            source_audio = source.audio if existAudio else None
            if isMono:
                source_audio = ffmpeg.filter([source_audio, source_audio], 'amerge', inputs=2)

            duration = meta.get('format', {}).get('duration', None)
            if duration is not None:
                duration = float(duration)

            video_process = None
            if source.video is not None:
                transparent_process = get_transparent_process(resolution.get_str())
                video_process = ffmpeg.overlay(transparent_process, source.video)
                video_process = ffmpeg.trim(video_process, start=0, end=duration)

            process = Process(
                video_process, source_audio, duration,
                WidthHeight(meta['streams'][0]['width'], meta['streams'][0]['width']), Position(0, 0)
            )

        case SourceContentType.TEXT:
            transparent_process = get_transparent_process(resolution.get_str())
            video_process = ffmpeg.drawtext(
                transparent_process, text=vsml_content.src,
                fontfile='/mnt/c/Windows/Fonts/msgothic.ttc', fontsize=80, fontcolor='white'
            )
            # TODO: WidthHeightの計算を見直す
            row_str_list = vsml_content.src.split('\n')
            col_count = max(map(len, row_str_list))
            row_count = len(row_str_list)
            print(vsml_content)
            print(col_count)
            print(row_count)
            process = Process(video_process, None, None, WidthHeight(80 * col_count, 80 * row_count), Position(0, 0))

        case _:
            raise Exception()

    return process

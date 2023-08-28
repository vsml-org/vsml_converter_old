import ffmpeg
from typing import Optional
from vsml import SourceContent, SourceContentType, WidthHeight
from .schemas import Process

def create_source_process(vsml_content: SourceContent, resolution: WidthHeight, debug_mode: bool = False) -> Optional[Process]:
    match vsml_content.type:
        case SourceContentType.IMAGE:
            source = ffmpeg.input(vsml_content.src, loop=1).video.filter('setsar', '1/1')
            process = Process(source, None, None)

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

            process = Process(None, source, duration)

        case SourceContentType.VIDEO:
            existAudio = False
            isMono = False

            meta = ffmpeg.probe(vsml_content.src)
            for stream in meta.get('streams', []):
                if stream.get('codec_type') == 'audio':
                    existAudio = True
                    isMono = stream.get('channel_layout') == 'stereo'
                    break

            source = ffmpeg.input(vsml_content.src)
            source_audio = source.audio if existAudio else None
            if isMono:
                source_audio = ffmpeg.filter([source_audio, source_audio], 'amerge', inputs=2)

            duration = meta.get('format', {}).get('duration', None)
            if duration is not None:
                duration = float(duration)

            process = Process(source.video, source_audio, duration)

        case SourceContentType.TEXT:
            # TODO: テキスト対応
            process = None
            # process = ffmpeg.input('color=c=0x000000@0.0', f='lavfi')
            # process = ffmpeg.filter(process, 'drawtext', text=vsml_content.src)
        case _:
            raise Exception()

    if process is not None:
        video_process_item = process.video
        if video_process_item is not None:
            # TODO: ↓ここ透過画像とのconcatにしたいな
            video_process_item = ffmpeg.filter(video_process_item, 'pad', w=f'iw+{resolution.width}', h=f'ih+{resolution.height}')
            video_process_item = ffmpeg.crop(video_process_item, x=0, y=0, width=resolution.width, height=resolution.height)
        process.video = video_process_item

    return process

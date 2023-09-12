import ffmpeg
from typing import Optional
from vsml import SortType, VSMLContent
from utils import VSMLManager
from .schemas import Process
from .utils import get_transparent_process

def create_sequence_process(processes: list[Process], vsml_content: VSMLContent, debug_mode: bool = False) -> Process:
    video_process = None
    audio_process = None

    if vsml_content.duration:
        video_margin = 0
        audio_margin = 0
        for process_item in processes:
            if process_item is None:
                continue
            if process_item.duration is None:
                continue
            ## 映像の結合
            # 映像がない場合、時間マージンを加算する(後でtpadで足す)
            if process_item.video is None:
                video_margin += process_item.duration
            # 映像がある場合、マージンをつけつつ、映像を結合する(ベースの映像がなければそのストリームを使う)
            else:
                if video_margin:
                    process_item.video = ffmpeg.filter(process_item.video, 'tpad', start_duration=video_margin)
                    video_margin = 0
                if video_process is None:
                    video_process = process_item.video
                else:
                    video_process = ffmpeg.concat(video_process, process_item.video, v=1, a=0)

            ## 音声の結合
            # 音声がない場合、時間マージンを加算する(後でadelayで足す)
            if process_item.audio is None:
                audio_margin += process_item.duration
            # 音声がある場合、マージンをつけつつ、音声を結合する(ベースの音声がなければそのストリームを使う)
            else:
                if audio_margin:
                    process_item.audio = ffmpeg.filter(process_item.audio, 'adelay', f'{audio_margin}s')
                    audio_margin = 0
                if audio_process is None:
                    audio_process = process_item.audio
                else:
                    audio_process = ffmpeg.concat(audio_process, process_item.audio, v=0, a=1)

        # 余った時間マージンを追加する
        if video_margin and video_process:
            video_process = ffmpeg.filter(video_process, 'tpad', stop_duration=video_margin)
        if audio_margin and audio_process:
            audio_process = ffmpeg.filter(audio_process, 'apad', pad_dur=audio_margin)
    else:
        video_process = processes[0].video
        audio_process = processes[0].audio

    # Processにまとめてreturn
    return Process(video_process, audio_process, vsml_content.duration, vsml_content.resolution, vsml_content.start_position)

def create_parallel_process(processes: list[Process], vsml_content: VSMLContent, debug_mode: bool = False) -> Process:
    video_process = None
    audio_process = None

    # 動画または音声を含む場合
    if vsml_content.duration:
        video_max_length = 0.0
        audio_max_length = 0.0
        for process in processes:
            # 映像の合成
            if process.video:
                if process.duration:
                    video_max_length = min(vsml_content.duration, max(video_max_length, process.duration))
                else:
                    # 静止画系の処理
                    process.video = ffmpeg.trim(process.video, start=0, end=vsml_content.duration)
                    video_max_length = vsml_content.duration

                if video_process is None:
                    video_process = process.video
                else:
                    video_process = ffmpeg.overlay(video_process, process.video)
            # 音声の合成
            if process.audio:
                if audio_process is None:
                    audio_process = process.audio
                else:
                    audio_process = ffmpeg.filter([audio_process, process.audio], 'amix')
                if process.duration:
                        audio_max_length = min(vsml_content.duration, max(audio_max_length, process.duration))
        # 長さが足りていないときに要素を伸ばす
        if vsml_content.duration > video_max_length and video_process:
            video_process = ffmpeg.filter(video_process, 'tpad', stop_duration=audio_max_length-video_max_length)
        if vsml_content.duration > audio_max_length and audio_process:
            audio_process = ffmpeg.filter(audio_process, 'apad', pad_dur=video_max_length-audio_max_length)
    # 静止画系のみの場合
    else:
        for process_item in processes:
            process_item.video = ffmpeg.trim(process_item.video, start=0, end=1)
            if video_process is None:
                video_process = process_item.video
            else:
                video_process = ffmpeg.overlay(video_process, process_item.video)
        video_process = ffmpeg.filter(video_process, 'loop', loop=-1)

    # Processにまとめてreturn
    return Process(video_process, audio_process, vsml_content.duration, vsml_content.resolution, vsml_content.start_position)

def create_wrap_process(processes: list[Process], vsml_content: VSMLContent, debug_mode: bool = False) -> Optional[Process]:
    match len(processes):
        case 0:
            process = None
        case _:
            match vsml_content.type:
                case SortType.SEQUENCE:
                    process = create_sequence_process(processes, vsml_content, debug_mode)
                case SortType.PARALLEL:
                    process = create_parallel_process(processes, vsml_content, debug_mode)
                case _:
                    raise Exception()
    
    if vsml_content.start_position and vsml_content.resolution and vsml_content.background_color:
        box_process = ffmpeg.drawbox(
            get_transparent_process(VSMLManager.get_root_resolution().get_str()),
            vsml_content.start_position.x, vsml_content.start_position.y,
            vsml_content.resolution.width, vsml_content.resolution.height, vsml_content.background_color, 'fill',
            replace=1
        )
        if process:
            if process.video:
                process.video = ffmpeg.overlay(box_process, process.video, shortest=1)
            else:
                process.video = box_process
        else:
            process = Process(box_process, None, vsml_content.duration, vsml_content.resolution, vsml_content.start_position)

    return process

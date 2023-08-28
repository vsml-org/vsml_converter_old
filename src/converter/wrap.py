import ffmpeg
from typing import Optional
from vsml import SortType, SourceContentType
from .schemas import Process

def create_wrap_process(processes: list[Process], type: SortType, debug_mode: bool = False) -> Optional[Process]:
    match len(processes):
        case 0:
            process = None
        case 1:
            process = processes[0]
        case _:
            match type:
                case SortType.SEQUENCE:
                    whole_length = 0
                    video_process = None
                    audio_process = None
                    video_margin = 0
                    audio_margin = 0

                    for process_item in processes:
                        # processがNoneの場合スキップ
                        if process_item is None:
                            continue
                        # 長さのあるProcessの合計値を算出
                        if process_item.length is not None:
                            whole_length += process_item.length
                        # 映像の結合
                        if process_item.video is None:
                            if process_item.length is not None:
                                video_margin += process_item.length
                        else:
                            video_process_with_margin = ffmpeg.filter(process_item.video, 'tpad', start_duration=video_margin)
                            if video_process is None:
                                video_process = video_process_with_margin
                            else:
                                video_process = ffmpeg.concat(video_process, video_process_with_margin, v=1, a=0)
                        # 音声の結合
                        if process_item.audio is None:
                            if process_item.length is not None:
                                audio_margin += process_item.length
                        else:
                            audio_process_with_margin = ffmpeg.filter(process_item.audio, 'adelay', f'{audio_margin}s')
                            if audio_process is None:
                                audio_process = audio_process_with_margin
                            else:
                                audio_process = ffmpeg.concat(audio_process, audio_process_with_margin, v=0, a=1)

                    if video_margin and video_process:
                        video_process = ffmpeg.filter(video_process, 'tpad', stop_duration=video_margin)
                    if audio_margin and audio_process:
                        audio_process = ffmpeg.filter(audio_process, 'apad', pad_dur=audio_margin)

                    if video_process is None and audio_process is None:
                        process = None
                    else:
                        process = Process(video_process, audio_process, whole_length)

                case SortType.PARALLEL:
                    video_max_length = 0.0
                    audio_max_length = 0.0
                    for process_item in processes:
                        # processがNoneの場合スキップ
                        if process_item is None:
                            processes.pop(process_item)
                            continue
                        if process_item.video is not None and process_item.length is not None:
                            video_max_length = max(video_max_length, process_item.length)
                        if process_item.audio is not None and process_item.length is not None:
                            audio_max_length = max(audio_max_length, process_item.length)
                    max_length = max(video_max_length, audio_max_length)

                    video_process = None
                    audio_process = None
                    for process_item in processes:
                        # 映像の合成
                        if process_item.video is not None:
                            if process_item.length is None:
                                process_item.video = ffmpeg.trim(process_item.video, start=0, end=max_length)
                                video_max_length = max_length
                            if video_process is None:
                                video_process = process_item.video
                            else:
                                video_process = ffmpeg.overlay(video_process, process_item.video)
                        # 音声の合成
                        if process_item.audio is not None:
                            if audio_process is None:
                                audio_process = process_item.audio
                            else:
                                audio_process = ffmpeg.filter([audio_process, process_item.audio], 'amix')

                    if video_max_length > audio_max_length:
                        audio_process = ffmpeg.filter(audio_process, 'apad', pad_dur=video_max_length-audio_max_length)
                    elif video_max_length < audio_max_length:
                        video_process = ffmpeg.filter(video_process, 'tpad', stop_duration=audio_max_length-video_max_length)

                    if video_process is None and audio_process is None:
                        process = None
                    else:
                        process = Process(video_process, audio_process, max_length)
                case _:
                    raise Exception()
    return process

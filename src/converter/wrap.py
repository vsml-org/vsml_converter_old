import ffmpeg
from typing import Optional
from vsml import SortType
from utils import WidthHeight, Position
from .schemas import Process
from .utils import get_transparent_process

def create_sequence_process(processes: list[Process], resolution: WidthHeight, param: str, debug_mode: bool = False) -> Optional[Process]:
    whole_length = 0
    is_no_length = True
    process_start_position = Position(0, 0)
    process_end_position = Position(0, 0)
    process_size = None
    video_process = None
    audio_process = None

    for process_item in processes:
        # processがNoneの場合スキップ
        if process_item is None:
            processes.pop(process_item)
            continue

        if not (process_item.size is None or process_item.start_position is None):
            process_start_position.x = min(process_start_position.x, process_item.start_position.x)
            process_start_position.y = min(process_start_position.y, process_item.start_position.y)
            process_end_position.x = max(
                process_end_position.x,
                process_item.start_position.x+process_item.size.width
            )
            process_end_position.y = max(
                process_end_position.y,
                process_item.start_position.y+process_item.size.height
            )

        if process_item.length is not None:
            is_no_length = False
            # 長さのあるProcessの合計値を算出
            whole_length += process_item.length

    if is_no_length:
        video_process = processes[0].video
        audio_process = processes[0].audio
    else:
        video_margin = 0
        audio_margin = 0
        for process_item in processes:
            if process_item.length is None:
                continue
            ## 映像の結合
            # 映像がない場合、時間マージンを加算する(後でtpadで足す)
            if process_item.video is None:
                video_margin += process_item.length
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
                audio_margin += process_item.length
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

    if whole_length == 0:
        whole_length = None

    if process_start_position == Position(0, 0) and process_end_position == Position(0, 0):
        process_start_position = None
    else:
        process_size = WidthHeight(
            process_end_position.x - process_start_position.x,
            process_end_position.y - process_start_position.y
        )
        # TODO: 色指定なども考える
        if param:
            box_process = ffmpeg.drawbox(
                get_transparent_process(resolution.get_str()),
                process_start_position.x, process_start_position.y,
                process_size.width, process_size.height, 'red', 'fill',
                replace=1
            )
            video_process = ffmpeg.overlay(box_process, video_process)

    # Processにまとめてreturn
    if video_process is None and audio_process is None:
        process = None
    else:
        process = Process(video_process, audio_process, whole_length, process_size, process_start_position)

    return process

def create_parallel_process(processes: list[Process], resolution: WidthHeight, param: str, debug_mode: bool = False) -> Optional[Process]:
    video_max_length = 0.0
    audio_max_length = 0.0
    video_process = None
    audio_process = None
    process_start_position = Position(0, 0)
    process_end_position = Position(0, 0)
    process_size = None

    # max_lengthを計算
    for process_item in processes:
        # processがNoneの場合スキップ(ついでにリストから削除)
        if process_item is None:
            processes.pop(process_item)
            continue
        if not (process_item.size is None or process_item.start_position is None):
            process_start_position.x = min(process_start_position.x, process_item.start_position.x)
            process_start_position.y = min(process_start_position.y, process_item.start_position.y)
            process_end_position.x = max(
                process_end_position.x,
                process_item.start_position.x+process_item.size.width
            )
            process_end_position.y = max(
                process_end_position.y,
                process_item.start_position.y+process_item.size.height
            )

        if process_item.length is not None:
            if process_item.video is not None:
                video_max_length = max(video_max_length, process_item.length)
            if process_item.audio is not None:
                audio_max_length = max(audio_max_length, process_item.length)
    max_length = max(video_max_length, audio_max_length)

    if max_length == 0:
        for process_item in processes:
            process_item.video = ffmpeg.trim(process_item.video, start=0, end=1)
            if video_process is None:
                video_process = process_item.video
            else:
                video_process = ffmpeg.overlay(video_process, process_item.video)
        video_process = ffmpeg.filter(video_process, 'loop', loop=-1)
    else:
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
            if audio_process:
                audio_process = ffmpeg.filter(audio_process, 'apad', pad_dur=video_max_length-audio_max_length)
        elif video_max_length < audio_max_length:
            if video_process:
                video_process = ffmpeg.filter(video_process, 'tpad', stop_duration=audio_max_length-video_max_length)

    if max_length == 0:
        max_length = None

    if process_start_position == Position(0, 0) and process_end_position == Position(0, 0):
        process_start_position = None
    else:
        process_size = WidthHeight(
            process_end_position.x - process_start_position.x,
            process_end_position.y - process_start_position.y
        )
        # TODO: 色指定なども考える
        if param:
            box_process = ffmpeg.drawbox(
                get_transparent_process(resolution.get_str()),
                process_start_position.x, process_start_position.y,
                process_size.width, process_size.height, 'red', 'fill',
                replace=1
            )
            video_process = ffmpeg.overlay(box_process, video_process)

    # Processにまとめてreturn
    if video_process is None and audio_process is None:
        process = None
    else:
        process = Process(video_process, audio_process, max_length, process_size, process_start_position)
    return process

def create_wrap_process(processes: list[Process], resolution: WidthHeight, type: SortType, param: str, debug_mode: bool = False) -> Optional[Process]:
    match len(processes):
        case 0:
            process = None
        case _:
            match type:
                case SortType.SEQUENCE:
                    process = create_sequence_process(processes, resolution, param, debug_mode)
                case SortType.PARALLEL:
                    process = create_parallel_process(processes, resolution, param, debug_mode)
                case _:
                    raise Exception()
    return process

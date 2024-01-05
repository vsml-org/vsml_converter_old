from content import WrapContent
from converter.ffmpeg import (
    adjust_fit_sequence,
    concat_filter,
    get_background_color_code,
    object_length_filter,
    set_background_filter,
    time_space_end_filter,
    time_space_start_filter,
)
from converter.schemas import Process
from style import TimeValue


def create_sequence_process(
    child_processes: list[Process],
    vsml_content: WrapContent,
    debug_mode: bool = False,
) -> Process:
    video_process = None
    audio_process = None

    video_time_margin = TimeValue("0")
    audio_time_margin = TimeValue("0")
    previous_time_margin = TimeValue("0")

    style = vsml_content.style

    (
        width_with_padding,
        height_with_padding,
    ) = style.get_size_with_padding()
    background_color_code = get_background_color_code(style.background_color)

    for child_process in child_processes:
        child_style = child_process.style
        length_with_padding = child_style.get_object_length_with_padding()

        max_time_margin = max(
            previous_time_margin,
            child_style.time_margin_start,
        )
        # オブジェクトの始めの余白時間は1つ前のオブジェクトの終わりの余白時間との最大値を取り、その値で余白を付ける
        child_process.video, child_process.audio = time_space_start_filter(
            max_time_margin,
            background_color_code,
            child_process.video,
            child_process.audio,
        )

        previous_time_margin = child_style.time_margin_end

        if child_process.video is not None:
            # concatのため解像度を合わせた透明背景を設定
            child_process.video = set_background_filter(
                width=width_with_padding,
                height=height_with_padding,
                background_color=style.background_color,
                video_process=child_process.video,
                fit_video_process=True,
            )
            child_process.video, _ = time_space_start_filter(
                video_time_margin,
                background_color_code,
                video_process=child_process.video,
            )
            video_time_margin = TimeValue("0")
            video_process = concat_filter(
                video_process, child_process.video, is_video=True
            )
        else:
            # 映像が存在しない場合、余白時間を加算し、後で余白を付ける
            video_time_margin += max_time_margin + length_with_padding
        if child_process.audio is not None:
            _, child_process.audio = time_space_start_filter(
                audio_time_margin,
                background_color_code,
                audio_process=child_process.audio,
            )
            audio_time_margin = TimeValue("0")
            audio_process = concat_filter(
                audio_process, child_process.audio, is_video=False
            )
        else:
            # 音声が存在しない場合、余白時間を加算し、後で余白を付ける
            audio_time_margin += max_time_margin + length_with_padding

        # FITな子要素があれば以降をこのオブジェクトで埋める
        if child_style.object_length.is_fit():
            video_process, audio_process = adjust_fit_sequence(
                background_color_code, video_process, audio_process
            )
            video_time_margin = TimeValue("0")
            audio_time_margin = TimeValue("0")
            previous_time_margin = TimeValue("0")
            break

    # 余った時間マージンを追加する
    if video_process is not None:
        video_remain_time_margin = video_time_margin + previous_time_margin
        if video_remain_time_margin.is_zero_over():
            video_process, _ = time_space_end_filter(
                video_remain_time_margin,
                background_color_code,
                video_process=video_process,
            )
    if audio_process is not None:
        audio_remain_time_margin = audio_time_margin + previous_time_margin
        if audio_remain_time_margin.is_zero_over():
            _, audio_process = time_space_end_filter(
                audio_remain_time_margin,
                audio_process=audio_process,
            )
    video_process, audio_process = object_length_filter(
        style.object_length,
        video_process=video_process,
        audio_process=audio_process,
    )

    return Process(
        video_process,
        audio_process,
        vsml_content.style,
    )

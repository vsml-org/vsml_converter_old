from content import WrapContent
from converter.ffmpeg import (
    adjust_parallel_audio,
    audio_merge_filter,
    get_background_color_code,
    get_background_process,
    layering_filter,
    object_length_filter,
    time_space_end_filter,
    time_space_start_filter,
)
from converter.schemas import Process
from style import GraphicValue, LayerMode


def create_parallel_process(
    child_processes: list[Process],
    vsml_content: WrapContent,
    debug_mode: bool = False,
) -> Process:
    video_process = None
    audio_process = None

    style = vsml_content.style
    width_with_padding = style.get_width_with_padding()
    height_with_padding = style.get_height_with_padding()

    background_color_code = get_background_color_code(style.background_color)
    if vsml_content.exist_video:
        video_process = get_background_process(
            "{}x{}".format(
                width_with_padding.get_pixel(),
                height_with_padding.get_pixel(),
            ),
            style.background_color,
        )
        video_process, _ = object_length_filter(
            style.object_length, video_process=video_process
        )

    is_single = style.layer_mode == LayerMode.SINGLE
    is_row = style.direction is None or style.direction.is_row()
    is_reverse = style.direction is None or style.direction.is_reverse
    current_graphic_length = (
        (
            width_with_padding - style.padding_right
            if is_row
            else height_with_padding - style.padding_bottom
        )
        if is_reverse
        else (style.padding_left if is_row else style.padding_top)
    )

    remain_margin = GraphicValue("0")

    for child_process in child_processes:
        child_style = child_process.style
        child_process.video, child_process.audio = time_space_start_filter(
            child_style.time_margin_start,
            background_color_code,
            child_process.video,
            child_process.audio,
        )
        if not child_style.object_length.is_fit():
            child_process.video, child_process.audio = time_space_end_filter(
                child_style.time_margin_end,
                background_color_code,
                child_process.video,
                child_process.audio,
            )
        if child_process.video is not None:
            # この子要素と一つ前の子要素の間のmarginの長さ
            max_space = max(
                (
                    child_style.margin_left
                    if is_row
                    else child_style.margin_top
                ),
                remain_margin,
            )
            # この子要素の本体分のずらす長さ
            child_graphic_length = (
                child_style.get_width_with_padding()
                if is_row
                else child_style.get_height_with_padding()
            )

            # 正順ならmargin分進んだ位置に、リバースなら全体から本体分戻した位置に子要素を配置
            current_graphic_length += (
                -child_graphic_length if is_reverse else max_space
            )
            # 左上の位置を指定して子要素を配置する
            video_process = layering_filter(
                video_process,
                child_process.video,
                (
                    current_graphic_length
                    if is_single and is_row
                    else style.padding_left + child_style.margin_left
                ),
                (
                    current_graphic_length
                    if is_single and not is_row
                    else style.padding_top + child_style.margin_top
                ),
            )
            # 正順なら本体分進めておき、リバースならmargin分戻しておく
            current_graphic_length += (
                -max_space if is_reverse else child_graphic_length
            )
            # 次の周で使うmargin
            remain_margin = (
                child_style.margin_right
                if is_row
                else child_style.margin_bottom
            )
        if child_process.audio is not None:
            audio_process = audio_merge_filter(
                audio_process, child_process.audio
            )
    if audio_process is not None:
        audio_process = adjust_parallel_audio(
            style.object_length, audio_process
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

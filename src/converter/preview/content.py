from typing import Optional

from style import Order
from vsml import SourceContent, VSMLContent, WrapContent


def pick_data(
    vsml_content: VSMLContent, second: float
) -> Optional[VSMLContent]:
    if not vsml_content.exist_video:
        return None
    if isinstance(vsml_content, WrapContent):
        if vsml_content.style.order == Order.SEQUENCE:
            items = vsml_content.items
            vsml_content.items = []
            whole_second = 0
            left_margin_end = 0

            for item in items:
                whole_second += max(
                    item.style.time_margin_start.get_second(), left_margin_end
                )
                if second < whole_second:
                    return vsml_content
                whole_second += item.style.time_padding_start.get_second()
                if second < whole_second:
                    item._second = -1
                    vsml_content.items = [item]
                    return vsml_content
                whole_second_with_object_length = (
                    whole_second + item.style.object_length.get_second()
                )
                if second < whole_second_with_object_length:
                    child = pick_data(item, second - whole_second)
                    if child is not None:
                        vsml_content.items = [child]
                    return vsml_content
                whole_second = whole_second_with_object_length
                whole_second += item.style.time_padding_end.get_second()
                if second < whole_second:
                    item._second = -1
                    vsml_content.items = [item]
                    return vsml_content
                left_margin_end = item.style.time_margin_end.get_second()

        elif vsml_content.style.order == Order.PARALLEL:
            items = vsml_content.items
            vsml_content.items = []

            for item in items:
                whole_second = item.style.time_margin_start.get_second()
                if second < whole_second:
                    continue
                whole_second += item.style.time_padding_start.get_second()
                if second < whole_second:
                    item._second = -1
                    vsml_content.items.append(item)
                    continue
                whole_second_with_object_length = (
                    whole_second + item.style.object_length.get_second()
                )
                if (
                    second < whole_second_with_object_length
                    or item.style.object_length.is_fit()
                ):
                    child = pick_data(item, second - whole_second)
                    if child is not None:
                        vsml_content.items.append(child)
                    continue
                whole_second = whole_second_with_object_length
                whole_second += item.style.time_padding_end.get_second()
                if second < whole_second:
                    item._second = -1
                    vsml_content.items.append(item)
                    continue
            return vsml_content

        else:
            raise Exception()
    elif isinstance(vsml_content, SourceContent):
        vsml_content._second = second
        return vsml_content
    else:
        raise Exception()

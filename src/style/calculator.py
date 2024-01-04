from typing import Optional

from utils import VSMLManager

from .types import GraphicUnit, GraphicValue, TimeUnit, TimeValue


def time_calculator(
    value: TimeValue,
    parent_value: Optional[TimeValue] = None,
    source_value: Optional[TimeValue] = None,
) -> TimeValue:
    # FIT
    output_value = TimeValue("fit")
    match value.unit:
        case TimeUnit.SECOND | TimeUnit.FRAME:
            # SECOND, FRAME
            output_value = value
        case TimeUnit.PERCENT:
            if parent_value is not None:
                output_value.value = parent_value.value * value.value / 100
                # SECOND, FRAME
                output_value.unit = parent_value.unit
            elif source_value is not None:
                # SECOND
                output_value = source_value
        case TimeUnit.SOURCE:
            if source_value is not None:
                # SECOND
                output_value = source_value
    return output_value


def graphic_calculator(
    value: GraphicValue,
    parent_pixel: Optional[int] = None,
    source_value: Optional[GraphicValue] = None,
) -> GraphicValue:
    # AUTO
    output_value = GraphicValue("auto")
    match value.unit:
        case GraphicUnit.PIXEL:
            # PIXEL
            output_value = value
        case GraphicUnit.PERCENT:
            if parent_pixel is not None:
                output_value.value = int(parent_pixel * value.value / 100)
                # PIXEL
                output_value.unit = GraphicUnit.PIXEL
            elif source_value is not None:
                # PIXEL
                output_value = source_value
        case GraphicUnit.RESOLUTION_WIDTH:
            output_value.value = int(
                VSMLManager.get_root_resolution().width * value.value / 100
            )
            # PIXEL
            output_value.unit = GraphicUnit.PIXEL
        case GraphicUnit.RESOLUTION_HEIGHT:
            output_value.value = int(
                VSMLManager.get_root_resolution().height * value.value / 100
            )
            # PIXEL
            output_value.unit = GraphicUnit.PIXEL
        case GraphicUnit.RESOLUTION_MIN:
            output_value.value = int(
                VSMLManager.get_root_resolution().get_min() * value.value / 100
            )
            # PIXEL
            output_value.unit = GraphicUnit.PIXEL
        case GraphicUnit.RESOLUTION_MAX:
            output_value.value = int(
                VSMLManager.get_root_resolution().get_max() * value.value / 100
            )
            # PIXEL
            output_value.unit = GraphicUnit.PIXEL
    return output_value

from typing import Optional

from utils import VSMLManager

from .types import GraphicUnit, GraphicValue


def graphic_calculator(
    value: GraphicValue,
    parent_pixel: Optional[int] = None,
    source_value: Optional[GraphicValue] = None,
) -> GraphicValue:
    output_value = GraphicValue("auto")
    match value.unit:
        case GraphicUnit.PERCENT:
            if parent_pixel is None:
                if source_value is None:
                    # AUTO
                    output_value.unit = GraphicUnit.AUTO
                else:
                    # PIXEL
                    output_value = source_value
            else:
                output_value.value = int(parent_pixel * value.value / 100)
                # PIXEL
                output_value.unit = GraphicUnit.PIXEL
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

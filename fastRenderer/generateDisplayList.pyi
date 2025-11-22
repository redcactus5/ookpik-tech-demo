# render_loop.pyi
from typing import List, Tuple
from configAndTools import BasicSprite
from pygame import Rect
from pygame import surface

def fastDisplayListGeneratorLoop(
    internalLayersReference: list[set[BasicSprite]],
    cameraRectReference: Rect
) -> List[Tuple[surface.Surface, Tuple[int, int]]]: ...
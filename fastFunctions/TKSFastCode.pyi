
from typing import List, Tuple,Any
from TKSSprites import BasicSprite
from pygame import Rect
from pygame import surface

class ImageSize:
    x: int
    y: int

    def __init__(self, x: int, y: int) -> None: ...
    

class SpriteSheetData:
    frame: int
    imageSizeList: List[ImageSize]
    frameList: List[Any]  # List of pygame.Surface objects or any Python object

    def __init__(self) -> None: ...
    def addFrame(self, surface: Any, width: int, height: int) -> None: ...
    

class SpriteRenderData:
    imageX: int
    imageY: int
    offsetX: int
    offsetY: int
    visible: bool

def fastDisplayListGeneratorLoop(
    internalLayersReference: list[set[BasicSprite]],
    cameraRectReference: Rect
) -> List[Tuple[surface.Surface, Tuple[int, int]]]: ...
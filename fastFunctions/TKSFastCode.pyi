
from typing import List, Tuple,Any
from TKSSprites import BasicSprite,AnimationSet
from pygame import Rect
from pygame import surface




class ImageSize:
    width: int
    height: int

    def __init__(self, width: int, height: int) -> None: ...
    

class FastRect:
    x: int
    y: int
    width:int
    height:int
    def __init__(self, x: int, y: int, width: int, height: int) -> None: ...



class Camera:
    x: int
    y: int
    width: int
    height: int

    def __init__(self, x: int = 0, y: int = 0, width: int = 0, height: int = 0) -> None: ...
    
    def getPos(self) -> tuple[int, int]: ...
    
    def setPos(self, x: int, y: int) -> None: ...
    
    def move(self, x: int, y: int) -> None: ...


class SpriteSheetData:
    frame: int
    imageSizeList: List[ImageSize]
    frameList: List[Any]  # List of pygame.Surface objects or any Python object

    def __init__(self) -> None: ...
    def addFrame(self, surface: Any, width: int, height: int) -> None: ...
    

class SpriteRenderData:
    imageX: int
    imageY: int
    imageOffsetX: int
    imageOffsetY: int
    visible: bool


class SpriteSetData:
    animations: List[SpriteSetData]  # list of animation data (unspecified type)
    currentAnim: int

    def __init__(self, animationDataList: List[SpriteSetData], startingAnimation: int = 0) -> None: ...

def fastDisplayListGeneratorLoop(
    internalLayersReference: list[set[BasicSprite]],
    cameraRectReference: Rect
) -> List[Tuple[surface.Surface, Tuple[int, int]]]: ...
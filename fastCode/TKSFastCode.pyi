import pygame
from typing import List, Tuple, Optional

class FastRect:
    x: int
    y: int
    width: int
    height: int

    def __init__(self, x: int = 0, y: int = 0, width: int = 0, height: int = 0) -> None: ...
    def getPygameEquivalent(self) -> Tuple[int, int, int, int]: ...


class ImageSize:
    width: int
    height: int

    def __init__(self, width: int = 0, height: int = 0) -> None: ...


class AnimationFrames:
    length: int
    imageSizeList: List[ImageSize]
    frameList: List[pygame.Surface]

    def __init__(self, animationFrames: List[pygame.Surface]) -> None: ...


class Animation:
    sheetData: AnimationFrames
    startingFrame: int
    looping: bool
    frameRate: int
    frameRateDelay: float
    lengthMinusOne: int
    length: int

    def __init__(self, frames: AnimationFrames, startingFrame: int, frameRate: int, shouldLoop: bool) -> None: ...


class AnimationControllerCore:
    animations: List[Animation]
    animationsLen: int
    currentAnimIndex: int
    frame: int
    lastFrame: int
    frameTimeCarry: float
    frameTime: float
    correctedFrameTime: float
    unpaused: bool
    passedFrames: int
    prospectiveFrame: int
    currentAnimation: Animation
    currentFrameSize: ImageSize
    currentImage: pygame.Surface

    def __init__(self, animationDataList: List[Animation], startingAnimation: int = 0) -> None: ...
    def swapAnimation(self, newAnimationIndex: int) -> None: ...
    def frameUpdate(self, frameTime: float) -> None: ...
    def pause(self) -> None: ...
    def play(self) -> None: ...
    def setFrame(self, frame: int) -> None: ...
    def resetAnimation(self) -> None: ...


class SpriteCore:
    x: int
    y: int
    width: int
    height: int
    imageOffsetX: int
    imageOffsetY: int
    visible: bool
    animationController: AnimationControllerCore

    def __init__(
        self, x: int, y: int, width: int, height: int,
        visible: bool, animationController: AnimationControllerCore,
        imageOffsetX: int = 0, imageOffsetY: int = 0
    ) -> None: ...
    def show(self) -> None: ...
    def hide(self) -> None: ...
    def setPos(self, x: int, y: int) -> None: ...
    def move(self, x: int, y: int) -> None: ...
    def setTextureOffset(self, x: int, y: int) -> None: ...


class TileSpriteCore(SpriteCore):
    tileSize: int
    tileX: int
    tileY: int
    tileOffsetX: int
    tileOffsetY: int

    def __init__(
        self, tileX: int, tileY: int, width: int, height: int, tileSize: int,
        visible: bool, animationController: AnimationControllerCore,
        imageOffsetX: int = 0, imageOffsetY: int = 0,
        tileOffsetX: int = 0, tileOffsetY: int = 0
    ) -> None: ...
    def move(self, x: int, y: int) -> None: ...
    def setPos(self, x: int, y: int) -> None: ...
    def tileMove(self, x: int, y: int) -> None: ...
    def setTilePos(self, x: int, y: int) -> None: ...
    def getTileOffset(self) -> Tuple[int, int]: ...
    def setTileOffset(self, x: int, y: int) -> None: ...
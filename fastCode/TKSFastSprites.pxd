# Cython header file for sprite and animation classes

import pygame

cdef class FastRect:
    """
    Constructor: FastRect(x:int, y:int, width:int, height:int)
    """
    cdef public long x
    cdef public long y
    cdef public long width
    cdef public long height

    cpdef tuple getPygameEquivalent(self)

cdef class ImageSize:
    """
    Constructor: ImageSize(width:int, height:int)
    """
    cdef public int width
    cdef public int height

cdef class AnimationFrames:
    """
    Constructor: AnimationFrames(animationFrames: list[pygame.Surface])
    """
    cdef public int length
    cdef public list[ImageSize] imageSizeList
    cdef public list[pygame.Surface] frameList

cdef class Animation:
    """
    Constructor: Animation(frames: AnimationFrames, startingFrame:int, frameRate:int, shouldLoop:bool)
    """
    cdef public AnimationFrames sheetData
    cdef public int startingFrame
    cdef public bint looping
    cdef public int frameRate
    cdef public double frameRateDelay
    cdef public int lengthMinusOne
    cdef public int length

cdef class AnimationControllerCore:
    cdef public list animations
    cdef public int animationsLen
    cdef public int currentAnimIndex
    cdef public int frame
    cdef public int lastFrame
    cdef public double frameTimeCarry
    cdef public double frameTime
    cdef public double correctedFrameTime
    cdef public bint unpaused
    cdef public int passedFrames
    cdef public int prospectiveFrame
    cdef public Animation currentAnimation
    cdef public ImageSize currentFrameSize
    cdef public pygame.Surface currentImage

    cpdef void swapAnimation(self, int newAnimationIndex)
    cpdef void frameUpdate(self, float frameTime)
    cpdef pause(self)
    cpdef play(self)
    cpdef setFrame(self, int frame)
    cpdef resetAnimation(self)

cdef class SpriteCore:
    cdef public long x
    cdef public long y
    cdef public int width
    cdef public int height
    cdef public int imageOffsetX
    cdef public int imageOffsetY
    cdef public bint visible
    cdef public AnimationControllerCore animationController

    cpdef show(self)
    cpdef hide(self)
    cpdef setPos(self, long x, long y)
    cpdef move(self, long x, long y)
    cpdef setTextureOffset(self, int x, int y)
    cpdef setAnimationControllerCore(self, AnimationControllerCore newAnimController)

cdef class TileSpriteCore(SpriteCore):
    cdef public int tileSize
    cdef public long tileX
    cdef public long tileY
    cdef public int tileOffsetX
    cdef public int tileOffsetY

    cpdef move(self, long x, long y)
    cpdef setPos(self, long x, long y)
    cpdef tileMove(self, long x, long y)
    cpdef setTilePos(self, long x, long y)
    cpdef getTileOffset(self)
    cpdef setTileOffset(self, int x, int y)
    cpdef setAnimationControllerCore(self, AnimationControllerCore newAnimController)
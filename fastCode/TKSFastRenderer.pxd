import numpy as np
cimport numpy as np

import pygame
import threading

from fastCode.TKSFastSprites cimport (
    SpriteCore,
    AnimationControllerCore,
    TileSpriteCore,
    ImageSize,
    AnimationFrames
)

import TKSSprites


# =========================
# Camera
# =========================

cdef class Camera:
    cdef public long x
    cdef public long y
    cdef public int width
    cdef public int height
    cdef public object name

    cpdef getPos(self)
    cpdef setPos(self, long x, long y)
    cpdef move(self, long x, long y)

    cdef setSize(self, int newWidth, int newHeight)


# =========================
# DisplayListManager
# =========================

cdef class DisplayListManager:
    cdef int fps
    cdef list displayList
    cdef int frameCounter
    cdef object averagingNumbersBackend
    cdef long averagingNumber
    cdef long averageSize
    cdef long lastAverage
    cdef object append
    cdef object clear

    cpdef list generateDisplayList(
        self,
        list internalLayersReference,
        Camera cameraReference
    )


# =========================
# SceneManager
# =========================

cdef class SceneManager:
    cdef Camera currentCamera
    cdef list layers
    cdef list internalLayers
    cdef list indexLookupTables
    cdef list cameras

    cpdef reset(
        self,
        int startingLayerCount,
        long startingCameraX,
        long startingCameraY,
        int internalWidth,
        int internalHeight
    )

    cdef _getInternalLayers(self)

    cpdef int getLayerCount(self)

    cpdef insertLayer(self, int index)
    cpdef addLayer(self)
    cpdef removeLayer(self, int index)

    cpdef changeCamera(self, int index)
    cpdef Camera getCamera(self, int index)
    cpdef Camera getCurrentCamera(self)
    cpdef removeCamera(self, int targetIndex)
    cpdef addCamera(self, Camera newCamera)
    cpdef insertCamera(self, Camera newCamera, int insertionIndex)
    cpdef int findCamera(self, Camera cameraToFind)

    cpdef moveCurrentCamera(self, long x, long y)
    cpdef setCurrentCameraPos(self, long x, long y)

    cpdef addSprite(self, int layerIndex, TKSSprites.BasicSprite newSprite)
    cpdef addMultipleSprites(
        self,
        int layerIndex,
        list newSpriteList
    )

    cpdef swapLayersByIndex(self, int layerID1, int layerID2)
    cpdef swapLayers(self, list layer1, list layer2)

    cpdef deleteSprite(self, TKSSprites.BasicSprite sprite, int layer)
    cpdef deleteSprites(self, list spriteList, int layer)
    cpdef deleteSpriteFromAllLayers(self, TKSSprites.BasicSprite sprite)
    cpdef deleteSpritesFromAllLayers(self, list spriteList)

    cpdef clearAllLayers(self)
    cpdef clearLayer(self, int index)


# =========================
# Renderer
# =========================

cdef class Renderer:
    # configuration
    cdef int internalWidth
    cdef int internalHeight
    cdef tuple clearColor
    cdef tuple backgroundColor
    cdef int targetFrameRate

    # window + buffers
    cdef pygame.Surface screen
    cdef pygame.Surface letterBoxViewPort
    cdef pygame.Surface integerScaleBuffer
    cdef pygame.Surface displayFrameBuffer
    cdef pygame.Surface renderFrameBuffer
    cdef pygame.Surface transferFrameBuffer
    cdef pygame.Surface menuFrameBuffer
    cdef pygame.Surface framebufferSwapPointer

    # scaling
    cdef list scaledDisplayRect
    cdef list integerBufferSize
    cdef int scaledWidth
    cdef int scaledHeight
    cdef list scaledSize
    cdef int scaledDisplayOffsetX
    cdef int scaledDisplayOffsetY
    cdef list scaledDisplayOffset
    cdef int scaledStepSize
    cdef bint shouldSmoothScale

    # rendering control
    cdef bint shouldDraw
    cdef tuple oldSize
    cdef threading.Lock frameBufferSwapLock
    cdef threading.Event newFrameTrigger
    cdef bint started

    # scene/render subsystems
    cdef SceneManager currentSceneManager
    cdef DisplayListManager currentDisplayListManager

    # temp math
    cdef int intScalingValue
    cdef float floatScalingValue
    cdef int clearFlag
    cdef list scalingDataPacket

    cpdef start(
        self,
        int internalDisplayWidth,
        int internalDisplayHeight,
        tuple clearColor,
        tuple backgroundColor,
        int scaleStepSize,
        int targetFrameRate,
        int startingLayerCount,
        long startingCameraX=?,
        long startingCameraY=?
    )

    cpdef reset(self)
    cpdef SceneManager getCurrentSceneManager(self)
    cpdef _calculateScaling(self, tuple screenSize)
    cpdef list getWindowData(self)
    cpdef frameTick(self)
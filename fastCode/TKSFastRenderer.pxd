
import numpy as np
cimport numpy as np
import pygame
cimport pygame
from fastCode.TKSFastSprites cimport SpriteCore, AnimationControllerCore, TileSpriteCore, ImageSize, AnimationFrames
import TKSSprites

cdef class Camera:
    cdef public long x
    cdef public long y
    cdef public int width
    cdef public int height
    cdef public str name



    cpdef tuple getPos(self)
    cpdef setPos(self, long x, long y)
    cpdef move(self, long x, long y)


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


    cpdef list[list] generateDisplayList(self, list[set[SpriteCore]] internalLayersReference, Camera cameraReference)


cdef class SceneManager:
    cdef Camera currentCamera
    cdef list[list[TKSSprites.BasicSprite]] layers
    cdef list[list[SpriteCore]] internalLayers
    cdef list[dict[TKSSprites.BasicSprite, int]] indexLookupTables
    cdef list[Camera] cameras

    
    cpdef reset(self, int startingLayerCount, long startingCameraX, long startingCameraY, int internalWidth, int internalHeight)
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
    cpdef addMultipleSprites(self, int layerIndex, list[TKSSprites.BasicSprite] newSpriteList)
    cpdef swapLayersByIndex(self, int layerID1, int layerID2)
    cpdef swapLayers(self, list layer1, list layer2)
    cpdef deleteSprite(self, TKSSprites.BasicSprite sprite, int layer)
    cpdef deleteSprites(self, list[TKSSprites.BasicSprite] spriteList, int layer)
    cpdef deleteSpriteFromAllLayers(self, TKSSprites.BasicSprite sprite)
    cpdef deleteSpritesFromAllLayers(self, list[TKSSprites.BasicSprite] spriteList)
    cpdef clearAllLayers(self)
    cpdef clearLayer(self, int index)


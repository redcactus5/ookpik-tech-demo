from libc.stdint cimport int32_t


def fastDisplayListGeneratorLoop(set internalLayersReference, object cameraRectReference):
    #cache the camera positions
    cdef int cameraLeft=cameraRectReference.left
    cdef int cameraRight=cameraRectReference.right
    cdef int cameraTop=cameraRectReference.top
    cdef int cameraBottom=cameraRectReference.bottom

    #create some variables for objects
    cdef list displayList=[]
    cdef set layer
    cdef object sprite
    cdef object spriteSheet
    cdef list[object] textures
    cdef object imageRect
    cdef int frameIndex

    #variables for the four corners and coords
    cdef int spriteLeft
    cdef int spriteRight
    cdef int spriteTop
    cdef int spriteBottom
    cdef int spriteX
    cdef int spriteY

    #the main nested loops
    for layer in internalLayersReference:
        for sprite in layer:
            #early visibility check optimisation
            if(<bool>sprite.visible):
                #load the sprites
                imageRect=sprite.imageRect
                spriteLeft=imageRect.left
                spriteRight=imageRect.right
                spriteTop=imageRect.top
                spriteBottom=imageRect.bottom
                spriteX=imageRect.x
                spriteY=imageRect.y
                #viewport culling check
                if((spriteRight >= cameraLeft)and(spriteLeft <= cameraRight)and
                    (spriteTop <= cameraBottom)and(spriteBottom  >= cameraTop)):
                    spriteSheet=sprite.currentSpriteSheet
                    textures=spriteSheet.textures
                    frameIndex=spriteSheet.frame
                    displayList.append((textures[frameIndex], (spriteX - cameraLeft, spriteY - cameraTop)))
    return displayList






from libc.stdint cimport int32_t


def fastDisplayListGeneratorLoop(object internalLayersReference, object cameraRectReference):
    #cache the camera positions
    cdef int cameraLeft=cameraRectReference.left
    cdef int cameraRight=cameraRectReference.right
    cdef int cameraTop=cameraRectReference.top
    cdef int cameraBottom=cameraRectReference.bottom

    #create some variables for objects
    cdef list displayList=[]
    cdef set layer
    cdef object sprite

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
            #load the sprites
            spriteLeft=sprite.rect.left
            spriteRight=sprite.rect.right
            spriteTop=sprite.rect.top
            spriteBottom=sprite.rect.bottom
            spriteX=sprite.rect.x
            spriteY=sprite.rect.y

            if ((spriteRight >= cameraLeft)and(spriteLeft <= cameraRight)and
                (spriteTop <= cameraBottom)and(spriteBottom  >= cameraTop)):
                displayList.append((sprite.image, (spriteX - cameraLeft, spriteY - cameraTop)))
    return displayList






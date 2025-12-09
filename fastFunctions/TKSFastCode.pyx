from libc.stdint cimport int32_t



cdef class ImageSize:
    cdef public int x
    cdef public int y

    def __cinit__(self,x,y):
        self.x=x
        self.y=y

    def __init__(self, x=0, y=0):
        pass


cdef class SpriteSheetData:
    cdef public int frame
    cdef public list imageSizeList    # list of IntPair objects
    cdef public list frameList        # list of Surfaces or frames

    def __cinit__(self):
        self.frame=0
        self.imageSizeList=[]
        self.frameList=[]

    def addFrame(self, surface, width, height):
        self.frameList.append(surface)
        self.imageSizeList.append(ImageSize(width, height))



cdef class SpriteRenderData:
    cdef public int imageX
    cdef public int imageY
    cdef public int imageOffsetX
    cdef public int imageOffsetY
    cdef public bint visible

    def __cinit__(self,imageX,imageY,imageOffsetX,imageOffsetY,visible):
        self.imageX=imageX
        self.imageY=imageY
        self.imageOffsetX=imageOffsetX
        self.imageOffsetY=imageOffsetY
        self.visible=visible



def fastDisplayListGeneratorLoop(list internalLayersReference, object cameraRectReference):
    #cache the camera positions
    cdef object cameraRect=cameraRectReference
    cdef int cameraLeft=cameraRect.left
    cdef int cameraRight=cameraRect.right
    cdef int cameraTop=cameraRect.top
    cdef int cameraBottom=cameraRect.bottom

    #cache the reference to internalLayers
    cdef list internalLayers=internalLayersReference

    #create some variables for objects
    cdef list displayList=[]
    #cache the display list append function
    cdef object append = displayList.append
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
                    append((textures[frameIndex], (spriteX - cameraLeft, spriteY - cameraTop)))
    return displayList






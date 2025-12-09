from libc.stdint cimport int32_t


cdef class FastRect:
    cdef public int x
    cdef public int y
    cdef public int width
    cdef public int height

    def __cinit__(self,x,y,width,height):
        self.x=x
        self.y=y
        self.width=width
        self.height=height

    def __init__(self,x=0,y=0,width=0,height=0) -> None:
        pass


cdef class Camera:
    cdef public int x
    cdef public int y
    cdef public int width
    cdef public int height
    def __cinit__(self,x,y,width,height) -> None:
        self.x=x
        self.y=y
        self.width=width
        self.height=height
    
    def __init__(self,x=0,y=0,width=0,height=0) -> None:
        pass

    def getPos(self):
        return (self.x, self.y)
    
    def setPos(self,x,y):
        self.x=x
        self.y=y
    
    def move(self,x,y):
        self.x+=x
        self.y+=y

cdef class ImageSize:
    cdef public int width
    cdef public int height

    def __cinit__(self,width,height):
        self.width=width
        self.height=height

    def __init__(self, width=0, height=0):
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

cdef class SpriteSetData:
    cdef public list animations
    cdef public int currentAnim

    def __cinit__(self, animationDataList,startingAnimation=0):
        self.currentAnim=startingAnimation
        self.animations=animationDataList
            
            



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


#need to be reworked for new sprite render data system
def fastDisplayListGeneratorLoop(list internalLayersReference, Camera cameraReference):
    #cache the camera positions
    cdef Camera camera=cameraReference
    cdef int cameraLeft=camera.x
    cdef int cameraRight=camera.x+camera.width
    cdef int cameraTop=camera.y
    cdef int cameraBottom=camera.y+camera.height

    #cache the reference to internalLayers
    cdef list internalLayers=internalLayersReference

    #create some variables for objects
    cdef list displayList=[]
    #cache the display list append function
    cdef object append = displayList.append
    cdef set layer
    cdef object sprite
    cdef SpriteRenderData SpriteData
    cdef object spriteSheet
    cdef SpriteSheetData sheetData
    cdef ImageSize frameSize

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
            SpriteData=sprite.renderData
            #early visibility check optimisation
            if(SpriteData.visible):
                #load the sprites
                spriteSheet=sprite.currentSpriteSheet
                sheetData=spriteSheet.renderingData
                frameSize=sheetData.imageSizeList[sheetData.frame]
                spriteX=SpriteData.imageX+SpriteData.imageOffsetX
                spriteY=SpriteData.imageY+SpriteData.imageOffsetY
                spriteLeft=spriteX
                spriteRight=spriteLeft+frameSize.width
                spriteTop=spriteY
                spriteBottom=spriteTop+frameSize.height
                
                #viewport culling check
                if((spriteRight >= cameraLeft)and(spriteLeft <= cameraRight)and
                    (spriteTop <= cameraBottom)and(spriteBottom  >= cameraTop)):
                    append((sheetData.frameList[sheetData.frame], (spriteX - cameraLeft, spriteY - cameraTop)))
    return displayList






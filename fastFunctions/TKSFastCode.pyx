import numpy as np
cimport numpy as np

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

cdef class AnimationFrames:
    cdef public int length
    cdef public list imageSizeList    # list of IntPair objects
    cdef public list frameList        # list of Surfaces or frames

    def __cinit__(self,animationFrames):
        #the lists for the data for every frame
        self.imageSizeList=[]
        self.frameList=[]
        #loop through and get the size for every frame and store it
        for frame in animationFrames:
            self.frameList.append(frame)
            self.imageSizeList.append(ImageSize(frame.width, frame.height))
        #cache our length
        self.length=len(self.frameList)

    def __init__(self,animationFrames) -> None:
        pass


cdef class Animation:
    #the sprite sheet for this animation
    cdef public AnimationFrames sheetData
    #config data
    cdef public int startingFrame
    cdef public bint looping
    cdef public int frameRate
    cdef public double frameRateDelay
    cdef public int lengthMinusOne
    cdef public int length

    def __cinit__(self,frames,startingFrame,frameRate,shouldLoop):
        self.sheetData=frames
        self.startingFrame=startingFrame
        self.looping=shouldLoop
        self.frameRate=frameRate
        #precalculate the frame delay
        if(self.frameRate>0):
            self.frameRateDelay=1/self.frameRate
        else:
            self.frameRateDelay=0
        self.lengthMinusOne=self.sheetData.length-1
        self.length=self.sheetData.length


    def __init__(self,frames,startingFrame,frameRate,shouldLoop) -> None:
        pass
        



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
    cdef public object currentImage
    




    def __cinit__(self, list animationDataList, int startingAnimation=0):
        self.currentAnimIndex=startingAnimation
        self.animations=animationDataList
        self.animationsLen=len(self.animations)
        self.currentAnimation=self.animations[startingAnimation]
        self.frame=self.currentAnimation.startingFrame
        #the last frame index, used for detecting if the cache needs an update
        self.lastFrame=self.frame
        #leaf cache
        self.currentImage=self.currentAnimation.sheetData.frameList[self.frame]
        self.currentFrameSize=self.currentAnimation.sheetData.imageSizeList[self.frame]
        #the left over time between frame durations 
        self.frameTimeCarry=0
        self.correctedFrameTime=0
        #cast start value to bint
        self.unpaused=0
        #intermediate variables cached for speed
        self.passedFrames=0
        self.prospectiveFrame=0
        self.frameTime=0
        
    cpdef void swapAnimation(self,int newAnimationIndex):
        #set the new index
        self.currentAnimIndex=newAnimationIndex
        #load the new animation
        self.currentAnimation=self.animations[self.currentAnimIndex]
        #init the starting frame
        self.frame=self.currentAnimation.startingFrame
        #clear the last frame
        self.lastFrame=self.frame
        #clear the leaf cache
        self.currentImage=self.currentAnimation.sheetData.frameList[self.frame]
        self.currentFrameSize=self.currentAnimation.sheetData.imageSizeList[self.frame]

        


        #clear the frame time carry value
        self.frameTimeCarry=0
        #pause the animation state
        self.unpaused=0
    
        
    cpdef void frameUpdate(self, float frameTime):
        cdef Animation anim
        if (self.unpaused):
            # Cache the current animation in a local C variable
            anim = self.currentAnimation

            # Reuse the preallocated class attributes
            self.frameTime = frameTime
            self.correctedFrameTime = (self.frameTime + self.frameTimeCarry)

            if((anim.frameRate > 0) and ((self.frame < anim.lengthMinusOne) or (anim.looping))):
                #calculate how many animation frames have passed
                self.passedFrames = <int>(self.correctedFrameTime // anim.frameRateDelay)
                #calculate the left over time to carry
                self.frameTimeCarry = (self.correctedFrameTime % anim.frameRateDelay)
                #calculate the frame index we want to go to
                self.prospectiveFrame = (self.frame + self.passedFrames)
                #if that is a real frame and not the last one
                if(self.prospectiveFrame < anim.length):
                    #jump to it
                    self.frame = self.prospectiveFrame
                    if(self.lastFrame!=self.frame):
                        #update the frame
                        self.lastFrame=self.frame
                        #update the leaf cache
                        self.currentImage=self.currentAnimation.sheetData.frameList[self.frame]
                        self.currentFrameSize=self.currentAnimation.sheetData.imageSizeList[self.frame]
                elif(anim.looping):
                    self.frame = (self.prospectiveFrame % anim.length)
                    if(self.lastFrame!=self.frame):
                        #update the frame
                        self.lastFrame=self.frame
                        #update the leaf cache
                        self.currentImage=self.currentAnimation.sheetData.frameList[self.frame]
                        self.currentFrameSize=self.currentAnimation.sheetData.imageSizeList[self.frame] 
                else:
                    self.frame = anim.lengthMinusOne
                    if(self.lastFrame!=self.frame):
                        #update the frame
                        self.lastFrame=self.frame
                        #update the leaf cache
                        self.currentImage=self.currentAnimation.sheetData.frameList[self.frame]
                        self.currentFrameSize=self.currentAnimation.sheetData.imageSizeList[self.frame]
    

    cpdef pause(self):
        self.unpaused=0

    cpdef play(self):
        self.unpaused=1

    cpdef setFrame(self,int frame):
        if((frame<0)or(frame>self.currentAnimation.lengthMinusOne)):
            raise ValueError("frameset error: given frame index is out of bounds\nvalue must be between 0 and "+str(self.currentAnimation.length)+" given value: "+str(frame))
        self.frame=frame
        self.frameTimeCarry=0
        self.lastFrame=frame

        self.currentImage=self.currentAnimation.sheetData.frameList[self.frame]
        self.currentFrameSize=self.currentAnimation.sheetData.imageSizeList[self.frame]

    cpdef resetAnimation(self):
        self.setFrame(self.currentAnimation.startingFrame)
        


        
            
            




cdef class SpriteCore:
    #core variables of sprites
    cdef public int x
    cdef public int y
    cdef public int width
    cdef public int height
    cdef public int imageOffsetX
    cdef public int imageOffsetY
    cdef public bint visible
    cdef public AnimationControllerCore animationController

    

    def __cinit__(self,int x,int y,int width,int height,bint visible, AnimationControllerCore animationController,int imageOffsetX=0,int imageOffsetY=0):
        self.x=x
        self.y=y
        self.width=width
        self.height=height
        self.imageOffsetX=imageOffsetX
        self.imageOffsetY=imageOffsetY
        self.visible=visible
        self.animationController=animationController

        #init tile data



    cpdef show(self):
        self.visible=1

    cpdef hide(self):
        self.visible=0

    cpdef setPos(self,x,y):
        self.x=x
        self.y=y

    cpdef move(self,x,y):
        self.x+=x
        self.y+=y

    cpdef setTextureOffset(self,x,y):
        self.imageOffsetX=x
        self.imageOffsetY=y

     
#need to make a subclass of the above for the tile sprite
cdef class TileSpriteCore(SpriteCore):
    #only used by tile sprites
    cdef public int tileSize
    cdef public int tileX
    cdef public int tileY
    cdef public int tileOffsetX
    cdef public int tileOffsetY

    def __cinit__(self, int tileX, int tileY, int width, int height, int tileSize, bint visible, AnimationControllerCore animationController, int imageOffsetX=0, int imageOffsetY=0,tileOffsetX:int=0,tileOffsetY:int=0):
        #init new vals
        self.tileSize=tileSize
        self.tileX=tileX
        self.tileY=tileY
        self.tileOffsetX=tileOffsetX
        self.imageOffsetY=tileOffsetY
        #init existing vals
        self.visible=visible
        self.width=width
        self.height=height
        
        self.animationController=animationController
        self.imageOffsetX=imageOffsetX
        self.imageOffsetY=imageOffsetY





#this one spiraled out of control
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

    

    def __cinit__(self,int fps):
        cdef int STARTSIZE=5000
        self.displayList=[[None,[0,0].copy()] for i in range(STARTSIZE)]
        self.fps=fps * 15
        self.frameCounter=0
        self.averageSize=0
        
        self.averagingNumbersBackend=np.zeros(self.fps, dtype=np.int32)
        self.append = self.displayList.append





    
    cpdef list generateDisplayList(self, list internalLayersReference, Camera cameraReference):
        #cache the camera positions
        cdef Camera camera=cameraReference
        cdef int cameraLeft=camera.x
        cdef int cameraRight=camera.x+camera.width
        cdef int cameraTop=camera.y
        cdef int cameraBottom=camera.y+camera.height

        #cache the reference to internalLayers
        cdef list internalLayers=internalLayersReference
        
        #hoop jumping to use memory views because cython is picky
        cdef int[:] averagingNumbersWindow = self.averagingNumbersBackend

        #this check runs roughly every 15 seconds and is designed to take a memory allocation hit 
        #to free shadow allocated memory if the predicted shadow allocation exceeds the current average usage
        #by double or more
        if(self.frameCounter>self.fps):
            #reset the counter and average
            self.frameCounter=0
            self.lastAverage=self.averageSize

            #use numpy to add all the entries
            self.averageSize=np.sum(self.averagingNumbersBackend)

            #then divide by how many there were to get the average
            self.averageSize = self.averageSize//self.averagingNumbersBackend.size

            if(self.lastAverage>=(self.averageSize*2)):
                #allocate a new display list to reset the buffer
                self.displayList=[[None,[0,0].copy()] for i in range(self.averageSize)]

                #reset the prefetched functions to the new list
                self.append = self.displayList.append


        #create some variables for objects
        cdef set layerRef
        cdef SpriteCore SpriteData
        cdef AnimationControllerCore animationController
        cdef ImageSize frameSize

        #variables for the four corners and coords
        cdef int spriteLeft
        cdef int spriteRight
        cdef int spriteTop
        cdef int spriteBottom
        cdef int spriteX
        cdef int spriteY

        #cache the length of the current display list
        cdef int displayListLen=len(self.displayList)
        #stores the current display list entry we are editing and its coords
        cdef list entry
        cdef list entryCoords

        #counter for statistics purposes and the anti allocation algorithm
        cdef int spriteCount=0
        #the main nested loops
        for layer in internalLayersReference:
            layerRef=layer
            for sprite in layerRef:
                SpriteData=sprite.animationController
                #early visibility check optimisation
                if(SpriteData.visible):
                    #load the sprite's position and image data
                    animationController=SpriteData.animationController
                    frameSize=animationController.currentFrameSize
                    spriteX=SpriteData.x+SpriteData.imageOffsetX
                    spriteY=SpriteData.y+SpriteData.imageOffsetY
                    spriteLeft=spriteX
                    spriteRight=spriteLeft+frameSize.width
                    spriteTop=spriteY
                    spriteBottom=spriteTop+frameSize.height
                    
                    #viewport culling check
                    if((spriteRight >= cameraLeft)and(spriteLeft <= cameraRight)and
                        (spriteTop <= cameraBottom)and(spriteBottom  >= cameraTop)):
                        #if we have some saved draw commands we can overwrite
                        if(spriteCount<displayListLen):
                            entry=self.displayList[spriteCount]
                            entryCoords=entry[1]
                            entry[0]=animationController.currentImage
                            entryCoords[0]=spriteX - cameraLeft
                            entryCoords[1]=spriteY - cameraTop
                        else:
                            ##otherwise allocate some new ones
                            self.append([animationController.currentImage, [spriteX - cameraLeft, spriteY - cameraTop]])
                        spriteCount+=1
        #if we have any leftover space
        if(spriteCount<displayListLen):
            #delete it
            del self.displayList[spriteCount:]
        #store the final sprite count
        averagingNumbersWindow[self.frameCounter]=max(0,spriteCount-1)
        #increment the shadow memory usage check timer
        self.frameCounter+=1
        return self.displayList
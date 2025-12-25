import pygame
cdef class FastRect:
    cdef public long x
    cdef public long y
    cdef public long width
    cdef public long height

    def __cinit__(self,x,y,width,height):
        self.x=x
        self.y=y
        self.width=width
        self.height=height

    cpdef getPygameEquivalent(self):
        return (self.x,self.y,self.width,self.height)

    def __init__(self,x=0,y=0,width=0,height=0) -> None:
        pass


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
    cdef public list[ImageSize] imageSizeList    # list of IntPair objects
    cdef public list[pygame.Surface] frameList        # list of Surfaces or frames

    def __cinit__(self,animationFrames:list[pygame.Surface]):
        #the lists for the data for every frame
        self.imageSizeList:list[ImageSize]=[]
        self.frameList:list[pygame.Surface]=[]
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
        self.sheetData:AnimationFrames=frames
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
    cdef public pygame.Surface currentImage
    

    def __cinit__(self, list animationDataList, int startingAnimation=0):
        self.currentAnimIndex=startingAnimation
        self.animations=animationDataList
        self.animationsLen=len(self.animations)
        self.currentAnimation:Animation=self.animations[startingAnimation]
        self.frame:int=self.currentAnimation.startingFrame
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
        self.currentAnimation:Animation=self.animations[self.currentAnimIndex]
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
    cdef public long x
    cdef public long y
    cdef public int width
    cdef public int height
    cdef public int imageOffsetX
    cdef public int imageOffsetY
    cdef public bint visible
    cdef public AnimationControllerCore animationController

    

    def __cinit__(self,long x,long y,long width,int height,bint visible, AnimationControllerCore animationController,int imageOffsetX=0,int imageOffsetY=0):
        self.x=x
        self.y=y
        self.width=width
        self.height=height
        self.imageOffsetX=imageOffsetX
        self.imageOffsetY=imageOffsetY
        self.visible=visible
        self.animationController=animationController

        



    cpdef show(self):
        self.visible=1

    cpdef hide(self):
        self.visible=0

    cpdef setPos(self,long x,long y):
        self.x=x
        self.y=y

    cpdef move(self,long x,long y):
        self.x+=x
        self.y+=y

    cpdef setTextureOffset(self,x,y):
        self.imageOffsetX=x
        self.imageOffsetY=y

     
#need to make a subclass of the above for the tile sprite
cdef class TileSpriteCore(SpriteCore):
    #only used by tile sprites
    cdef public int tileSize
    cdef public long tileX
    cdef public long tileY
    cdef public int tileOffsetX
    cdef public int tileOffsetY

    def __cinit__(self, long tileX, long tileY, int width, int height, int tileSize, bint visible, AnimationControllerCore animationController, int imageOffsetX=0, int imageOffsetY=0, int tileOffsetX=0,int tileOffsetY=0):
        #init new vals
        self.tileSize=tileSize
        self.tileX=tileX
        self.tileY=tileY
        self.tileOffsetX=tileOffsetX
        self.imageOffsetY=tileOffsetY
        #init existing vals
        SpriteCore.__cinit__(self,(self.tileX*self.tileSize)+self.tileOffsetX,(self.tileY*self.tileSize)+self.tileOffsetY,width,height,visible,animationController,imageOffsetX,imageOffsetY)

    cpdef move(self,long x,long y):
        #move to the new pos first
        self.x+=x
        self.y+=y

        #calculate our tile position for x
        self.tileX=self.x//self.tileSize
        #calculate our tile offset for x
        self.tileOffsetX=self.x%self.tileSize

        #calculate our tile position for y
        self.tileY=self.y//self.tileSize
        #calculate our tile offset for y
        self.tileOffsetY=self.y%self.tileSize

    cpdef setPos(self,long x,long y):
        #move to the new pos first
        self.x=x
        self.y=y

        #calculate our tile position for x
        self.tileX=self.x//self.tileSize
        #calculate our tile offset for x
        self.tileOffsetX=self.x%self.tileSize

        #calculate our tile position for y
        self.tileY=self.y//self.tileSize
        #calculate our tile offset for y
        self.tileOffsetY=self.y%self.tileSize


    cpdef tileMove(self, long x, long y):
        #adjust the tile position first
        self.tileX+=x
        self.tileY+=y
        #adjust the actual position
        self.x=(self.tileX*self.tileSize)+self.tileOffsetX
        self.y=(self.tileY*self.tileSize)+self.tileOffsetY

    cpdef setTilePos(self, long x, long y):
        #adjust the tile position first
        self.tileX=x
        self.tileY=y
        #adjust the actual position
        self.x=(self.tileX*self.tileSize)+self.tileOffsetX
        self.y=(self.tileY*self.tileSize)+self.tileOffsetY

    cpdef getTileOffset(self):
        return (self.tileOffsetX,self.tileOffsetY)

    cpdef setTileOffset(self, int x, int y):
        #adjust the values
        self.tileOffsetX=x
        self.tileOffsetY=y
        #adjust the actual position
        self.x=(self.tileX*self.tileSize)+self.tileOffsetX
        self.y=(self.tileY*self.tileSize)+self.tileOffsetY




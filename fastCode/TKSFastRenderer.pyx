import numpy as np
cimport numpy as np

import pygame
import pygame_gui
from fastCode.TKSFastSprites cimport SpriteCore,AnimationControllerCore,TileSpriteCore,ImageSize,AnimationFrames
import TKSSprites
import threading
import TKSExceptions

cdef class Camera:
    cdef public long x
    cdef public long y
    cdef public int width
    cdef public int height
    def __cinit__(self,long x,long y,int width,int height,str name) -> None:
        self.x=x
        self.y=y
        self.width=width
        self.height=height
        self.name=name
    
    def __init__(self,x=0,y=0,width=0,height=0) -> None:
        pass

    cpdef getPos(self):
        return (self.x, self.y)
    
    cpdef setPos(self,long x,long y):
        self.x=x
        self.y=y
    
    cpdef move(self,long x,long y):
        self.x+=x
        self.y+=y

    cdef setSize(self, int newWidth, int newHeight):
        self.width=newWidth
        self.height=newHeight



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
        cdef int DISPLAYLISTSTARTSIZE=5000
        self.displayList=[[None,[0,0].copy()] for i in range(DISPLAYLISTSTARTSIZE)]
        self.fps=fps * 15
        self.frameCounter=0
        self.averageSize=0
        
        self.averagingNumbersBackend=np.zeros(self.fps, dtype=np.int32)
        self.append = self.displayList.append





    
    cpdef list[list] generateDisplayList(self, list[list[SpriteCore]] internalLayersReference, Camera cameraReference):
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

            if(self.lastAverage>=(self.averageSize * 2)):
                #allocate a new display list to reset the buffer
                self.displayList=[[None,[0,0].copy()] for i in range(self.averageSize)]

                #reset the prefetched functions to the new list
                self.append = self.displayList.append


        #create some variables for objects
        cdef list layerRef
        cdef AnimationControllerCore animationController
        cdef ImageSize frameSize
        cdef SpriteCore sprite

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
                
                #early visibility check optimisation
                if(sprite.visible):
                    #load the sprite's position and image data
                    animationController=sprite.animationController
                    frameSize=animationController.currentFrameSize
                    spriteX=sprite.x+sprite.imageOffsetX
                    spriteY=sprite.y+sprite.imageOffsetY
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



cdef class SceneManager:
    cdef Camera currentCamera
    cdef list[list[TKSSprites.BasicSprite]] layers
    cdef list[list[SpriteCore]] internalLayers
    cdef list[dict[TKSSprites.BasicSprite, int]] indexLookupTables
    cdef list[Camera] cameras
    

    def __cinit__(self,int startingLayerCount,long startingCameraX, long startingCameraY, int startingCameraWidth,int StartingCameraHeight):
        #init the starting camera
        self.currentCamera=Camera(startingCameraX,startingCameraY,startingCameraWidth,StartingCameraHeight)#ignore the error, thats just the language server getting confused

        #init the cameraList
        self.cameras=[self.currentCamera]

        #init the two layers lists
        #these two hold the sprites, one the wrapper, and one the data core the render uses
        self.layers:list[list[TKSSprites.BasicSprite]]=[list() for layer in range(startingLayerCount)]
        self.internalLayers:list[list[SpriteCore]]=[list() for layer in range(startingLayerCount)]
        self.indexLookupTables:list[dict[TKSSprites.BasicSprite, int]]=[dict() for layer in range(startingLayerCount)]



    cpdef reset(self,int startingLayerCount,long startingCameraX, long startingCameraY, int internalWidth,int internalHeight):
        #init the starting camera
        self.currentCamera=Camera(startingCameraX,startingCameraY,internalWidth,internalHeight)#ignore the error, thats just the language server getting confused

        #init the cameraList
        self.cameras:list[Camera]=[self.currentCamera]

        #init the two layers lists
        #these two hold the sprites, one the wrapper, and one the data core the render uses
        self.layers:list[list[TKSSprites.BasicSprite]]=[list() for layer in range(startingLayerCount)]
        self.internalLayers:list[list[SpriteCore]]=[list() for layer in range(startingLayerCount)]
        self.indexLookupTables:list[dict[TKSSprites.BasicSprite, int]]=[dict() for layer in range(startingLayerCount)]


    cdef _getInternalLayers(self):
        return self.internalLayers
    
    cpdef int getLayerCount(self):
        return len(self.layers)

    cpdef insertLayer(self,int index):
        self.layers.insert(index,list())
        self.internalLayers.insert(index,list())
        self.indexLookupTables.insert(index,dict())

    cpdef addLayer(self):
        self.layers.append(list())
        self.internalLayers.append(list())
        self.indexLookupTables.append(dict())

    cpdef removeLayer(self,int index):
        self.layers.pop(index)
        self.internalLayers.pop(index)
        self.indexLookupTables.pop(index)

    #camera functions
    cpdef changeCamera(self,int index):
        self.currentCamera=self.cameras[index]

    cpdef Camera getCamera(self,int index):
        return self.cameras[index]

    cpdef Camera getCurrentCamera(self):
        return self.currentCamera

    cpdef removeCamera(self,int targetIndex):
        self.cameras.pop(targetIndex)

    cpdef addCamera(self,Camera newCamera):
        self.cameras.append(newCamera)

    cpdef insertCamera(self,Camera newCamera, int insertionIndex):
        self.cameras.insert(insertionIndex,newCamera)

    cpdef int findCamera(self,Camera cameraToFind):
        cdef int index
        for index in range(len(self.cameras)):
            if(self.cameras[index]==cameraToFind):
                return index
        return -1

    cpdef moveCurrentCamera(self, long x, long y):
        self.currentCamera.move(x,y)

    cpdef setCurrentCameraPos(self, long x, long y):
        self.currentCamera.setPos(x,y)

    cpdef addSprite(self,int layerIndex, TKSSprites.BasicSprite newSprite):
        self.layers[layerIndex].append(newSprite)
        self.internalLayers[layerIndex].append(<SpriteCore>newSprite.core)
        self.indexLookupTables[layerIndex][newSprite]=len(self.layers[layerIndex])-1

    cpdef addMultipleSprites(self,int layerIndex, list[TKSSprites.BasicSprite] newSpriteList):
        cdef TKSSprites.BasicSprite tempWrapper
        cdef SpriteCore tempCore
        cdef list[TKSSprites.BasicSprite] targetLayer
        cdef list[SpriteCore] targetInternalLayer
        cdef dict[TKSSprites.BasicSprite, int] targetLookupTable
        cdef int index
        #the layer in the layer lists we are targeting
        targetLayer=self.layers[layerIndex]
        targetInternalLayer=self.internalLayers[layerIndex]
        targetLookupTable=self.indexLookupTables[layerIndex]
        #loop through the sprites to add
        for index in range(len(newSpriteList)):
            #extract the sprite to add
            tempWrapper=newSpriteList[index]
            #extract its core
            tempCore=<SpriteCore>tempWrapper.core
            #add the wrapper to its list
            targetLayer.append(tempWrapper)
            #add the core to its list
            targetInternalLayer.append(tempCore)
            #save the index in the lookup table
            self.indexLookupTables[layerIndex][tempWrapper]=len(self.layers[layerIndex])-1



    cpdef swapLayersByIndex(self,int layerID1,int layerID2):
        #pretty simple and self explanitory, just swap some references
        #swap the wrappers
        cdef list[TKSSprites.BasicSprite] wrapperTemp
        wrapperTemp=self.layers[layerID1]
        self.layers[layerID1]=self.layers[layerID2]
        self.layers[layerID2]=wrapperTemp
        #swap the internal layers
        cdef list[SpriteCore] coreTemp
        coreTemp=self.internalLayers[layerID1]
        self.internalLayers[layerID1]=self.internalLayers[layerID2]
        self.internalLayers[layerID2]=coreTemp
        #swap the lookup tables
        cdef dict lookupTemp
        lookupTemp=self.indexLookupTables[layerID1]
        self.indexLookupTables[layerID1]=self.indexLookupTables[layerID2]
        self.indexLookupTables[layerID2]=lookupTemp


    cpdef swapLayers(self,list layer1, list layer2):
        cdef int layerID1
        cdef int layerID2
        layerID1=self.layers.index(layer1)
        layerID2=self.layers.index(layer2)
        #swap the wrappers
        cdef list[TKSSprites.BasicSprite] wrapperTemp
        wrapperTemp=self.layers[layerID1]
        self.layers[layerID1]=self.layers[layerID2]
        self.layers[layerID2]=wrapperTemp
        #swap the internal layers
        cdef list[SpriteCore] coreTemp
        coreTemp=self.internalLayers[layerID1]
        self.internalLayers[layerID1]=self.internalLayers[layerID2]
        self.internalLayers[layerID2]=coreTemp
        #swap the lookup tables
        cdef dict lookupTemp
        lookupTemp=self.indexLookupTables[layerID1]
        self.indexLookupTables[layerID1]=self.indexLookupTables[layerID2]
        self.indexLookupTables[layerID2]=lookupTemp

    

    cpdef deleteSprite(self,TKSSprites.BasicSprite sprite,int layer):
        #temporary object storage
        cdef TKSSprites.BasicSprite tempWrapper0
        cdef TKSSprites.BasicSprite tempWrapper1
        cdef SpriteCore tempCore0
        cdef SpriteCore tempCore1
        cdef int tempIndex0
        cdef int tempIndex1

        #the target lists and dicts
        cdef list targetLayer
        cdef list targetInternalLayer
        cdef dict targetLookupTable

        #if the sprite exists
        if(sprite in self.indexLookupTables[layer]):
            #grab the layers we are removing from
            targetLayer=self.layers[layer]
            targetInternalLayer=self.internalLayers[layer]
            targetLookupTable=self.indexLookupTables[layer]

            #grab the indexes for the swap trick
            #grab the index of the sprite to delete
            tempIndex0=targetLookupTable[sprite]
            #and the last index overall
            tempIndex1=len(self.layers[layer])-1
            #if the index isnt already the last one
            if(tempIndex0!=tempIndex1):
                #do a swap trick to prevent dict reconstruction
                #grab the target sprite wrapper
                tempWrapper0=targetLayer[tempIndex0]
                #grab the last sprite wrapper
                tempWrapper1=targetLayer[tempIndex1]
                #grab the target core
                tempCore0=targetInternalLayer[tempIndex0]
                #grab the last core
                tempCore1=targetInternalLayer[tempIndex1]

                #swap the lookup table indexes
                #targetLookupTable[sprite]=tempIndex1 NOTE: this line can be omitted because we are removing it anyway so it doesn't need an update
                targetLookupTable[tempWrapper1]=tempIndex0

                #swap the wrapper indexes
                targetLayer[tempIndex0]=tempWrapper1
                targetLayer[tempIndex1]=tempWrapper0

                #swap the core indexes
                targetInternalLayer[tempIndex0]=tempCore1 
                targetInternalLayer[tempIndex1]=tempCore0

            #remove the target indexes
            targetLayer.pop()
            targetInternalLayer.pop()
            #what we will remove will always be the target sprite
            targetLookupTable.pop(sprite)

            #i know this looks complicated but it prevents needing to rebuild the lookup table from scratch every time we do this

                
                

    #these are all pretty self explanatory
    cpdef deleteSprites(self,list[TKSSprites.BasicSprite] spriteList,int layer):
        cdef TKSSprites.BasicSprite sprite
        for sprite in spriteList:
            self.deleteSprite(sprite,layer)

    cpdef deleteSpriteFromAllLayers(self,TKSSprites.BasicSprite sprite):
        cdef int layer
        for layer in range(len(self.layers)):
            self.deleteSprite(sprite,layer)
 
    cpdef deleteSpritesFromAllLayers(self,list[TKSSprites.BasicSprite] spriteList):
        cdef int layer
        for layer in range(len(self.layers)):
            self.deleteSprites(spriteList,layer)

    cpdef clearAllLayers(self):
        cdef int index
        for index in range(len(self.layers)):
            self.layers[index].clear()
            self.internalLayers[index].clear()
            self.indexLookupTables[index].clear()

    cpdef clearLayer(self,int index):
        self.layers[index].clear()
        self.internalLayers[index].clear()
        self.indexLookupTables[index].clear()
        


#switched back to triple buffering because multithreaded double buffering was getting to be too much trouble
cdef class Renderer:
    #configuration settings
    cdef int internalWidth
    cdef int internalHeight
    cdef tuple clearColor
    cdef tuple backgroundColor
    cdef int targetFrameRate
    #the window
    cdef pygame.Surface screen
    #the scaling framebuffers
    cdef pygame.Surface letterBoxViewPort
    cdef pygame.Surface integerScaleBuffer
    #the framebuffer cache
    cdef pygame.Surface displayFrameBuffer
    #the framebuffer
    cdef pygame.Surface renderFrameBuffer
    #transfer slot buffer
    cdef pygame.Surface transferFrameBuffer
    #the framebuffer for the menus
    cdef pygame.Surface menuFrameBuffer

    #just used an an intermidate for buffer swapping
    cdef pygame.Surface framebufferSwapPointer

    #fancy scaling values
    cdef list[int] scaledDisplayRect
    cdef list[int] integerBufferSize
    cdef int scaledWidth
    cdef int scaledHeight
    cdef list[int] scaledSize
    cdef int scaledDisplayOffsetX
    cdef int scaledDisplayOffsetY
    cdef list[int] scaledDisplayOffset

    #the steps in which the smooth scaling will increase
    cdef int scaledStepSize
    #the flag to enable smooth scaling
    cdef bint shouldSmoothScale
    #the flag to determine if we should draw
    cdef bint shouldDraw
    cdef tuple oldSize
    cdef threading.Lock frameBufferSwapLock

    #just a flag to early exit if we arent started
    cdef bint started

    #the current scene manager object
    cdef SceneManager currentSceneManager
    #the current display list manager object
    cdef DisplayListManager currentDisplayListManager

    #temporary values for math
    cdef int intScalingValue
    cdef float floatScalingValue
    #storage for a value so i dont look it up every frame
    cdef int clearFlag

    #the trigger for rendering the next frame
    cdef threading.Event newFrameTrigger

    cdef list[int] scalingDataPacket

    def __cinit__(self):
        #init the variables of the object for safety
        self.started=<bint>False
        #set the internal display resolution
        self.internalWidth=0
        self.internalHeight=0
        #init the surface pointers to null for safety
        self.screen=NULL
        self.letterBoxViewPort=NULL
        self.integerScaleBuffer=NULL
        self.displayFrameBuffer=NULL
        self.renderFrameBuffer=NULL
        self.transferFrameBuffer=NULL
        self.menuFrameBuffer=NULL
        self.framebufferSwapPointer=NULL
        #set the color to clear the display, and the background/letterbox color
        self.clearColor=NULL
        self.backgroundColor=NULL
        self.targetFrameRate=0

        #init the values used for smooth scaling
        self.scaledDisplayRect=[0,0,self.internalWidth,self.internalHeight]
        self.integerBufferSize=[self.internalWidth,self.internalHeight]
        self.scaledWidth=0
        self.scaledHeight=0
        self.scaledDisplayOffsetX=0
        self.scaledDisplayOffsetY=0
        self.intScalingValue=0
        self.floatScalingValue=0
        self.scaledDisplayOffset=NULL
        self.scaledSize=NULL
        self.scalingDataPacket=NULL
        
        #the size of the steps that the window will scale by
        self.scaleStepSize=20
        #enables or disables smooth scaling if needed or not as determined by the scaling algorithm
        self.shouldSmoothScale=<bint>False

        #variables for controlling what gets rendered and when
        self.shouldDraw=<bint>True
        self.oldSize=(0,0)
        self.frameBufferSwapLock:threading.Lock=threading.Lock()
        self.newFrameTrigger:threading.Event=threading.Event()

        #the main sub modules of the renderer
        self.currentDisplayListManager=NULL
        self.currentSceneManager=NULL
        self.newFrameTrigger=NULL

    cpdef start(self,int internalDisplayWidth, int internalDisplayHeight, tuple clearColor, tuple backgroundColor, int scaleStepSize,int targetFrameRate,int startingLayerCount,long startingCameraX=0, long startingCameraY=0):
        #make sure the display is inactive
        if(pygame.display.get_active()):
            pygame.display.quit()

        #set the internal display resolution
        self.internalWidth=internalDisplayWidth
        self.internalHeight=internalDisplayHeight
        #set the important colors
        self.clearColor=clearColor
        self.backgroundColor=backgroundColor
        #set the config values
        self.scaledStepSize=scaleStepSize
        self.targetFrameRate=targetFrameRate

        self.scaledSize=[0,0]
        self.scaledDisplayOffset=[0,0]
        self.scalingDataPacket=[0,0,0,0]
        self.screen=pygame.display.set_mode(size=(self.internalWidth, self.internalHeight),vsync=1, flags=pygame.DOUBLEBUF|pygame.RESIZABLE)
        self.integerScaleBuffer=pygame.Surface((self.internalWidth,self.internalHeight))
        self.displayFrameBuffer=pygame.Surface((self.internalWidth,self.internalHeight))
        self.renderFrameBuffer=pygame.Surface((self.internalWidth,self.internalHeight))
        self.framebufferSwapPointer=NULL

        #release the lock if it is held
        if(self.frameBufferSwapLock.locked()):
            self.frameBufferSwapLock.release()

        self.newFrameTrigger:threading.Event=threading.Event()
        
        #init the main sub modules
        self.currentSceneManager:SceneManager=SceneManager(startingLayerCount,startingCameraX,startingCameraY,self.internalWidth,self.internalHeight)#ignore these errors, its just the langauge server getting confused by cython
        self.currentDisplayListManager:DisplayListManager=DisplayListManager(targetFrameRate)

        #raise the initialized flag
        self.started=<bint> True

    cpdef reset(self):
        if(self.started):
            self.start(self.internalWidth,self.internalHeight,self.clearColor,self.backgroundColor,self.scaledStepSize,self.targetFrameRate,self.currentSceneManager.getLayerCount())
            #reset these to default
            self.scaledDisplayRect=[0,0,self.internalWidth,self.internalHeight]
            self.integerBufferSize=[self.internalWidth,self.internalHeight]
            
            
            self.shouldSmoothScale=<bint>False
            self.shouldDraw=<bint>True
            self.oldSize=(0,0)
            self.scaledDisplayOffsetX=0
            self.scaledDisplayOffsetY=0
            self.intScalingValue=0
            self.floatScalingValue=0
            self.scaledWidth=0
            self.scaledHeight=0

    cpdef SceneManager getCurrentSceneManager(self):
        if(self.started):
            return self.currentSceneManager
        else:
            raise TKSExceptions.RendererNotStartedError("Error: cannot get scene manager before scene manager is created. renderer must be started first.")

    
    cpdef _calculateScaling(self,tuple screenSize):
        #calculate the new integer scaling value, making sure it isnt below 1
        intScalingValue=max(1,min((screenSize[0]//self.internalWidth),(screenSize[1]//self.internalHeight)))
        #calculate the new float scale value, making sure it isn't below 1, and adjust it for steps
        floatScalingValue=round(max(1,min((screenSize[0]/self.internalWidth),(screenSize[1]/self.internalHeight)))/self.scaleStepSize) * self.scaleStepSize

        #turn off smooth scaling if unnecessary
        if((floatScalingValue-intScalingValue)>(self.scaleStepSize//100)):
            self.shouldSmoothScale=<bint>True
        else:
            self.shouldSmoothScale=<bint>False

        #update the intermediate scaled size value
        self.scaledWidth=<int> (self.internalWidth * floatScalingValue)
        self.scaledHeight=<int> (self.internalHeight * floatScalingValue)
        #update the intermediate offset values
        self.scaledDisplayOffsetX=((self.oldSize[0]-self.scaledWidth)//2)
        self.scaledDisplayOffsetY=((self.oldSize[1]-self.scaledHeight)//2)
        #update the letterbox viewport rect
        #adust the width
        self.scaledDisplayRect[2]=self.scaledWidth
        #adjust the height
        self.scaledDisplayRect[3]=self.scaledHeight
        #adjust the x offset
        self.scaledDisplayRect[0]=self.scaledDisplayOffsetX
        #adjust the y offset
        self.scaledDisplayRect[1]=self.scaledDisplayOffsetY
        #handle integer scaling
        self.integerBufferSize[0]=self.internalWidth * intScalingValue
        self.integerBufferSize[1]=self.internalHeight * intScalingValue
        #update the pseudo tuples used by the engine for scaling and offsetting the viewport
        self.scaledDisplayOffset[0]=self.scaledDisplayOffsetX
        self.scaledDisplayOffset[1]=self.scaledDisplayOffsetY
        self.scaledSize[0]=self.scaledWidth
        self.scaledSize[1]=self.scaledHeight
        #get a new renderer subsurface for that viewport, leaving the rest as letterbox
        self.letterboxViewPort=self.displayFrameBuffer.subsurface(self.scaledDisplayRect)

    cpdef list[int] getWindowData(self):
        self.scalingDataPacket[0]=self.scaledWidth
        self.scalingDataPacket[1]=self.scaledHeight
        self.scalingDataPacket[2]=self.scaledDisplayOffsetX
        self.scalingDataPacket[3]=self.scaledDisplayOffsetY



    cpdef frameTick(self):
        #get the current window size
        screenSize=self.screen.get_size()

        #if the screensize has changed
        if((self.oldSize!=screenSize)):
            #clear the new frame trigger if it has been set
            self.newFrameTrigger.clear()
            if((screenSize[0]!=0)and(screenSize[1]!=0)):
                #adjust the screen scaling
                self._calculateScaling(screenSize)
                #set the should draw flag so we update the screen with the new size
                self.shouldDraw=<bint>True

        #otherwise check if there are any new frames to draw and set the flag if so
        elif(self.newFrameTrigger.is_set()):
            #clear the trigger
            self.newFrameTrigger.clear()
            self.shouldDraw=<bint>True

        #if there is a reason to draw a new frame
        if(self.shouldDraw):
            #cache the current screensize for size checking
            self.oldSize=screenSize
            #clear the screen
            self.screen.fill(self.backgroundColor)
            
            
            #acquire the framebuffer access lock
            with self.frameBufferSwapLock:
                #swap the buffers
                self.framebufferSwapPointer=self.displayFrameBuffer
                self.displayFrameBuffer=self.transferFrameBuffer
                self.transferFrameBuffer=self.framebufferSwapPointer
                self.framebufferSwapPointer=NULL
            
            pygame.transform.scale(self.displayFrameBuffer,self.integerBufferSize,self.integerScaleBuffer)
            
            
            #depending on if smooth scaling is turned on:
            if(self.shouldSmoothScale):
                #smooth scale to the screen
                pygame.transform.smoothscale(self.integerScaleBuffer,self.scaledSize,self.letterboxViewPort)
            else:
                #blit to the screen
                self.letterboxViewPort.blit(self.integerScaleBuffer,self.scaledDisplayOffset)
            #flip the display
            pygame.display.flip()
            #reset the should draw flag
            self.shouldDraw=False


    def render(self):
        #hyperoptimized render code
        #use a cython version of the above to increase speed
        displayList:list=self.currentDisplayListManager.generateDisplayList(self.currentSceneManager._getInternalLayers(),self.currentSceneManager.getCurrentCamera())
        self.renderFrameBuffer.fill(self.clearColor,special_flags=self.clearFlag)
        self.renderFrameBuffer.blits(displayList)
        #put render menu code here
        with self.frameBufferSwapLock:
            self.framebufferSwapPointer=self.transferFrameBuffer
            self.transferFrameBuffer=self.renderFrameBuffer
            self.renderFrameBuffer=self.framebufferSwapPointer
            self.framebufferSwapPointer=NULL
        self.newFrameTrigger.set()

        



    






        


        






    
                
        


    

    


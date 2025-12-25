import numpy as np
cimport numpy as np

import pygame
import pygame_gui
from fastFunctions.TKSFastSprites cimport SpriteCore,AnimationControllerCore,TileSpriteCore,ImageSize,AnimationFrames


cdef class Camera:
    cdef public int x
    cdef public int y
    cdef public int width
    cdef public int height
    cdef public str name
    def __cinit__(self,x,y,width,height,name) -> None:
        self.x=x
        self.y=y
        self.width=width
        self.height=height
        self.name=name
    
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


#need to create the fast renderer class and scene manager class and possibly window manager class


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
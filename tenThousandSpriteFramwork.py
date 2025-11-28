
#start of full framework rewrite
import threading
import pygame
import pygame_gui
from fastFunctions.TKSFastFunctions import fastDisplayListGeneratorLoop
import math
import TKSWorkerThreads
#TKS engine


#need to rewrite to use pygame

#arcitecture: render object with layers via sprite groups, core engine, menu objects via pygame gui, generator object for genration code, event handler object



        
class EventHandler:
    def __init__(self) -> None:
        pass

    def scanEvent(self, event:pygame.Event):
        pass

class GameLogic:
    def __init__(self) -> None:
        pass
        
    def frameTick(self) -> None:
        pass

    def unlockedTick(self) ->None:
        pass

    def start(self) -> None:
        pass



def getImageSize(image:pygame.Surface):
    imageRect=image.get_rect()
    return (imageRect.width,imageRect.height)


class BasicSprite(pygame.sprite.Sprite):
    def __init__(self,x:int,y:int,width:int,height:int,image:pygame.Surface) -> None:
        super().__init__()
        #init texture
        self.image:pygame.Surface=image
        #init rects
        self.rect:pygame.Rect=pygame.Rect(x,y,width,height)
        self.imageRect:pygame.Rect=self.image.get_rect()
        #init visibility
        self.visible=True
        #init image pos
        self.imageRect.x=self.rect.x
        self.imageRect.y=self.rect.y
        #init image offset
        self.imageOffsetX=0
        self.imageOffsetY=0
        


    def hide(self):
        self.visible=False



    def show(self):
        self.visible=True
 

    def changeTexture(self, newTexture:pygame.Surface):
        self.image=newTexture
        self.imageRect=self.image.get_rect()
        self.imageRect.x=self.rect.x+self.imageOffsetX
        self.imageRect.y=self.rect.y+self.imageOffsetY

    def setPos(self,x,y):
        self.rect.x=x
        self.rect.y=y
        self.imageRect.x=self.rect.x+self.imageOffsetX
        self.imageRect.y=self.rect.y+self.imageOffsetY


    def move(self,x,y):
       self.rect.x+=x
       self.rect.y+=y
       self.imageRect.x=self.rect.x+self.imageOffsetX
       self.imageRect.y=self.rect.y+self.imageOffsetY

    def setTextureOffset(self,x,y):
        self.imageOffsetX=x
        self.imageOffsetY=y
        self.imageRect.x=self.rect.x+self.imageOffsetX
        self.imageRect.y=self.rect.y+self.imageOffsetY


    








class Camera:
    def __init__(self,x,y,width,height) -> None:
        self.viewRect=pygame.Rect(x,y,width,height)

    def getPos(self):
        return (self.viewRect.x, self.viewRect.y)
    
    def setPos(self,x,y):
        self.viewRect.x=x
        self.viewRect.y=y
    
    def move(self,x,y):
        self.viewRect.x+=x
        self.viewRect.y+=y

    def getRect(self):#lol
        return self.viewRect







class Renderer:
    def __init__(self,displayWidth:int, displayHeight:int, clearColor:tuple,layers:int, targetFrameRate:int) -> None:
        #config stuff
        self.internalWidth=displayWidth
        self.internalHeight=displayHeight
        self.clearColor=clearColor
        self.targetFrameRate:int=targetFrameRate
        #our three main surfaces, dont mind them, they are just here for the backend
        self.screen:pygame.Surface=None
        self.letterboxViewPort:pygame.Surface=None
        self.displayFrameBuffer:pygame.Surface=None
        self.renderFrameBuffer:pygame.Surface=None
        #our numbers used for fancy scaling
        self.scaledDisplayRect=pygame.Rect(0,0,self.internalWidth,self.internalHeight)
        #swapper and its events
        self.frameBufferSwapper:TKSWorkerThreads.frameBufferSwapper=None
        self.bufferSwapTrigger:threading.Event=threading.Event()
        self.newFrameTrigger:threading.Event=threading.Event()
        self.swapFinishedSignal:threading.Event=threading.Event()
        self.goAroundSignal:threading.Event=threading.Event()
        #variables for controlling what gets rendered and when
        self.shouldDraw=True
        self.oldSize=(0,0)
        self.framebufferAccessLock:threading.Lock=threading.Lock()
        #sprite layer stuff, because everything is a sprite
        self.layerCount:int=layers
        self.layers:list[pygame.sprite.Group]=[pygame.sprite.Group() for l in range(layers)]
        #speed optimization i didnt want but must have
        self.internalLayers:list[set[BasicSprite]]=[set() for l in range(layers)]
        

        #camera feature
        self.currentCamera:Camera=Camera(0,0,self.internalWidth,self.internalHeight)

        #TODO: menu integration
        #placeholder for menu stuff
        #ui container class
        #ui layer surface.
        
    def _swapFrameBuffers(self)->None:
        temp=self.renderFrameBuffer
        self.renderFrameBuffer=self.displayFrameBuffer
        self.renderFrameBuffer=temp
    

    def frameTick(self) -> None:
        #get the current window size
        screenSize=self.screen.get_size()

        #if the screensize has changed
        if((self.lastSize!=screenSize)):
            #clear the new frame trigger if it has been set
            self.newFrameTrigger.clear()
            if((screenSize[0]!=0)and(screenSize[1]!=0)):
                #calculate the new letterbox
                scalingValue=min((self.lastSize[0]/self.internalWidth),(self.lastSize[1]/self.internalHeight))
                #update the letterbox viewport rect
                self.scaledDisplayRect.width=int(self.internalWidth*scalingValue)
                self.scaledDisplayRect.height=int(self.internalHeight*scalingValue)
                self.scaledDisplayRect.x=((self.lastSize[0]-self.scaledDisplayRect.width)//2)
                self.scaledDisplayRect.y=((self.lastSize[1]-self.scaledDisplayRect.height)//2)
                #get a new renderer subsurface for that viewport, leaving the rest as letterbox
                self.letterboxViewPort=self.displayFrameBuffer.subsurface(self.scaledDisplayRect)
                #set the should draw flag so we update the screen with the new size
                self.shouldDraw=True

        #otherwise check if there are any new frames to draw and set the flag if so
        elif(self.newFrameTrigger.is_set()):
            #clear the trigger
            self.newFrameTrigger.clear()
            self.shouldDraw=True
        #if there is a reason to draw a new frame
        if(self.shouldDraw):
            #cache the current screensize for size checking
            self.lastSize=screenSize
            #clear the screen
            self.screen.fill((0,0,0))
            #acquire the framebuffer access lock
            with self.framebufferAccessLock:
                pygame.transform.smoothscale(self.displayFrameBuffer,(self.scaledDisplayRect.width,self.scaledDisplayRect.height),self.letterboxViewPort)
            #flip the display
            pygame.display.flip()
            #reset the should draw flag
            self.shouldDraw=False


 

    def render(self) -> None:
        #hyperoptimized render code
        '''
        cameraRect=self.camera.getRect()#get rekt son!
        cameraLeft=cameraRect.left
        cameraRight=cameraRect.right
        cameraBottom=cameraRect.bottom
        cameraTop=cameraRect.top
        displayList=[
            (sprite.image, (sprite.rect.x-cameraRect.x, sprite.rect.y-cameraRect.y)) 
            for layer in self.internalLayers for sprite in layer 
            if(((sprite.rect.right>=cameraLeft) and (sprite.rect.left<=cameraRight)) and 
            ((sprite.rect.top<=cameraBottom) and (sprite.rect.bottom>=cameraTop)))
            ]
        '''
        #use a cython version of the above to increase speed
        displayList:list[tuple[pygame.Surface,tuple[int,int]]]=fastDisplayListGeneratorLoop(self.internalLayers,self.currentCamera.getRect())
        self.renderFrameBuffer.fill(self.clearColor,special_flags=pygame.SRCALPHA)
        self.renderFrameBuffer.blits(displayList)
        
        #put render menu code here

        #put new render system logic here



    def getCurrentCamera(self):
        return self.currentCamera
    
    


    def setCurrentCamera(self,camera:Camera):
        self.currentCamera=camera


    def moveCamera(self,x,y):
        self.currentCamera.move(x,y)


    def setCameraPos(self,x,y):
        self.currentCamera.setPos(x,y)


    
    def addSprite(self,sprite:BasicSprite,layer:int):
        #update both the sprite group representation and the set representation, plus the camera, so everything is seamless and doesn't break
        #because of how sprite groups work and my obsession with speed in an inherently slow language
        self.layers[layer].add(sprite)
        self.internalLayers[layer].add(sprite)
        

    def addSprites(self,sprites:list[BasicSprite],layer:int):
        #update both the sprite group representation and the set representation, plus the camera,
        #for all objects, so everything is seamless and doesn't break
        self.layers[layer].add(sprites)
        self.internalLayers[layer].update(sprites)






        
        

    def start(self) -> None:
        #make sure the display is inactive
        if(pygame.display.get_active()):
            pygame.display.quit()
        #init the display and framebuffer
        self.screen=pygame.display.set_mode(size=(self.internalWidth, self.internalHeight),vsync=1, flags=pygame.DOUBLEBUF|pygame.RESIZABLE|pygame.SCALED)
        self.stagingFrameBuffer=pygame.Surface((self.internalWidth,self.internalHeight))
        self.displayFrameBuffer=pygame.Surface((self.internalWidth,self.internalHeight))
        self.swapFrameBuffer=pygame.Surface((self.internalWidth,self.internalHeight))
        self.renderFrameBuffer=pygame.Surface((self.internalWidth,self.internalHeight))
        #init the control events
        self.bufferSwapTrigger.clear()
        self.newFrameTrigger.clear()
        self.swapFinishedSignal.clear()
        self.goAroundSignal.clear()
        if(self.frameBufferSwapper!=None):
            self.frameBufferSwapper.shutdown()
        #init the swap thread
        self.frameBufferSwapper=TKSWorkerThreads.frameBufferSwapper(self,self.framebufferAccessLock,self.bufferSwapTrigger,self.swapFinishedSignal,self.goAroundSignal,self.targetFrameRate,self.newFrameTrigger)
        #release the lock if it is held
        if(self.framebufferAccessLock.locked()):
            self.framebufferAccessLock.release()
        



    def deleteSprite(self,sprite:BasicSprite,layer:int):
        if(self.layers[layer].has(sprite)):
            self.layers[layer].remove(sprite)
            self.internalLayers[layer].remove(sprite)
    
    def deleteSprites(self,spriteList:list[BasicSprite],layer:int):
        for sprite in spriteList:
            if(self.layers[layer].has(sprite)):
                self.layers[layer].remove(sprite)
                self.internalLayers[layer].remove(sprite)

    def deleteSpriteFromAllLayers(self,sprite:BasicSprite):
        for layer in range(len(self.layers)):
            self.deleteSprite(sprite,layer)
 
    def deleteSpritesFromAllLayers(self,spriteList:list[BasicSprite]):
        for layer in range(len(self.layers)):
            self.deleteSprites(spriteList,layer)

    def clearAllLayers(self):
        for index,layer in enumerate(self.layers):
            layer.empty()
            self.internalLayers[index]=set()
        self.render()

    def clearLayer(self,index:int):
        self.layers[index].empty()
        self.internalLayers[index]=set()
        self.render()

        




class Core:
    def __init__(self,eventHandler:EventHandler,gameLogic:GameLogic,renderer:Renderer,targetFps:int) -> None:
        #pygame stuff
        pygame.init()
        self.clock:pygame.time.Clock=pygame.time.Clock()

        #custom objects to farm out key logic blocks
        self.eventHandler=eventHandler
        self.gameLogic=gameLogic
        self.renderer=renderer

        #config variables
        self.targetFps=targetFps

        #runtime variables
        self.running=False
        self.deltaTime:float=0
        
        
    


    def run(self):
        self.running=True
        self.renderer.start()
        self.gameLogic.start()
        
        while(self.running):
            for event in pygame.event.get():
                if(event.type==pygame.QUIT):
                    self.running=False
                    break
                self.eventHandler.scanEvent(event)
            
            self.gameLogic.frameTick()

            self.renderer.frameTick()

            self.deltaTime= self.clock.tick(self.targetFps) / 1000


        pygame.quit()
            









        



#a class for syncing two threads
#it is designed that the host will first signal that
#it is ready, and then the client will later read this
#then perform its task, then sync that it is done
#the object should then be reset by the host. to use 
#it, set host ready, then set client working, then 
#set client done. to reset, use the reset function after a cycle.
#THIS IS DESIGNED TO ONLY BE EVER USED BY TWO TASKS ONLY, NO MORE THAN THAT
class TwoTaskSyncer:
    def __init__(self) -> None:
        #just a variable for tracking state
        self.stage=0
        #also a lock for safety
        self.taskLock=threading.Lock()


    def setHostReady(self):
        with self.taskLock:
            if(self.stage==0):
                self.stage=1
                return True
            return False
            

    def setClientWorking(self):
        with self.taskLock:
            if(self.stage==1):
                self.stage=2
                return True
            return False



    def setClientDone(self):
        with self.taskLock:
            if(self.stage==2):
                self.stage=3
                return True
            return False
        

    def reset(self):
        with self.taskLock:
            if(self.stage>=3):
                self.stage=0
                return True
            return False


    def blockingIsHostReady(self):
        with self.taskLock:
            if(self.stage==1):
                return True
            return False
    
    def blockingIsClientDone(self):
        with self.taskLock:
            if(self.stage==3):
                return True
            return False
        
    
    def IsHostReady(self):
        if(self.taskLock.locked()):
            return False
        with self.taskLock:
            if(self.stage==1):
                return True
            return False
    
    def IsClientDone(self):
        if(self.taskLock.locked()):
            return False
        with self.taskLock:
            if(self.stage==3):
                return True
            return False
        
        





      


#start of full framework rewrite
import threading
import pygame
import pygame_gui
from fastFunctions.TKSFastFunctions import fastDisplayListGeneratorLoop
import math

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







#TODO: implement new scaling system based on windowed and full screen
class Renderer:
    def __init__(self,displayWidth:int, displayHeight:int, clearColor:tuple,layers:int) -> None:
        #config stuff
        self.internalWidth=displayWidth
        self.internalHeight=displayHeight
        self.clearColor=clearColor
        self.displayAspectMode=0
        self.framebufferAspectMode=0
        #our three main surfaces, dont mind them, they are just here for the backend
        self.screen:pygame.Surface=None
        self.stagingFrameBuffer:pygame.Surface=None
        self.displayFrameBuffer:pygame.Surface=None
        self.swapFrameBuffer:pygame.Surface=None
        self.renderFrameBuffer:pygame.Surface=None
        #our numbers used for fancy scaling
        self.scaledDisplaySize=(0,0)
        self.scaledDisplayOffset=(0,0)

        #our events and locks to synchronize rendering
        self.newFrame:bool=True
        self.swapLock:threading.Lock=threading.Lock()
        #variables for controlling what gets rendered and when
        self.shouldDraw=True
        self.oldSize=(0,0)
        

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
        
  

    def frameTick(self) -> None:
        screenSize=self.screen.get_size()
        if(self.newFrame):
            temp=self.displayFrameBuffer
            with self.swapLock:
                self.displayFrameBuffer=self.swapFrameBuffer
                self.swapFrameBuffer=temp
                self.newFrame=False
            self.shouldDraw=True
        elif((self.lastSize!=screenSize)):
            self.shouldDraw=True
            scalingValue=min((self.lastSize[0]/self.internalWidth),(self.lastSize[1]/self.internalHeight))
            self.scaledDisplaySize=(int(self.internalWidth*scalingValue),int(self.internalHeight*scalingValue))
            self.scaledDisplayOffset=(((self.lastSize[0]-self.scaledDisplaySize[0])//2),((self.lastSize[1]-self.scaledDisplaySize[1])//2))
        if(self.shouldDraw):
            self.lastSize=screenSize
            self.screen.fill((0,0,0))
            pygame.transform.smoothscale(self.displayFrameBuffer,self.scaledDisplaySize,self.stagingFrameBuffer)
            self.screen.blit(self.stagingFrameBuffer,self.scaledDisplayOffset)
            pygame.display.flip()
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
        temp=self.renderFrameBuffer
        with self.swapLock:
            self.renderFrameBuffer=self.swapFrameBuffer
            self.swapFrameBuffer=temp
            self.newFrame=True
        #put render menu code here



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
        
        





      

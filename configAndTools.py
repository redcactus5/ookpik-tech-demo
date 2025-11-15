
#start of full framework rewrite
import threading
import pygame
import pygame_gui


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



class Camera:
    def __init__(self,x,y,width,height) -> None:
        self.viewport=pygame.rect.Rect(x,y,width,height)

    def getPos(self):
        return (self.viewport.x, self.viewport.y)
    
    def setPos(self,x,y):
        self.viewport.x=x
        self.viewport.y=y
    
    def move(self,x,y):
        self.viewport.x+=x
        self.viewport.y+=y

    def getRect(self):#lol
        return self.viewport


    



class BasicSprite(pygame.sprite.Sprite):
    def __init__(self,x,y,image:pygame.surface.Surface) -> None:
        super().__init__()
        #init texture
        self.currentTexture:pygame.surface.Surface=image
        self.image:pygame.surface.Surface=self.currentTexture
        self.rect:pygame.rect.Rect=self.image.get_rect()
        #init pos and visibility
        self.visible=True
        self.x=x
        self.y=y
        #init image pos
        self.rect.x=self.x
        self.rect.y=self.y

    def hide(self):
        if(self.visible):
            self.visible=False
            self.image=pygame.surface.Surface((self.rect.width,self.rect.height))
            self.rect=self.image.get_rect()
            self.rect.x=self.x
            self.rect.y=self.y
            

    def show(self):
        if(not self.visible):
            self.visible=True
            self.image=self.currentTexture
            self.rect=self.image.get_rect()
            self.rect.x=self.x
            self.rect.y=self.y

    def changeTexture(self, newTexture:pygame.surface.Surface):
        self.currentTexture=newTexture
        self.image=newTexture
        self.rect=self.currentTexture.get_rect()
        self.rect.x=self.x
        self.rect.y=self.y

    def setPos(self,x,y):
        self.x=x
        self.y=y
        self.rect.x=self.x
        self.rect.y=self.y


    def move(self,x,y):
        self.x=(self.x+x)
        self.y=(self.y+y)
        self.rect.x=self.x
        self.rect.y=self.y





class Renderer:
    def __init__(self,displayWidth:int, displayHeight:int, clearColor:tuple,layers:int) -> None:
        #config stuff
        self.displayWidth=displayWidth
        self.displayHeight=displayHeight
        self.clearColor=clearColor
        #our two main surfaces, dont mind them, they are just here for the backend
        self.screen:pygame.Surface = pygame.Surface((0,0))
        self.frameBuffer:pygame.Surface = pygame.Surface((0,0))
        #flags for controlling what gets rendered and when
        self.frameChanged=True
        self.lastSize=(0,0)

        #sprite layer stuff, because everything is a sprite
        self.layerCount:int=layers
        self.layers:list[pygame.sprite.Group]=[pygame.sprite.Group() for l in range(layers)]
        
        

        #camera feature
        self.camera:Camera=Camera(0,0,self.displayWidth,self.displayHeight)

        #placeholder for menu stuff
        
  

    def frameTick(self) -> None:
        screenSize=self.screen.get_size()
        if(self.frameChanged or (self.lastSize!=screenSize)):
            self.lastSize=screenSize
            pygame.transform.smoothscale(self.frameBuffer,screenSize,self.screen)
            pygame.display.flip()
            self.frameChanged=False

 

    def render(self) -> None:
        #hyperoptimized render code
        displayList=[(sprite.image, (sprite.x - self.camera.viewport.x, sprite.y - self.camera.viewport.y)) for layer in self.layers for sprite in layer.sprites() if(sprite.rect.colliderect(self.camera.viewport))]
        self.frameBuffer.blits(displayList)
        self.frameChanged=True
        #put render menu code here

    def getCurrentCamera(self):
        return self.camera
    

    def setCurrentCamera(self,camera:Camera):
        self.camera=camera

    def moveCamera(self,x,y):
        self.camera.move(x,y)

    def setCameraPos(self,x,y):
        self.camera.setPos(x,y)


    def start(self) -> None:
        self.screen=pygame.display.set_mode(size=(self.displayWidth, self.displayHeight),vsync=1,flags=pygame.SCALED|pygame.RESIZABLE)
        self.frameBuffer=pygame.Surface((self.displayWidth,self.displayHeight))

        




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
        
        





      

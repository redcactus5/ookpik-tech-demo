'''
the 10,000 sprites engine
'''
thanksForTheMemories="we miss you Becky H."

import threading
import pygame
import pygame_gui
import TKSWorkerThreads
import TKSSprites
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



#TODO: implement vfx controller class, and add two slots for them in the render
#one slot for the game, one slot for the 

#TODO: implement ui manager and controller classes


#no fullscreen effects processor system implemented, may be done later if needed
#TODO: move to cython code
class Renderer:
    def __init__(self,displayWidth:int, displayHeight:int, clearColor:tuple, targetFrameRate:int) -> None:
        #config stuff
        self.internalWidth=displayWidth
        self.internalHeight=displayHeight
        self.clearColor=clearColor
        self.targetFrameRate:int=targetFrameRate
        #our three main surfaces, dont mind them, they are just here for the backend
        self.screen:pygame.Surface=None
        self.letterboxViewPort:pygame.Surface=None
        self.integerScaleBuffer:pygame.Surface=None
        self.displayFrameBuffer:pygame.Surface=None
        self.renderFrameBuffer:pygame.Surface=None
        #our numbers used for fancy scaling
        self.scaledDisplayRect=[0,0,self.internalWidth,self.internalHeight]
        self.integerBufferSize:list[int]=[self.internalWidth,self.internalHeight]
        self.scaledSize:list[int]=[0,0]
        self.scaledDisplayOffset=[0,0]
        self.scaleStepSize=10
        self.shouldSmoothScale:bool=False
        #swapper and its events
        self.frameBufferSwapper:TKSWorkerThreads.frameBufferSwapper=None
        self.bufferSwapTrigger:threading.Event=threading.Event()
        self.newFrameTrigger:threading.Event=threading.Event()
        self.notBusyDrawing:threading.Event=threading.Event()
        #variables for controlling what gets rendered and when
        self.shouldDraw=True
        self.oldSize=(0,0)
        self.framebufferAccessLock:threading.Lock=threading.Lock()
        #sprite layer stuff, because everything is a sprite

        #TODO: menu integration
        #placeholder for menu stuff
        #ui container class
        #ui layer surface.
        
    def _swapFrameBuffers(self)->None:
        temp=self.renderFrameBuffer
        self.renderFrameBuffer=self.displayFrameBuffer
        self.displayFrameBuffer=temp
    

    def _calculateScaling(self,screenSize:tuple[int,int]):
        #calculate the new integer scaling value, making sure it isnt below 1
        intScalingValue=max(1,min((screenSize[0]//self.internalWidth),(screenSize[1]//self.internalHeight)))
        #calculate the new float scale value, making sure it isn't below 1, and adjust it for 10% steps
        floatScalingValue=round(max(1,min((screenSize[0]/self.internalWidth),(screenSize[1]/self.internalHeight)))/self.scaleStepSize)*self.scaleStepSize
        #turn off smooth scaling if unnecessary
        if((floatScalingValue-intScalingValue)>(self.scaleStepSize//100)):
            self.shouldSmoothScale=True
        else:
            self.shouldSmoothScale=False

        #update the letterbox viewport rect
        self.scaledSize=(int(self.internalWidth*floatScalingValue),int(self.internalHeight*floatScalingValue))
        self.scaledDisplayRect.width=self.scaledSize[0]
        self.scaledDisplayRect.height=self.scaledSize[1]
        self.scaledDisplayOffset=(((self.lastSize[0]-self.scaledSize[0])//2),((self.lastSize[1]-self.scaledSize[1])//2))
        self.scaledDisplayRect.x=self.scaledDisplayOffset[0]
        self.scaledDisplayRect.y=self.scaledDisplayOffset[1]
        #get a new renderer subsurface for that viewport, leaving the rest as letterbox
        self.letterboxViewPort=self.displayFrameBuffer.subsurface(self.scaledDisplayRect)
        
        #handle integer scaling
        self.integerBufferSize=(self.internalWidth*intScalingValue,self.internalHeight*intScalingValue)




    def frameTick(self) -> None:
        #get the current window size
        screenSize=self.screen.get_size()

        #if the screensize has changed
        if((self.lastSize!=screenSize)):
            #clear the new frame trigger if it has been set
            self.newFrameTrigger.clear()
            if((screenSize[0]!=0)and(screenSize[1]!=0)):
                #adjust the screen scaling
                self._calculateScaling(screenSize)
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
            self.screen.fill(backgroundColor)
            #set the wait state flag so the go around system has a shred of a chance of working
            self.notBusyDrawing.clear()
            #acquire the framebuffer access lock
            with self.framebufferAccessLock:
                pygame.transform.scale(self.displayFrameBuffer,self.integerBufferSize,self.integerScaleBuffer)
            self.notBusyDrawing.set()
            
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


 

    def render(self) -> None:
        #hyperoptimized render code
        if(not self.bufferSwapTrigger.is_set()):
            #use a cython version of the above to increase speed
            displayList:list[list[pygame.Surface,list[int,int]]]=fastDisplayListGeneratorLoop(self.layers,self.currentCamera)
            self.renderFrameBuffer.fill(self.clearColor,special_flags=pygame.SRCALPHA)
            self.renderFrameBuffer.blits(displayList)
            

            #put render menu code here

            self.bufferSwapTrigger.set()



    def start(self) -> None:
        #make sure the display is inactive
        if(pygame.display.get_active()):
            pygame.display.quit()
        #init the display and framebuffer
        self.screen=pygame.display.set_mode(size=(self.internalWidth, self.internalHeight),vsync=1, flags=pygame.DOUBLEBUF|pygame.RESIZABLE|pygame.SCALED)
        self.integerScaleBuffer=pygame.Surface((self.internalWidth,self.internalHeight))
        self.displayFrameBuffer=pygame.Surface((self.internalWidth,self.internalHeight))
        self.renderFrameBuffer=pygame.Surface((self.internalWidth,self.internalHeight))
        #clear any old threads
        if(self.frameBufferSwapper!=None):
            self.frameBufferSwapper.shutdown()
        #init the control events
        self.bufferSwapTrigger.clear()
        self.newFrameTrigger.clear()
        #inverted because of how wait works
        self.notBusyDrawing.set()
        #init the swap thread
        self.frameBufferSwapper=TKSWorkerThreads.frameBufferSwapper(self,self.framebufferAccessLock,self.bufferSwapTrigger,self.targetFrameRate,self.newFrameTrigger,self.notBusyDrawing)
        #release the lock if it is held
        if(self.framebufferAccessLock.locked()):
            self.framebufferAccessLock.release()
        


        




class Core:
    def __init__(self,eventHandler:EventHandler,gameLogic:GameLogic,renderer:Renderer,targetFps:int) -> None:
        #pygame stuff
        pygame.init()
        self.clock:pygame.time.Clock=pygame.time.Clock()

        #custom objects to farm out key logic blocks
        self.eventHandler=eventHandler
        self.gameLogic=gameLogic
        self.renderer=renderer
        self.unlockedUpdater=TKSWorkerThreads.UnlockedTicker(self)


        #config variables
        self.targetFps=targetFps

        #runtime variables
        self.running=False
        self.deltaTime:float=0
        
        
        
    def unlockedTick(self):
        self.gameLogic.unlockedTick()


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
            self.unlockedUpdater.pause()
            self.unlockedUpdater.waitForUnblock()
            self.renderer.frameTick()
            self.unlockedUpdater.resume()

            self.deltaTime= self.clock.tick(self.targetFps) / 1000

        self.unlockedUpdater.shutdown()
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
        
        





      

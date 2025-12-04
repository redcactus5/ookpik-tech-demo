from TKS import Renderer
from TKS import Core
import threading
import time

class frameBufferSwapper(threading.Thread):
    def __init__(self,parentRenderer:Renderer,framebufferAccessLock:threading.Lock,swapTrigger:threading.Event,frameRate:int,newFrame:threading.Event,notBusySignal:threading.Event) -> None:
        super().__init__(daemon=True)
        #init the signals
        self.renderer:Renderer=parentRenderer
        self.swapTrigger:threading.Event=swapTrigger
        self.newFrameSignal:threading.Event=newFrame
        self.mainThreadNotBusy:threading.Event=notBusySignal
        #init the variables
        self.shutdownSignal:bool=False
        self.frameTime=(1/frameRate)
        self.running:bool=False
        self.swapLock:threading.Lock=framebufferAccessLock
        
    def run(self) -> None:
        self.running=True
        while self.running:
            #detect if the thread should die
            if(self.shutdownSignal):
                #break the circular reference
                self.renderer=None
                self.swapTrigger=None
                self.newFrameSignal=None
                self.mainThreadNotBusy=None
                self.swapLock=None
                #stop the loop
                self.running=False
                #bail
                break
            #if not wait for the swaptrigger
            elif(self.swapTrigger.wait()):
                self.swapTrigger.clear()
                #wait for the draw thread to not be busy
                if(self.mainThreadNotBusy.wait(self.frameTime)):
                    #swap the framebuffers
                    with self.swapLock:
                        self.renderer._swapFrameBuffers()
                    #alert that the swap has happened
                    self.newFrameSignal.set()



    def shutdown(self):
        self.shutdownSignal=True
        self.swapTrigger.set()
        self.join(1)

        
            

            


class UnlockedTicker(threading.Thread):
    def __init__(self,coreObject:Core):
        super().__init__(daemon=True)
        self.coreObject:Core=coreObject
        self.tickRate:int=60
        self.loopInterval:float=1/self.tickRate
        self.neededLoops:int=0
        self.intervalTime:float=0
        self.startTime:float=0
        self.endTime:float=0
        self.running:bool=False
        self.unpaused:threading.Event=threading.Event()


    def calculateLoops(self):
        self.intervalTime+=self.endTime-self.startTime
        self.neededLoops+=int(self.intervalTime//self.loopInterval)
        self.intervalTime-=self.loopInterval*self.neededLoops

    def run(self):
        self.running=True
        start2=0
        end2=0
        trueInterval=0
        while(self.running):
            self.unpaused.wait()
            self.endTime=time.perf_counter()
            self.calculateLoops()
            if(self.loopInterval>0):
                start2=time.perf_counter()
                self.startTime=time.perf_counter()
                for loop in range(self.neededLoops):
                    self.unpaused.wait()
                    self.neededLoops-=1
                    self.coreObject.unlockedTick()
                end2=time.perf_counter()
                trueInterval=self.loopInterval-(end2-start2)
            
                    
            if(trueInterval>0):
                time.sleep(trueInterval)


    def pause(self):
        self.unpaused.clear()

    def resume(self):
        self.unpaused.set()

    def shutdown(self):
        self.running=False
        self.coreObject=None
        self.join(1)



    

        

from TKS import Renderer
import threading


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

        
            

            



    

        

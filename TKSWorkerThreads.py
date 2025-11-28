from tenThousandSpriteFramwork import Renderer
import threading


class frameBufferSwapper(threading.Thread):
    def __init__(self,parentRenderer:Renderer,framebufferAccessLock:threading.Lock,swapTrigger:threading.Event,finishedSignal:threading.Event,goAroundSignal:threading.Event,frameRate:int,newFrame:threading.Event) -> None:
        super().__init__(daemon=True)
        #init the signals
        self.renderer:Renderer=parentRenderer
        self.swapTrigger:threading.Event=swapTrigger
        self.newFrameSignal:threading.Event=newFrame
        self.finishedSignal:threading.Event=finishedSignal
        self.goAroundSignal:threading.Event=goAroundSignal
        #init the variables
        self.shutdownSignal:bool=False
        self.frameTime=1/frameRate
        self.running:bool=False
        self.swapLock:threading.Lock=framebufferAccessLock
        
    def run(self) -> None:
        self.running=True
        while self.running:
            #detect if the thread should die
            if(self.shutdownSignal):
                #break the circular reference
                self.renderer=None
                #stop the loop
                self.running=False
                #bail
                break
            #if not wait for the swaptrigger
            elif(self.swapTrigger.wait(self.frameTime)):
                with self.swapLock:
                    self.renderer._swapFrameBuffers()
                self.newFrameSignal.set()
                self.finishedSignal.set()
            else:
                self.goAroundSignal.set()
                self.swapTrigger.clear()

    def shutdown(self):
        self.shutdownSignal=True
        self.join(1)

        
            

            



    

        

from TKSFastRenderer cimport Renderer
import threading
import weakref

cdef class FramebufferSwapThread:
    cdef Renderer Renderer

    cdef threading.Event swapTrigger
    cdef threading.Event newFrameSignal
    cdef threading.Event mainThreadNotBusy

    cdef bint shutdownSignal
    cdef float frameTime
    cdef bint running 
    cdef threading.Lock swapLock
    cdef threading.Thread backendThread


    def __cinit__(self, Renderer parentRenderer, threading.Lock frameBufferAccessLock, threading.Event swapTrigger, int frameRate, threading.Event newFrame, threading.Event notBusySignal):
        #the renderer with the buffers we are swapping
        self.renderer=weakref.ref(parentRenderer)
        #the control events
        self.swapTrigger=swapTrigger
        self.newFrameSignal=newFrame
        self.mainThreadNotBusy=notBusySignal
        #the flag that triggers a shutdown
        self.shutdownSignal=<bint>False
        #the expected frame time
        self.frameTime=(1/frameRate)
        #the flag that controls if the thread will continue running
        self.running=<bint>False
        #the lock used to prevent race conditions on swap
        self.swapLock=frameBufferAccessLock
        #start the core process
        self.backendThread=threading.Thread(target=self.run,daemon=True)

    cpdef None run(self):
        self.running=<bint>True
        while(self.running):
            #check if the thread should die
            if(self.shutdownSignal):
                #manually clear all references to destroy circular references and release events
                self.renderer=NULL
                self.swapTrigger=NULL
                self.newFrameSignal=NULL
                self.mainThreadNotBusy=NULL
                self.swapLock=NULL

                #stop the loop
                self.running=<bint>False

                #break out of the loop
                break

            elif(self.swapTrigger.wait()):
                self.swapTrigger.clear()
                







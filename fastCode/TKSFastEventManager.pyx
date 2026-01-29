import pygame
cimport TKSFastRenderer

cdef class MouseManager:
    cdef int internalWidth
    cdef int internalHeight
    cdef int windowWidth
    cdef int windowHeight
    cdef int viewportWidth
    cdef int viewportHeight
    cdef int viewportOffsetX
    cdef int viewportOffsetY
    cdef int lastMouseX
    cdef int lastMouseY
    cdef float floatScalingValue
    cdef int intScalingValue
    cdef tuple windowSize
    cdef __cinit__(self):
        self.internalWidth=0
        self.internalHeight=0
        self.windowWidth=0
        self.windowHeight=0
        self.viewportWidth=0
        self.viewportHeight=0
        self.viewportOffsetX=0
        self.viewportOffsetY=0
        self.lastMouseX=0
        self.lastMouseY=0
        self.windowSize=tuple()

    cdef updateWindowData(self, TKSFastRenderer.Renderer renderer):
        self.windowSize=pygame.display.get_window_size()
        self.windowWidth=<int>self.windowSize[0]
        self.windowHeight=<int>self.windowSize[1]
        self.internalWidth=<int>renderer.internalWidth
        self.internalHeight=<int>renderer.internalHeight
        self.viewportWidth=<int>renderer.scaledWidth
        self.viewportHeight=<int>renderer.scaledHeight
        self.viewportOffsetX=<int>renderer.scaledDisplayOffsetX
        self.viewportOffsetY=<int>renderer.scaledDisplayOffsetY
        
        


    cdef list[int] correctAbsoluteMousePosition(self,int mouseX, int mouseY):
        pass

    cpdef tuple[int] getMousePosition(self):
        pass

    cpdef tuple[int] getMouseRelativeMovement(self):
        pass



cdef class EventHander:
    cdef dict sortedEventLookup
    cdef list[list] sortedEvents
    cdef list lastEventCategories

    cdef __cinit__(self):
        #init the vars
        self.sortedEventLookup=dict()
        self.lastEventCategories=list()
        self.sortedEvents=[]

        

    cdef processEvents(self, list[pygame.Event] frameEvents):
        pass

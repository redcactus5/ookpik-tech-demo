import pygame
cimport TKSFastRenderer



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

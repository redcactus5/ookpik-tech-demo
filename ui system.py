
import threading
import collections
import queue
import threading
import time
import random
#might remove later

import configAndTools



#config constants
WINDOWPIXELWIDTH=1280
WINDOWPIXELHEIGHT=720
TILESIZE=16
TILEWIDTH=int(WINDOWPIXELWIDTH/TILESIZE)
TILEHEIGHT=int(WINDOWPIXELHEIGHT/TILESIZE)
TARGETFPS=60
TICKRATETARGET=120
TITLE="ookpik map generator demo beta"
LAYERCOUNT=6

IMAGES:dict={}

def initImages():
    global IMAGES
    #set up the terrain list
    
    
    







    















#use separate rendering and logic threads
#create ipc system and frameskip?
#separate menu system
#thread pause system?
#escape to pause?
#need menu system
#need on screen terminal system
#will use layered rendering system for now
#separate generator map from rendering map


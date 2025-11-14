
import threading
import collections
import queue
import threading
import time
import tkinter as tk
from PIL import Image
import random
#might remove later
from playsound3 import playsound

import configAndTools



#config constants
WINDOWPIXELWIDTH=1280
WINDOWPIXELHEIGHT=800
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
    terrain=[]
    terrain.append(Image.open("art/terrain/ground.png"))
    terrain.append(Image.open("art/terrain/snow.png"))
    IMAGES["terrain"]=terrain

    gameObjects=[]
    gameObjects.append(Image.open("art/gameObjects/berry.png"))
    gameObjects.append(Image.open("art/gameObjects/happy little tree.png"))
    gameObjects.append(Image.open("art/gameObjects/spotlight.png"))
    gameObjects.append(Image.open("art/gameObjects/flood.png"))
    IMAGES["gameObjects"]=gameObjects

    #set up the owl list
    owl=[]
    for i in range(4):
        owl.append(Image.open("art/ookpik/ookpik_"+str(i)+".png"))
    IMAGES["owl"]=owl

    

    #set up the logo text list
    
    IMAGES["logoText"]=Image.open("art/ui/logo.png")
    
    







    



app:configAndTools.Core=configAndTools.Core(TITLE,WINDOWPIXELWIDTH,WINDOWPIXELHEIGHT,TILEWIDTH,TILEHEIGHT,TILESIZE,TARGETFPS,TICKRATETARGET,LAYERCOUNT)
initImages()


for y in range(TILEHEIGHT):
    for x in range(TILEWIDTH):
        app.drawTile(IMAGES["terrain"][1],x,y,0)


#dont ask. just dont.
app.drawSprite(IMAGES["logoText"],int((WINDOWPIXELWIDTH/2)-(544/2)),48,4)

app.render()
app.updateTK()  
app.runTK()












#use separate rendering and logic threads
#create ipc system and frameskip?
#separate menu system
#thread pause system?
#escape to pause?
#need menu system
#need on screen terminal system
#will use layered rendering system for now
#separate generator map from rendering map


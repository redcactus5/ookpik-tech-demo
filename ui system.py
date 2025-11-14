
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
    terrain.append(Image.open("art/ground.png"))
    terrain.append(Image.open("art/happy little tree.png"))
    terrain.append(Image.open("art/flood.png"))
    terrain.append(Image.open("art/berry.png"))
    terrain.append(Image.open("art/spotlight.png"))
    IMAGES["terrain"]=terrain

    #set up the owl list
    owl=[]
    for i in range(4):
        owl.append(Image.open("art/ookpik/ookpik_"+str(i)+".png"))
    IMAGES["owl"]=owl

    #set up the border list
    border=[]
    for i in range(8):
        border.append(Image.open("art/border/border_"+str(i)+".png"))
    IMAGES["border"]=border



app:configAndTools.Core=configAndTools.Core(TITLE,WINDOWPIXELWIDTH,WINDOWPIXELHEIGHT,TILEWIDTH,TILEHEIGHT,TILESIZE,TARGETFPS,TICKRATETARGET,LAYERCOUNT)
initImages()
'''
for x in range(1,TILEWIDTH-1):
    app.drawTile(IMAGES["border"][0],x,0,2)
    app.drawTile(IMAGES["border"][0],x,TILEHEIGHT-1,2)

for y in range(1,TILEHEIGHT-1):
    app.drawTile(IMAGES["border"][1],0,y,2)
    app.drawTile(IMAGES["border"][1],TILEWIDTH-1,y,2)

app.drawTile(IMAGES["border"][5],0,0,2)
app.drawTile(IMAGES["border"][2],0,TILEHEIGHT-1,2)
app.drawTile(IMAGES["border"][3],TILEWIDTH-1,TILEHEIGHT-1,2)
app.drawTile(IMAGES["border"][4],TILEWIDTH-1,0,2)

'''



for y in range(TILEHEIGHT+1):
    for x in range(TILEWIDTH):
        app.drawTile(IMAGES["terrain"][0],x,y,0)
        if(random.randint(0,5)<4):
            app.drawTile(IMAGES["terrain"][1],x,y,1)

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


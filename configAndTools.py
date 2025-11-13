
#start of full framework rewrite
import threading
import tkinter as tk
import PIL
#this rendering engine is herby designated qdtkr (quick and dirty tkinter renderer)


#creation automatically loads the ui due to technical reasons
class UIContainer:
    def __init__(self) -> None:
        pass
        self.widgetContainer=None
        
    def load(self):
        pass

    def _load(self,mount:tk.Frame,windowSize:tuple):#internal function called by the core, that inits internal stuff first, then calls the user init function
        self.widgetContainer:tk.Frame=tk.Frame(mount,border=0,highlightthickness=0,width=windowSize[0], height=windowSize[1])
        self.widgetContainer.pack(anchor=tk.CENTER, expand = False)
        self.load()
    

    def unload(self):
        pass

    def _destroy(self):
        self.unload()
        self.widgetContainer.destroy()

#switch renderer to use pil, and use images as a render target



class Core:
    def __init__(self,title:str,windowWidth:int,WindowHeight:int,TileWidth:int,TileHeight:int,tileSize:int,targetFPS:int,targetTickRate:int, layerNumber:int=1) -> None:
        #init tkinter
        self.windowWidth:int=windowWidth
        self.windowHeight:int=WindowHeight
        self.title:str=title
        self.targetFPS=targetFPS
        self.targetTickRate=targetTickRate
        self.tileWidth=TileWidth
        self.tileHeight=TileHeight
        self.tileSize=tileSize


        self.pause=False

        #root object creation
        self.root:tk.Tk=tk.Tk()


        #config root
        self.root.title(self.title)
        self.root.geometry(str(self.windowWidth+8)+"x"+str(self.windowHeight+8))
        self.root.resizable(width=False, height=False)

        #variable for storing the current menu
        self.currentUI:UIContainer=UIContainer()
        


        #init the container objects 
        #base for everything
        baseFrame:tk.Frame=tk.Frame(self.root,background="black",border=0,highlightthickness=0,highlightcolor="black",width=self.windowWidth, height=self.windowHeight)
        baseFrame.pack(anchor=tk.CENTER, expand = False)
        #base for canvases
        canvasFrame:tk.Frame=tk.Frame(baseFrame,background="black",border=4,highlightthickness=0,highlightcolor="black",width=self.windowWidth, height=self.windowHeight)
        canvasFrame.pack(anchor=tk.CENTER, expand = False)



        #init the first canvas
        backgroundCanvas:tk.Canvas=tk.Canvas(canvasFrame,background="grey",border=0,highlightthickness=0,width=self.windowWidth, height=self.windowHeight)
        backgroundCanvas.pack(anchor=tk.CENTER, expand = False)

        #init the rest of the layers
        layersProto:list[tk.Canvas]=[backgroundCanvas]
        
        
        if(layerNumber<1):
            raise Exception("error: core layer number must be greater than ")

        for layerIndex in range(layerNumber-1):
            #create a frame for the layer
            tempFrame:tk.Frame=tk.Frame(baseFrame,background=None,border=4,highlightthickness=0,highlightcolor="black",width=self.windowWidth, height=self.windowHeight)
            tempFrame.pack(anchor=tk.CENTER, expand = False)
            
            #create a canvas in that frame
            tempCanvas:tk.Canvas=tk.Canvas(tempFrame,bg=None,border=0,highlightthickness=0,width=self.windowWidth, height=self.windowHeight)
            tempCanvas.pack(anchor=tk.CENTER, expand = False)
            #save the canvas to the list
            layersProto.append(tempCanvas)
            

        self.layers:tuple[tk.Canvas,...]=tuple(layersProto)


        #create a place to put ui
        self.uiMount:tk.Frame=tk.Frame(baseFrame,border=0,highlightthickness=0,width=self.windowWidth, height=self.windowHeight)
        self.uiMount.pack(anchor=tk.CENTER, expand = False)


        #start the running
        self.running=True

    def getWindowSize(self):#self explanitory
        return (self.windowWidth,self.windowHeight)



    def loadUIContainer(self,uiObject:UIContainer):
        self.currentUI._destroy()
        self.currentUI=uiObject
        self.currentUI._load(self.uiMount,self.getWindowSize())
        
    def getCurrentUIContainer(self):
        return self.currentUI
    
    def _getCanvas(self,layerNumber):
        if((layerNumber>=0)and(layerNumber<len(self.layers))):
            return self.layers[layerNumber]
        else:
            raise Exception("error: requested canvas id is out of bounds")
    
    
    def clearAllLayers(self):
        for layer in self.layers:
            layer.delete("all")

    def clearLayer(self,layerNumber):
        if((layerNumber>=0)and(layerNumber<len(self.layers))):
            target:tk.Canvas=self.layers[layerNumber]
            target.delete("all")
        else:
            raise Exception("error: requested layer id is out of bounds")
    
    def drawSprite(self,texture:tk.PhotoImage,imageSize:int,x:int,y:int,layer:int): 
        if((layer>=0)and(layer<len(self.layers))):#safety check
            #grab the layer
            target:tk.Canvas=self.layers[layer]
            #draw
            target.create_image(((x*imageSize)+(imageSize/2),(y*imageSize)+(imageSize/2)),image=texture)
        else:
            raise Exception("error: requested canvas id is out of bounds")

    def drawTile(self,texture:tk.PhotoImage,tileX:int,tileY:int,layer:int):
        if((layer>=0)and(layer<len(self.layers))):#safety check
            #two more safety checks
            if((tileX<0)or(tileX>self.tileWidth)):
                raise Exception("error: tileX:"+str(tileX)+" is out of bounds")
            elif((tileY<0)or(tileY>self.tileHeight)):
                raise Exception("error: tileY:"+str(tileY)+" is out of bounds")

            #grab the layer
            target:tk.Canvas=self.layers[layer]
            #draw
            target.create_image(((tileX*self.tileSize)+(self.tileSize/2),(tileY*self.tileSize)+(self.tileSize/2)),image=texture)
        else:
            raise Exception("error: requested canvas id is out of bounds")

    def quitApp(self):
        #if the root exists, destroy it
        if(isinstance(self.root,tk.Tk)):
            self.root.destroy()
            self.root=None
            self.currentUI=None

    def updateTK(self): 
        if(isinstance(self.root,tk.Tk)):
            self.root.update()
            self.root.update_idletasks()
        

    def runTK(self):
        if(isinstance(self.root,tk.Tk)):
            self.root.mainloop()


    
        





        



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
        
        





      

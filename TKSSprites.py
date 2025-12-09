import TKS
import pygame
import tks
from fastFunctions.TKSFastCode import SpriteRenderData,ImageSize,SpriteSheetData


    
#need to rework this to work with having a wrapper class that handles most animation state
class TextureSheet:
    def __init__(self,textureSurfaces:list[pygame.Surface,]|pygame.Surface,frameRate:int=0,startFrame:int=0,playOnCreation:bool=False,looping:bool=False) -> None:
        #config variables
        #init config vals:
        self.looping:bool=looping
        self.startFrame:int=startFrame
        #init surfaces and sizes
        self.renderingData=SpriteSheetData()
        if(type(textureSurfaces)==list):
            for frame in textureSurfaces:
                frameRect:pygame.Rect=frame.get_rect()
                self.renderingData.addFrame(frame,frameRect.width,frameRect.height)
        elif(type(textureSurfaces)==pygame.Surface):
            frameRect:pygame.Rect=textureSurfaces.get_rect()
            self.renderingData.addFrame(textureSurfaces,frameRect.width,frameRect.height)
        #config runtime vars
        self.renderingData.frame=startFrame
        self.animationLen=len(self.renderingData.frameList)
        self.frameTimeCarry:float=0
        self.frameRate:int=frameRate
        #config framerate delay
        if(self.frameRate>0):
            self.frameRateDelay:float=1/self.frameRate
        else:
            self.frameRateDelay:float=0
        
        #init pause variable
        self.unpaused:bool=playOnCreation
        #the sizes of every image and the current frame, in cython for speed
        

            


    def frameUpdate(self,frameTime:float):
        #if currently playing
        if(self.unpaused):
            #if nothing should stop a frame advance
            if((self.frameRate!=0)and((self.renderingData.frame<self.animationLen-1) or self.looping)):
                #calculate how long it has been since we last did this
                adjustedFrameTime=frameTime+self.frameTimeCarry
                #figure out how many frames we should advance from that
                passedFrames=int(adjustedFrameTime//self.frameRateDelay)
                #save any excess
                self.frameTimeCarry=adjustedFrameTime%self.frameRateDelay
                #store how many frames we think we should advance
                prospectiveNewFrame=self.renderingData.frame+passedFrames
                #if the new frame is less than the animation length
                if(prospectiveNewFrame<self.animationLen):
                    #thats our new frame
                    self.renderingData.frame=prospectiveNewFrame
                #instead if we are looping
                elif(self.looping):
                    #loop over to the new frame
                    self.renderingData.frame=prospectiveNewFrame%self.animationLen
                #otherwise just rebound the final frame
                else:
                    self.renderingData.frame=self.animationLen-1

    def pause(self):
        self.unpaused=False

    def play(self):
        self.unpaused=True

    def setFrame(self,frameIndex:int):
        if((frameIndex<0)or(frameIndex>=self.animationLen)):
            raise ValueError("setFrame error: frame index must be greater than zero and less than or equal to the number of frames of the animation.\nanimation max index: "+str(self.animationLen-1)+" received index: "+str(frameIndex))
        self.renderingData.frame=frameIndex

    def resetAnimation(self):
        self.renderingData.frame=self.startFrame

    def getCurrentFrame(self):
        return self.renderingData.frameList[self.renderingData.frame]
            



class AnimationSet:
    def __init__(self) -> None:
        pass
        #need to populate this and make it use the 





#need to modify this to work with having a wrapper for the animations
class BasicSprite(pygame.sprite.Sprite):
    def __init__(self,x:int,y:int,width:int,height:int,image:pygame.Surface) -> None:

        #init texture
        self.currentSpriteSheet:TextureSheet=TextureSheet(image)
        #init rects
        self.rect:pygame.Rect=pygame.Rect(x,y,width,height)
        
        #init cython data container
        self.renderData=SpriteRenderData()
        #init visibility
        self.renderData.visible=True
        #init image pos
        self.renderData.imageX=self.rect.x
        self.renderData.imageY=self.rect.y
        #init image offset
        self.renderData.imageOffsetX=0
        self.renderData.imageOffsetY=0
        

        
        


    def hide(self):
        self.renderData.visible=False



    def show(self):
        self.renderData.visible=True
 

    def changeTexture(self, newTexture:pygame.Surface):
        self.currentSpriteSheet=TextureSheet(newTexture)
        self.renderData.imageX=self.rect.x
        self.renderData.imageY=self.rect.y

    def setPos(self,x:int,y:int):
        self.rect.x=x
        self.rect.y=y
        self.renderData.imageX=self.rect.x
        self.renderData.imageY=self.rect.y


    def move(self,x:int,y:int):
       self.rect.x+=x
       self.rect.y+=y
       self.renderData.imageX=self.rect.x
       self.renderData.imageY=self.rect.y

    def setTextureOffset(self,x:int,y:int):
        self.renderData.imageOffsetX=x
        self.renderData.imageY=y
        self.renderData.imageX=self.rect.x
        self.renderData.imageY=self.rect.y

    def frameTick(self,frameTime:float):
        pass

    def unlockedTick(self):
        pass



class BasicTileSprite(BasicSprite):
    def __init__(self, tileX:int, tileY:int, width:int, height:int, tileSize:int, image: pygame.Surface,tileOffsetX:int=0,tileOffsetY:int=0) -> None:
        self.tileX=tileX
        self.tileY=tileY
        self.tileOffsetX=tileOffsetX
        self.tileOffsetY=tileOffsetY
        self.tileSize=tileSize
        super().__init__(self.tileX*self.tileSize+self.tileOffsetX, self.tileY*self.tileSize+self.tileOffsetY, width, height, image)
        

    
    def move(self, x:int, y:int):
        super().move(x,y)
        self.tileX=self.rect.x//self.tileSize
        self.tileOffsetX=self.rect.x%self.tileSize

        self.tileY=self.rect.y//self.tileSize
        self.tileOffsetY=self.rect.y%self.tileSize

    def tileMove(self, x:int, y:int):
        self.tileX+=x
        self.tileY+=y
        self.rect.x=(self.tileX*self.tileSize)+self.tileOffsetX
        self.rect.y=(self.tileSize*self.tileY)+self.tileOffsetY
        self.imageX=self.rect.x
        self.imageY=self.rect.y

        
    def setPos(self, x:int, y:int):
        super().setPos(x,y)
        self.tileX=self.rect.x//self.tileSize
        self.tileOffsetX=self.rect.x%self.tileSize

        self.tileY=self.rect.y//self.tileSize
        self.tileOffsetY=self.rect.y%self.tileSize

    def setTilePos(self,x:int, y:int):
        self.tileX=x
        self.tileY=y
        self.rect.x=(self.tileX*self.tileSize)+self.tileOffsetX
        self.rect.y=(self.tileSize*self.tileY)+self.tileOffsetY
        self.imageX=self.rect.x
        self.imageY=self.rect.y
        
    def getTileOffset(self):
        return (self.tileOffsetX,self.tileOffsetY)

    def setTileOffset(self, x:int, y:int):
        self.tileOffsetX=x
        self.tileOffsetY=y
        self.rect.x=(self.tileSize*self.tileX)+self.tileOffsetX
        self.rect.y=(self.tileSize*self.tileY)+self.tileOffsetY
        self.imageX=self.rect.x
        self.imageY=self.rect.y

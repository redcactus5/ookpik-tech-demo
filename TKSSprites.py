import TKS
import pygame




class SpriteSheet:
    def __init__(self,textureSurfaces:list[pygame.Surface,]|pygame.Surface,frameRate:int=0,startFrame:int=0,playOnCreation:bool=False,looping:bool=False) -> None:
        #config variables
        self.looping:bool=looping
        self.frame:int=startFrame
        self.startFrame:int=startFrame
        if(type(textureSurfaces)==list):
            self.textures:list[pygame.Surface]=textureSurfaces
        elif(type(textureSurfaces)==pygame.Surface):
            self.textures:list[pygame.Surface]=[textureSurfaces]
        self.animationLen=len(self.textures)
        self.frameTimeCarry:float=0
        self.frameRate:int=frameRate
        if(self.frameRate>0):
            self.frameRateDelay:float=1/self.frameRate
        else:
            self.frameRateDelay:float=0
        self.unpaused:bool=playOnCreation

    def getImageRect(self):
        return self.textures[self.frame].get_rect().copy()

    def frameUpdate(self,frameTime:float):
        if(self.unpaused):
            if((self.frameRate!=0)and((self.frame<self.animationLen-1) or self.looping)):
                adjustedFrameTime=frameTime+self.frameTimeCarry
                passedFrames=int(adjustedFrameTime//self.frameRateDelay)
                self.frameTimeCarry=adjustedFrameTime%self.frameRateDelay
                prospectiveNewFrame=self.frame+passedFrames
                if(prospectiveNewFrame<self.animationLen):
                    self.frame=prospectiveNewFrame
                elif(self.looping):
                    self.frame=prospectiveNewFrame%self.animationLen
                else:
                    self.frame=self.animationLen-1

    def pause(self):
        self.unpaused=False

    def play(self):
        self.unpaused=True

    def setFrame(self,frameIndex:int):
        if((frameIndex<0)or(frameIndex>=self.animationLen)):
            raise ValueError("setFrame error: frame index must be greater than zero and less than or equal to the number of frames of the animation.\nanimation max index: "+str(self.animationLen-1)+" received index: "+str(frameIndex))
        self.frame=frameIndex

    def resetAnimation(self):
        self.frame=self.startFrame

    def getCurrentFrame(self):
        return self.textures[self.frame]
            

            










class BasicSprite(pygame.sprite.Sprite):
    def __init__(self,x:int,y:int,width:int,height:int,image:pygame.Surface) -> None:
        super().__init__()
        #init texture
        self.currentSpriteSheet:SpriteSheet=SpriteSheet(image)
        #init rects
        self.rect:pygame.Rect=pygame.Rect(x,y,width,height)
        self.imageRect:pygame.Rect=self.currentSpriteSheet.getImageRect()
        #init visibility
        self.visible=True
        #init image pos
        self.imageRect.x=self.rect.x
        self.imageRect.y=self.rect.y
        #init image offset
        self.imageOffsetX=0
        self.imageOffsetY=0
        


    def hide(self):
        self.visible=False



    def show(self):
        self.visible=True
 

    def changeTexture(self, newTexture:pygame.Surface):
        self.currentSpriteSheet=SpriteSheet(newTexture)
        self.imageRect=self.currentSpriteSheet.getImageRect()
        self.imageRect.x=self.rect.x+self.imageOffsetX
        self.imageRect.y=self.rect.y+self.imageOffsetY

    def setPos(self,x:int,y:int):
        self.rect.x=x
        self.rect.y=y
        self.imageRect.x=self.rect.x+self.imageOffsetX
        self.imageRect.y=self.rect.y+self.imageOffsetY


    def move(self,x:int,y:int):
       self.rect.x+=x
       self.rect.y+=y
       self.imageRect.x=self.rect.x+self.imageOffsetX
       self.imageRect.y=self.rect.y+self.imageOffsetY

    def setTextureOffset(self,x:int,y:int):
        self.imageOffsetX=x
        self.imageOffsetY=y
        self.imageRect.x=self.rect.x+self.imageOffsetX
        self.imageRect.y=self.rect.y+self.imageOffsetY

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
        self.imageRect.x=self.rect.x+self.imageOffsetX
        self.imageRect.y=self.rect.y+self.imageOffsetY

        
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
        self.imageRect.x=self.rect.x+self.imageOffsetX
        self.imageRect.y=self.rect.y+self.imageOffsetY
        
    def getTileOffset(self):
        return (self.tileOffsetX,self.tileOffsetY)

    def setTileOffset(self, x:int, y:int):
        self.tileOffsetX=x
        self.tileOffsetY=y
        self.rect.x=(self.tileSize*self.tileX)+self.tileOffsetX
        self.rect.y=(self.tileSize*self.tileY)+self.tileOffsetY
        self.imageRect.x=self.rect.x+self.imageOffsetX
        self.imageRect.y=self.rect.y+self.imageOffsetY

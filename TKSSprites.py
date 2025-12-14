import TKS
import pygame
import tks
from fastFunctions.TKSFastCode import SpriteRenderData,ImageSize,SpriteSheetData


    

            






#need to modify this to work with having a wrapper for the animations
class BasicSprite():
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
        self.renderData.imageOffsetY=y
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

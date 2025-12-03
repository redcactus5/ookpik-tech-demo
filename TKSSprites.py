import TKS
import pygame

class BasicSprite(pygame.sprite.Sprite):
    def __init__(self,x:int,y:int,width:int,height:int,image:pygame.Surface) -> None:
        super().__init__()
        #init texture
        self.image:pygame.Surface=image
        #init rects
        self.rect:pygame.Rect=pygame.Rect(x,y,width,height)
        self.imageRect:pygame.Rect=self.image.get_rect()
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
        self.image=newTexture
        self.imageRect=self.image.get_rect()
        self.imageRect.x=self.rect.x+self.imageOffsetX
        self.imageRect.y=self.rect.y+self.imageOffsetY

    def setPos(self,x,y):
        self.rect.x=x
        self.rect.y=y
        self.imageRect.x=self.rect.x+self.imageOffsetX
        self.imageRect.y=self.rect.y+self.imageOffsetY


    def move(self,x,y):
       self.rect.x+=x
       self.rect.y+=y
       self.imageRect.x=self.rect.x+self.imageOffsetX
       self.imageRect.y=self.rect.y+self.imageOffsetY

    def setTextureOffset(self,x,y):
        self.imageOffsetX=x
        self.imageOffsetY=y
        self.imageRect.x=self.rect.x+self.imageOffsetX
        self.imageRect.y=self.rect.y+self.imageOffsetY

    def frameTick(self,frameTime):
        pass

    def unlockedTick(self):
        pass

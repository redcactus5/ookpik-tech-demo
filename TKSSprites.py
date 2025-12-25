import TKS
import pygame
from fastCode.TKSFastCode import ImageSize,AnimationFrames,Animation,AnimationControllerCore,SpriteCore,TileSpriteCore

    

class AnimationController:
    def __init__(self,animationDataList:list[Animation],startingAnimation:int=0) -> None:
        self.core:AnimationControllerCore=AnimationControllerCore(animationDataList,startingAnimation)
        
    def frameUpdate(self,frameTime:float):
        self.core.frameUpdate(frameTime)

    def swapAnimations(self,newAnimationIndex:int):
        self.core.swapAnimation(newAnimationIndex)

    def pause(self):
        self.core.pause()

    def play(self):
        self.core.play()

    def setFrame(self, frame:int):
        self.core.setFrame(frame)

    def resetAnimation(self):
        self.core.resetAnimation()




#need to modify this to work with having a wrapper for the animations
class BasicSprite():
    def __init__(self,x:int,y:int,width:int,height:int,animationController:AnimationController,visible:bool=True,imageOffsetX:int=0,imageOffsetY:int=0) -> None:
        self.core=SpriteCore(x,y,width,height,visible,animationController.core,imageOffsetX,imageOffsetY)
        
    def hide(self):
        self.core.hide()

    def show(self):
        self.core.show()

    def setPos(self,x:int,y:int):
        self.core.setPos(x,y)

    def move(self,x:int,y:int):
       self.core.move(x,y)

    def setTextureOffset(self,x:int,y:int):
        self.core.setTextureOffset(x,y)

    def frameTick(self,frameTime:float):
        pass

    def unlockedTick(self):
        pass



class BasicTileSprite(BasicSprite):
    def __init__(self, tileX:int, tileY:int, width:int, height:int, tileSize:int, animationController:AnimationController, tileOffsetX:int=0,tileOffsetY:int=0,imageOffsetX:int=0,imageOffsetY:int=0) -> None:
        self.core=BasicTileSprite(tileX,tileY,width,height,tileSize,animationController,tileOffsetX,tileOffsetY,imageOffsetX,imageOffsetY)
    
    def move(self, x:int, y:int):
        self.core.move(x,y)

    def tileMove(self, x:int, y:int):
        self.core.tileMove(x,y)
   
    def setPos(self, x:int, y:int):
        self.core.setPos(x,y)

    def setTilePos(self,x:int, y:int):
        self.core.setTilePos(x,y)
        
    def getTileOffset(self):
        return self.core.getTileOffset()

    def setTileOffset(self, x:int, y:int):
        self.core.setTileOffset(x,y)

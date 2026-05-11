import random
import math
import time
import os
MAPWIDTH=115
MAPHEIGHT=30
PATHS=(6,30)
TREES=(50,280)
SEEDS=(15,30)
CLEARMODE=2


OWLPIC=["          __________-------____                 ____-------__________","          \------____-------___--__---------__--___-------____------/","           \//////// / / / / / \   _-------_   / \ \ \ \ \ \\\\\\\\\\\\\\\\/","             \////-/-/------/_/_| /___   ___\\ |_\_\------\-\-\\\\\\\\/","               --//// / /  /  //|| (O)\ /(O) ||\\\\  \  \ \ \\\\\\\\--","                    ---__/  // /| \\_  /V\  _/ |\ \\\\  \__---","                         -//  / /\\_ ------- _/\ \  \\\\-","                           \_/_/ /\\---------/\ \_\\_/","                               ----\   |   /----","                                    | -|- |","                                   /   |   \\","                                   ---- \___|"]

#memory micro optomisation
if(True):
    #compile the owl ascii art into a single string
    temp=""
    for line in OWLPIC:
        temp=temp+line+"\n"
    OWLPIC=temp
    
    #figure out which clear function to user
    try:
        #inspired by geeksforgeeks example code
        if(os.name=='nt'):#windows
            os.system('cls')
            CLEARMODE=0
        else:#posix
            os.system('clear')
            CLEARMODE=1
    except Exception:#no clear command avalible
        ln(50)
        CLEARMODE=2



#handly newline function
def ln(*argv):
    if(len(argv)<1):
        print("")
    elif(len(argv)>1):
        raise Exception("ln error: too many arguments")
    elif(not (type(argv[0])==int)):
        raise Exception("ln error: invalid argument type, must be positive integer")
    elif(argv[0]<1):
        raise Exception("ln error: invalid argument type, must be positive integer")
    elif(argv[0]<2):
        print("")
    else:
        print("\n"*(argv[0]-1))
    
    
#cross platform terminal clearing function
def clear():
    global CLEARMODE
    if(CLEARMODE==0):
        os.system('cls')
    elif(CLEARMODE==1):
        os.system('clear')
    else:
        ln(50)




class Ookpik:
    def __init__(self,x,y,dir):
        self.x=x
        self.y=y
        self.dir=dir
    
    def getCoords(self):
        coords=(self.y,self.x)
        return coords

    def setPos(self,x,y,dir):
        self.x=x
        self.y=y
        self.dir=dir
    
    def getDir(self):
        return self.dir

    def turnLeft(self):
        self.dir-=1
        if(self.dir<0):
            self.dir=3
    
    def turnRight(self):
        self.dir+=1
        if(self.dir>3):
            self.dir=0
    
    def move(self):
        if(self.dir==0):
            self.y-=1
        elif(self.dir==1):
            self.x+=1
        elif(self.dir==2):
            self.y+=1
        elif(self.dir==3):
            self.x-=1
        
    
    def testMove(self):
        x=self.x
        y=self.y
        if(self.dir==0):
            y-=1
        elif(self.dir==1):
            x+=1
        elif(self.dir==2):
            y+=1
        elif(self.dir==3):
            x-=1
        return (y,x)










def checkCoords(coord1,coord2):
    return(coord1[0]==coord2[0] and coord1[1]==coord2[1])
    
    
    
def coordInList(coord, coordList):
    for listCoord in coordList:
        if(checkCoords(listCoord,coord)):
            return True      
    return False  




def floodFillCheck(map, whiteSpace):

    hitCoords=[]
    toHitCoords=[]
    
    
    
    mapXLimit=len(map[0])
    mapYLimit=len(map)
    
    
    while True:
        startX=random.randint(0,len(map[0])-1)
        startY=random.randint(0,len(map)-1)
        if(map[startY][startX]==0):
            toHitCoords.append((startY,startX))
            break
    
    while (len(toHitCoords)>0):
        testCoord=toHitCoords.pop(0)
        hitCoords.append(testCoord)
        if(map[testCoord[0]][testCoord[1]]==0):
            whiteSpace-=1
            toTest=[]
            toTest.append((testCoord[0]+1,testCoord[1]))
            toTest.append((testCoord[0]-1,testCoord[1]))
            toTest.append((testCoord[0],testCoord[1]+1))
            toTest.append((testCoord[0],testCoord[1]-1))
            
            for coord in toTest:
            
                if((coord[0]>=0 and coord[0]<mapYLimit) and (coord[1]>=0 and coord[1]<mapXLimit)):
                    if(map[coord[0]][coord[1]]==0):
                        if(not(coordInList(coord, toHitCoords) or coordInList(coord, hitCoords))):
                            toHitCoords.append(coord)
                
            
        


    return (whiteSpace==0)
   
    
    
    
    
    
    


# function for line generation 
def bresenham(x1, y1, x2, y2): 
    #We draw lines from left to right.
    #x1 < x2 and y1 < y2
    #Slope of the line is between 0 and 1. We draw a line from lower left to upper right.


    #credit for this function goes to ash264 from geeksforgeeks
    #it is mostly their code with my own slight modifaction
    
    #i have absolutely now idea how this works, i just know it does
    
    pathPoints=[]
    pathPoints.append((y1,x1))
    pathPoints.append((y2,x2))
    
    xPoints=[]
    yPoints=[]
    flipH=False
    flipV=False
    
    if(y1>y2):
        flipV=True
        temp=y1
        y1=y2
        y2=temp
    if(x1>x2):
        flipH=True
        temp=x1
        x1=x2
        x2=temp
    
    if(x1==x2):
        for y in range(x1,x2):
            pathPoints.append((y,x1))
    elif(y1==y2):
        for x in range(y1,y2):
            pathPoints.append((x,y1))  
    
    else:
        
        
        m_new = 2 * (y2 - y1) 
        slope_error_new = m_new - (x2 - x1) 
        
        y = y1 
        for x in range(x1, x2+1): 

            yPoints.append(y)
            xPoints.append(x)
            
            
      
            # Add slope to increment angle formed 
            slope_error_new = slope_error_new + m_new 
      
            # Slope error reached limit, time to 
            # increment y and update slope error. 
            if (slope_error_new >= 0): 
                y = y+1
                slope_error_new = slope_error_new - 2 * (x2 - x1) 
    
    
        
        if(flipH):
            xPoints.reverse()
        if(flipV):
            yPoints.reverse()
        
        for i in range(len(xPoints)):
            pathPoints.append((yPoints[i],xPoints[i]))
        
    return pathPoints



def squarePlot(map,y,x,pen):
    map[y][x]=pen
    
    map[y+1][x]=pen
    
    map[y][x+1]=pen
    
    map[y+1][x+1]=pen
    
    

    return map

def uiHeader(actionLog,seedsRemaining,moves):
    clear()
    print("  ookpik v1.2  ")
    
    print("----------------------")
    print("seeds remaining: "+str(seedsRemaining))
    print("moves: "+str(moves))
    print("----------------------")
    for action in actionLog:
        print(action)
    print("----------------------")

    



def renderMap(map, ookpik,actionLog,seeds,moves):
    
    renderedMap=""
    for row in range(len(map)):
        rowString=""
        for col in range(len(map[0])):
        
            tile=map[row][col]
            if(checkCoords(ookpik.getCoords(),(row,col))):
                dir=ookpik.getDir()
                if(dir==0):
                    rowString+="˄"
                elif(dir==1):
                    rowString+=">"
                elif(dir==2):
                    rowString+="˅"
                else:
                    rowString+="<"
            else:
                if(tile==1):
                    rowString+="█"
                elif(tile==0):
                    rowString+=" "
                elif(tile==2):
                    rowString+="@"

        renderedMap=renderedMap+"\n"+rowString

    uiHeader(actionLog,seeds,moves)
    print(renderedMap)
    print("enter W to advance, A to turn left, and D to turn right")


def generateMap(w,h,paths,trees,seeds,owl):
    
    map=[]
    attempt=1
    start=time.time()
    while True:

        print("starting map generation...")
        print("generating land...")
        for i in range(h):
            collum=[]
            for j in range(w):
                collum.append(1)
            map.append(collum)
        print("done!")
        
        print("seeding clearings...")
        pathSeeds=[]
        for path in range(paths):
            x=random.randint(2,w-4)
            y=random.randint(2,h-4)
            pathSeeds.append((y,x))
            
        print("done!")
        
        #y1-y2/x1-x2
        print("plotting paths...")
        pathPoints=[]
        for path1 in pathSeeds:
            for path2 in pathSeeds:
                pathPoints+=bresenham(path1[1], path1[0], path2[1], path2[0])
        print("done!")
        
        print("cutting paths...")
        for point in pathPoints:
            squarePlot(map,point[0],point[1], 0)
        print("done!")
        
        print("planting trees...")
        localTrees=trees
        while (localTrees > 0):
            treeX=random.randint(1,w-2)
            treeY=random.randint(1,h-2)
            
            if(map[treeY][treeX]==0):
                map[treeY][treeX]=1
                localTrees-=1
        print("done!")  
        
        print("counting whitespaces...")
        totalWhiteSpace=0
        for y in range(len(map)):
            for x in range(len(map[0])):
                if(map[y][x]==0):
                    totalWhiteSpace+=1
        print("done!")
        
        print("verifying map is completeable...")
        safeMap=floodFillCheck(map,totalWhiteSpace)
        
        if(safeMap):
            break
        
        print("map is not completeable. restarting generation...")
        print("destroying everything...")   
        map=[]
        print("done!")
        attempt+=1
    
    print("done!")
    
    print("scattering seeds...")
    while (seeds > 0):
        seedX=random.randint(1,w-2)
        seedY=random.randint(1,h-2)
        
        if(map[seedY][seedX]==0):
            map[seedY][seedX]=2
            seeds-=1
    print("done!")
    
    print("placing owl...")
    while True:
        x=random.randint(1,len(map[0])-1)
        y=random.randint(1,len(map)-1)
        if(map[y][x]==0):
            dir=random.randint(0,3)
            owl.setPos(x,y,dir)
            break
        
        
    print("done!")
    completionTime=time.time()-start
    
    ln()
    print("map generation finished")
    print("took "+str(attempt)+" attempt(s)")
    print("completed in "+str(completionTime)+" seconds")
    
    
    
    return map




def multipleChoiceScreen(prompt, options, optionKeys, acurracy):

    while True:
        #print prompt
        clear()
        
        print(prompt)
        ln(2)
        for option in options:
            print(option)
        ln()
        
        #get user input
        print("please enter a selection:")
        selection=input()
        
        #if the input is not None
        if(len(selection)>=1):
            #for every possible option
            for i in range(len(optionKeys)):
            
                #create a local acurracy variable
                localAcurracy=acurracy
                
                #if the current selection is shorter than local accuracy
                if(len(selection)<localAcurracy):
                    #set local accuracy to the length of selection
                    localAcurracy=len(selection) 
                #cut the portion of the entry we want
                test=selection[0:localAcurracy]
                
                #if it matches the current option key
                if(test==optionKeys[i]):
                    clear()
                    return i+1 #return that key's index
                #otherwise go around again
            

        #if the input is not found or None
        clear()
        ln()
        
        print("invalid input. please choose from the provided options.")
        print("please try again")
        ln(3)
        input("press enter to continue")
    
    
def booleanChoiceScreen(prompt):
    options=("(y)es","(n)o")
    keys=("y","n")
    if(multipleChoiceScreen(prompt, options, keys, 1)==1):
        return True
    return False
    

    
    
owl=Ookpik(0,0,0)
 
def updateActionLog(actionLog, newAction):
    actionLog.pop(0)
    actionLog.append(newAction)
    return actionLog
    
    



def engine(owl,map,seeds):
    startTime=time.time()
    actionLog=[" "," "," "]
    localSeeds=seeds
    moves=0
    while True:
    
        if(localSeeds<=0):
            
            renderMap(map,owl,actionLog,localSeeds,moves)
            print("enter W to advance, A to turn left, and D to turn right")
            return (True,time.time()-startTime,moves)
    
        action=""
        while True:
            
            renderMap(map,owl,actionLog,localSeeds,moves)
            
            action=input()
            userActions=("W","A","D","w","a","d"," ","",None)
            if(action in userActions):
                break
            clear()
            print("input error! please only enter one of the provided inputs")
            ln(3)
            input("press enter to continue")
        
        #blank and space are mapped to advance
        moves+=1
        if(action in ("W","w"," ","",None)):
            potentialCoord=owl.testMove()
            
            if(potentialCoord[0]>len(map)-1 or potentialCoord[0]<0 or potentialCoord[1]>len(map[0])-1 or potentialCoord[1]<0):
                return (False,time.time()-startTime,moves)
            
            if(map[potentialCoord[0]][potentialCoord[1]]==1):
                return (False,time.time()-startTime,moves)
            
            owl.move()
            actionLog=updateActionLog(actionLog,"moved fowards")
            
            newpos=owl.getCoords()
            
            if(map[newpos[0]][newpos[1]]==2):
                map[newpos[0]][newpos[1]]=0
                localSeeds-=1
                actionLog=updateActionLog(actionLog,"collected seed")
        
        elif(action in ("a","A")):
            owl.turnLeft()
            actionLog=updateActionLog(actionLog,"turned left")
        
        elif(action in ("d","D")):
            owl.turnRight()
            actionLog=updateActionLog(actionLog,"turned right")


def winScreen(time, moves,mapSize):
    clear()
    ln(3)
    print("++++++++++++++++++++++++++++++++")
    print("           you win!")
    print("++++++++++++++++++++++++++++++++")
    ln(2)
    print("--------------------------------")
    if(mapSize):
        print("map size: large")
    else:
        print("map size: small")
    print("completion time: "+str(time)+" seconds")
    print("total moves: "+str(moves))
    print("--------------------------------")
    ln(2)
    input("press enter to continue")
    clear()
    

def loseScreen(time, moves,mapSize):
    clear()
    ln(3)
    print("++++++++++++++++++++++++++++++++")
    print("          you died!")
    print("++++++++++++++++++++++++++++++++")
    ln(2)
    print("--------------------------------")
    if(mapSize):
        print("map size: large")
    else:
        print("map size: small")
    print("time: "+str(time)+" seconds")
    print("moves: "+str(moves))
    print("--------------------------------")
    ln(2)
    input("press enter to continue")
    clear()

def mainMenu():
    global MAPWIDTH
    global MAPHEIGHT
    global PATHS
    global TREES
    global SEEDS
    global OWLPIC
    while True:
        userInput=multipleChoiceScreen("ookpik v1.2"+"\n\n"+OWLPIC,("(s)tart game","(h)elp","(q)uit"),("s","h","q","e"),1)
        
        if(userInput==1):
            mapSizeCheck=multipleChoiceScreen("please select the map size to play on",("(b)ig map","(s)mall map"),("b","s"),1)
            clear()
            print("starting game...")
            ln()
            owl=Ookpik(0,0,0)
            
            mapSize=(mapSizeCheck==1)
            
            map=generateMap(MAPWIDTH, MAPHEIGHT, PATHS[mapSize], TREES[mapSize], SEEDS[mapSize], owl)
            ln(2)
            input("press enter to start the game")
            win=engine(owl,map,SEEDS[mapSize])
            timer=str(win[1])

            if('.' in timer):
                temp=timer.split('.')
                temp2=temp[1]
                temp2=temp2[0:2]
                timer=temp[0]+"."+temp2

            
            if(win[0]):
                winScreen(timer,win[2],mapSize)
            else:
                loseScreen(timer,win[2],mapSize)
            
        elif(userInput==2):
            clear()
            print("welcome to ookpik!")
            print("ookpik is a simple roguelike where you must navigate the owl")
            print("(the arrow: \">\") through a randomly generated forest and collect all the seeds")
            print("(the at signs: \"@\") while avoiding the trees (the filled in tiles: \"█\")")
            print("as fast as possible and in as few moves as possible. as an owl, you can only")
            print("hop fowards one space at a time and turn left or right on the spot, 90 degrees")
            print("at a time. the controls are \"w\" and blank to go fowards, and \"a\" and ")
            print("\"d\" to turn left and right respectively. thats basically it for instruction.")
            print("have fun!")
            ln(2)
            input("press enter to continue")
        elif(userInput>2):
            clear()
            print("thank you for playing ookpik")
            break
    
mainMenu()
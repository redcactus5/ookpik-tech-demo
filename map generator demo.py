import random
import math
import time
import os



MAPWIDTH=115
MAPHEIGHT=45
PATHS=(6,20)
TREES=(50,350)
SEEDS=(15,30)
CLEARMODE=2
MAPCHARS=(" ","█","#","$","8","@")
OWLPIC=""



def init():
    global OWLPIC
    global CLEARMODE
    rawOwl=["          __________-------____                 ____-------__________","          \------____-------___--__---------__--___-------____------/","           \//////// / / / / / \   _-------_   / \ \ \ \ \ \\\\\\\\\\\\\\\\/","             \////-/-/------/_/_| /___   ___\\ |_\_\------\-\-\\\\\\\\/","               --//// / /  /  //|| (O)\ /(O) ||\\\\  \  \ \ \\\\\\\\--","                    ---__/  // /| \\_  /V\  _/ |\ \\\\  \__---","                         -//  / /\\_ ------- _/\ \  \\\\-","                           \_/_/ /\\---------/\ \_\\_/","                               ----\   |   /----","                                    | -|- |","                                   /   |   \\","                                   ---- \___|"]
    #compile the owl ascii art into a single string
    temp=""
    for line in rawOwl:
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

init()



#handly ln function, very uncomplicated
def ln(number:int=1):

    if(type(number)!=int):
        raise ValueError("error: argument must be an integer")
    elif(number<=0):
        raise ValueError("error: argument must be greater than zero")
    elif(number>0):
        print("\n"*(number),end="")
    else:
        raise ValueError("error: argument somehow hit the no match case, even though that should be impossible. \n(what the heck did you feed this poor function?) \nproblem argument value: "+str(number)+" problem argument value's type: "+str(type(number)))




class _ClearHandler:
    def __init__(self) -> None:
        import ctypes
        import sys
        import os
        self.localCT=ctypes
        self.localSY=sys
        self.localOS=os
        self.clearMode:int=0
        self._clearOperationDispatcher = {
            0: lambda: self._InternalAutoClearConfig(),
            1: lambda: self.localOS.system('cls'),
            2: lambda: self.localOS.system('clear'),
            3: lambda: print("\033[2J\033[3J\033[H", end=''),
            4: lambda: ln(100),
        }


    def _InternalAutoClearConfig(self)->None:



        try:

            if (self.localOS.name == 'nt'):

                #ansi compatible check
                if (self.localSY.stdout.isatty()):
                    self.clearMode=3
                    #enable ansi
                    kernel32 = self.localCT.windll.kernel32
                    handle = kernel32.GetStdHandle(-11)
                    mode = self.localCT.c_uint32()
                    if kernel32.GetConsoleMode(handle, self.localCT.byref(mode)):
                        kernel32.SetConsoleMode(handle, mode.value | 0x0004)
                    #clear
                    print("\033[2J\033[3J\033[H", end='')




                #determine what else we could be talking to
                else:


                    isterminternal=False
                    try:
                        kernel32 = self.localCT.windll.kernel32
                        h = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
                        mode = self.localCT.c_ulong()
                        isterminternal= bool(kernel32.GetConsoleMode(h, self.localCT.byref(mode)))
                    except Exception:
                        isterminternal=False
                    if(isterminternal):
                        self.clearMode=4
                        self.localOS.system('cls')
                        self.clearMode=1
                    else:
                        self.clearMode=5
                        ln(100)
                        self.clearMode=4





            elif(self.localOS.name == 'posix'):
                self.clearMode=5
                if (self.localSY.stdout.isatty()):
                    term = self.localOS.environ.get('TERM', '')
                    if (term == 'dumb'):
                        self.clearMode=4
                        self.localOS.system('clear')

                        self.clearMode=2
                    elif(not term):
                        self.clearMode=5
                        ln(100)
                        self.clearMode=4
                    else:
                        self.clearMode=3
                        print("\033[2J\033[3J\033[H", end='')




                else:
                    self.clearMode=4
                    ln(100)

            else:
                self.clearMode=4
                ln(100)


        except:
            if(self.clearMode==5):
                raise Exception("critical system error: easy cli fallback clear method failed to run!")
            self.clearMode=4
            ln(100)



    def clear(self):
        #this is what is usually called. notice how small it is? that means its faster than init!
        clearOp = self._clearOperationDispatcher.get(self.clearMode)
        if(clearOp is None):
            raise Exception("critical error: clear mode set to invalid value!\nvalue: "+str(self.clearMode))
        else:
            clearOp()




    def reDetermineTerminalClearType(self):
        self._InternalAutoClearConfig()


_PrivateClearHandlerObject=_ClearHandler()

def clear():
    _PrivateClearHandlerObject.clear()


def findShortestDistanceCoord(testCoords,targetCoord,mapList,stage,zoneIndex, allZonesCount):
    bestCoord=testCoords[0]
    minDist=findDistance(targetCoord[0],targetCoord[1],testCoords[0][0],testCoords[0][1])
    for coord in range(1,len(testCoords)):
        demoMap=duplicateMapList(mapList)
        line=bresenham(targetCoord[1],targetCoord[0],testCoords[coord][1],testCoords[coord][0])
        for lineCoord in line:
            demoMap[lineCoord[0]][lineCoord[1]]=3
        distance=findDistance(targetCoord[0],targetCoord[1],testCoords[coord][0],testCoords[coord][1])
        if(distance<minDist):
            minDist=distance
            bestCoord=testCoords[coord]
        if(stage==0):
            renderMapList(demoMap,"looking for best repair path for error "+str(zoneIndex)+" of "+str(allZonesCount)+", checking possible endpoint: "+str(coord)+" of "+str(len(testCoords)))
        elif(stage==1):
            renderMapList(demoMap,"double checking best repair path for error "+str(zoneIndex)+" of "+str(allZonesCount)+", checking possible start point: "+str(coord)+" of "+str(len(testCoords)))

    return bestCoord


def findDistance(y1,x1,y2,x2):
    return math.hypot((x2-x1),(y2-y1))



def checkCoords(coord1,coord2):
    return(coord1[0]==coord2[0] and coord1[1]==coord2[1])



def coordInList(coord, coordList):
    for listCoord in coordList:
        if(checkCoords(listCoord,coord)):
            return True
    return False




def renderMapList(mapList,currentOpp):
    global MAPCHARS
    localChars=MAPCHARS

    renderedMapList=[""]*((len(mapList)*len(mapList[0]))+len(mapList[0])+2)
    renderedMapList[0]=currentOpp
    renderedMapList[1]="\n"
    rowIndex=2
    for row in range(len(mapList)):
        for col in range(len(mapList[0])):

            tile=mapList[row][col]

            renderedMapList[rowIndex]=localChars[tile]

            rowIndex+=1
        renderedMapList[rowIndex]="\n"
        rowIndex+=1

    renderedMap="".join(renderedMapList)


    clear()
    print(renderedMap,end="")
    time.sleep(0.005)




def floodFillCheck(mapList, whiteSpace):

    hitCoords:set[tuple[int,int]]=set()
    toHitCoords:set[tuple[int,int]]=set()
    goodCoords=[]

    localWhitespace=whiteSpace
    mapListXLimit=len(mapList[0])
    mapListYLimit=len(mapList)






    while True:
        startX=random.randint(0,len(mapList[0])-1)
        startY=random.randint(0,len(mapList)-1)
        if(mapList[startY][startX]==0):
            toHitCoords.add((startY,startX))
            break

    while (len(toHitCoords)>0):
        testCoord=toHitCoords.pop()
        hitCoords.add(testCoord)
        renderMapList(mapList,"floodfill map winable check, "+str(whiteSpace)+" left to find out of "+str(localWhitespace))

        if(mapList[testCoord[0]][testCoord[1]]==0):
            goodCoords.append((testCoord[0],testCoord[1]))
            whiteSpace-=1
            mapList[testCoord[0]][testCoord[1]]=2
            toTest=[
                (testCoord[0]+1,testCoord[1]),
                (testCoord[0]-1,testCoord[1]),
                (testCoord[0],testCoord[1]+1),
                (testCoord[0],testCoord[1]-1)
            ]

            for coord in toTest:
                if((coord[0]>=0 and coord[0]<mapListYLimit) and (coord[1]>=0 and coord[1]<mapListXLimit)):
                    if(mapList[coord[0]][coord[1]]==0):
                        if(not((coord in toHitCoords) or (coord in hitCoords))):
                            toHitCoords.add(coord)






    renderMapList(mapList,"floodfill map winable check, "+str(whiteSpace)+" left to find out of "+str(localWhitespace))
    return ((whiteSpace==0),goodCoords)



def bresenham(x1, y1, x2, y2):
    #a list to store the generated line
    pathPoints=[]

    #figure out how far away the two points are
    xDistance=abs(x2-x1)
    yDistance=abs(y2-y1)

    #figure out what direction to go in (default left to right)
    stepX=1
    stepY=1
    if(x1>x2):
        stepX=-1
    if(y1>y2):
        stepY=-1

    #create our intermediate location variables and init them with our starting coord
    currentX=x1
    currentY=y1

    #i have no idea how this works, it just does

    #if the line is more more horizontal
    if(xDistance>yDistance):

        #init our error to half the x distance ignoring the remainder
        vectorError=xDistance//2

        #while we havent hit the end x
        while(currentX!=x2):

            #save our current location to the in progress line
            pathPoints.append((currentY, currentX))

            #update our error with our y distance
            vectorError-=yDistance

            #if error is negitive, its time to update y
            if(vectorError<0):
                #increment our current y
                currentY+=stepY
                #update our error with x distance
                vectorError+=xDistance
                #save our current location to the in progress line so we get a contiguous line
                pathPoints.append((currentY, currentX))


            #increment to next x
            currentX+=stepX

    #if the line is more vertical
    else:

        #init our error to half the y distance ignoring the remainder
        vectorError=yDistance//2

        #while we havent hit the end y
        while (currentY!=y2):

            #save our current location to the in progress line
            pathPoints.append((currentY, currentX))

            #update our error with our x distance
            vectorError-=xDistance

            #if error is negitive
            if (vectorError<0):

                #increment our current x
                currentX+=stepX

                #update our error with y distance
                vectorError+=yDistance

                #save our current location to the in progress line so we get a contiguous line
                pathPoints.append((currentY, currentX))

            #increment to next y
            currentY+=stepY

    # Add the final point
    pathPoints.append((y2, x2))

    return pathPoints


def floodFillGrouper(mapList, startCoordinate,groupNum):

    hitCoords:set[tuple[int,int]]=set()
    toHitCoords:set[tuple[int,int]]=set([startCoordinate])
    goodCoords=[]

    mapListXLimit=len(mapList[0])
    mapListYLimit=len(mapList)







    startX=startCoordinate[0]
    startY=startCoordinate[1]


    while (len(toHitCoords)>0):

        testCoord=toHitCoords.pop()
        hitCoords.add(testCoord)


        if(mapList[testCoord[0]][testCoord[1]]==0):
            renderMapList(mapList,"condensing map into zones, creating group "+str(groupNum))
            goodCoords.append((testCoord[0],testCoord[1]))
            mapList[testCoord[0]][testCoord[1]]=2
            toTest=[
                (testCoord[0]+1,testCoord[1]),
                (testCoord[0]-1,testCoord[1]),
                (testCoord[0],testCoord[1]+1),
                (testCoord[0],testCoord[1]-1)
            ]

            for coord in toTest:

                if((coord[0]>=0 and coord[0]<mapListYLimit) and (coord[1]>=0 and coord[1]<mapListXLimit)):
                    if(mapList[coord[0]][coord[1]]==0):
                        if(not((coord in toHitCoords) or (coord in hitCoords))):
                            toHitCoords.add(coord)






    renderMapList(mapList,"condensing map into zones, creating group "+str(groupNum))
    return goodCoords


def duplicateMapList(mapList):
    return [[x for x in y] for y in mapList]





def squarePlot(mapList,y,x,pen,uiHeader):
    renderFlag=True

    boundaryY=(len(mapList)-1)
    boundaryX=(len(mapList[y])-1)

    if((mapList[y][x]==0) and (mapList[y+1][x]==0) and (mapList[y][x+1]==0) and (mapList[y+1][x+1]==0)):
        renderFlag=False

    if((y>1) and (x>1) and (y<boundaryY) and (x<boundaryX)):
        mapList[y][x]=pen

        if((y+1)<boundaryY):
            mapList[y+1][x]=pen
            #diagonal so i cant reuse the check
            if((x+1)<((len(mapList[y+1])-1))):
                mapList[y+1][x+1]=pen

        if(((x+1)<boundaryX)):
            mapList[y][x+1]=pen

    if(renderFlag):
        renderMapList(mapList,uiHeader)

    return mapList


def fixMap(mapList, goodCoords):
    allCoords=[]
    for y in range(len(mapList)):
        for x in range(len(mapList[0])):
            allCoords.append((y,x))
    goodCoordsSet=set(goodCoords)


    badCoords=[]


    for coord in allCoords:
        if((not(coord in goodCoordsSet))and(mapList[coord[0]][coord[1]]==0)):
            badCoords.append(coord)


    demoCopy=duplicateMapList(mapList)

    zones=[goodCoords,]
    foundZones=1
    while(len(badCoords)>0):
        foundZones+=1
        found=floodFillGrouper(demoCopy,badCoords[len(badCoords)-1],foundZones)
        foundSet=set(found)
        newBad=[]
        for item in badCoords:
            if(not(item in foundSet)):
                newBad.append(item)
        badCoords=newBad

        zones.append(found)

    longestZoneIndex=0
    clear()
    print("finding longest zone")
    for index,zone in enumerate(zones):
        print("\nchecking zone "+str(index)+" against "+str(longestZoneIndex))
        if(len(zone)>len(zones[longestZoneIndex])):
            print("zone "+str(index)+" is the new longest zone!")
            longestZoneIndex=index
        time.sleep(0.5)

    print("zone "+str(longestZoneIndex)+" is the overall longest zone.")
    input("press enter to continue")

    longestZone:list=zones[longestZoneIndex]

    zones.remove(longestZone)

    for index,zone in enumerate(zones):
        bestEndPoint=findShortestDistanceCoord(longestZone,zone[random.randint(0,len(zone)-1)],mapList,0,index+1,len(zones))
        bestStartPoint=findShortestDistanceCoord(zone,bestEndPoint,mapList,1,index+1,len(zones))

        repair=bresenham(bestStartPoint[1],bestStartPoint[0],bestEndPoint[1],bestEndPoint[0])
        longestZone.extend(zone)
        longestZone.extend(repair)
        for point in repair:
            mapList[point[0]][point[1]]=0
            renderMapList(mapList,"cutting repair path for error "+str(index+1)+" of "+str(len(zones)))


    renderMapList(mapList,"map repairs complete.")

















def generatemapList(w,h,paths,trees, seeds):

    mapList=[]

    start=time.time()

    clear()
    print("creating forest...")
    for i in range(h):
        collum=[]
        for j in range(w):
            collum.append(1)
        mapList.append(collum)
        renderMapList(mapList,"now generating starting forest")

    print("done!")
    renderMapList(mapList,"starting forest:")
    print("seeding clearings...")
    pathSeeds=[]

    if(True):
        shadowmapList=[]
        for i in range(h):
            collum=[]
            for j in range(w):
                collum.append(1)
            shadowmapList.append(collum)

        for path in range(paths):
            x=random.randint(2,w-2)
            y=random.randint(2,h-2)
            pathSeeds.append((y,x))
            shadowmapList[y][x]=3
            renderMapList(shadowmapList,"seeding paths. now generating path seed "+str(path)+" out of "+str(paths))
    print("done!")
    clear()
    #y1-y2/x1-x2
    print("calculating paths...")
    pathPoints=[]
    if(True):
        shadowmapList=[]
        pathTuples=[]
        for i in range(h):
            collum=[]
            for j in range(w):
                collum.append(1)
            shadowmapList.append(collum)
        pathcount=1
        for path1 in pathSeeds:
            shadowPoints=[]
            for path2 in pathSeeds:
                if(path2!=path1 and (path2,path1) not in pathTuples):
                    pathTuples.append((path1,path2))

                    posiblePathPoints=bresenham(path1[1], path1[0], path2[1], path2[0])

                    for point in posiblePathPoints:
                        if(point in pathPoints):
                            posiblePathPoints.remove(point)
                        elif((point[0]<1)or(point[0]>(h-2))or(point[1]<1)or(point[1]>(w-2))):
                            posiblePathPoints.remove(point)


                    pathPoints+=posiblePathPoints
                    shadowPoints=bresenham(path1[1], path1[0], path2[1], path2[0])



                    for point in shadowPoints:
                        shadowmapList[point[0]][point[1]]=3


                    renderMapList(shadowmapList,"calculating paths. now calculating path "+str(pathcount)+" out of "+str(len(pathSeeds)*len(pathSeeds)))
                    pathcount+=1



    clear()

    print("cutting paths...")
    state=False
    sectionCount=0
    for index,point in enumerate(pathPoints):
        sectionCount+=1
        if(index%10==0):
            if(random.randint(0,100)>65):
                state=True
            else:
                state=False
        if(state):
            mapList=squarePlot(mapList,point[0],point[1], 0,"now cutting paths. cutting path block "+str(sectionCount)+" out of "+str(len(pathPoints)))
        else:
            if(mapList[point[0]][point[1]]!=0):
                mapList[point[0]][point[1]]=0
                renderMapList(mapList,"now cutting paths. cutting path block "+str(sectionCount)+" out of "+str(len(pathPoints)))




    clear()

    print("planting trees...")
    localTrees=trees
    while (localTrees > 0):
        treeX=random.randint(1,w-2)
        treeY=random.randint(1,h-2)

        if(mapList[treeY][treeX]==0):
            mapList[treeY][treeX]=1
            renderMapList(mapList,"planting trees. now planting tree "+str(trees-localTrees)+" out of "+str(trees))
            localTrees-=1

    clear()

    print("counting whitespaces...")
    totalWhiteSpace=0
    for y in range(len(mapList)):
        for x in range(len(mapList[0])):
            if(mapList[y][x]==0):
                totalWhiteSpace+=1


    clear()
    goodmapList=floodFillCheck(duplicateMapList(mapList),totalWhiteSpace)

    if(goodmapList[0]):
        print("map is good, continuing to food scattering and owl placement")
        goodmapList=goodmapList[0]
    else:
        print("map is bad, starting repair process")
        fixMap(mapList,goodmapList[1])
        goodmapList=goodmapList[0]
    input("press enter to continue")
    clear()
    print("scattering seeds...")
    localSeeds=seeds
    while (seeds > 0):
        seedX=random.randint(1,w-2)
        seedY=random.randint(1,h-2)

        if(mapList[seedY][seedX]==0):
            mapList[seedY][seedX]=5
            renderMapList(mapList,"scattering food. placing seed "+str(localSeeds-seeds)+" out of "+str(localSeeds))
            seeds-=1
    print("done!")

    print("placing owl...")
    while True:
        x=random.randint(1,len(mapList[0])-1)
        y=random.randint(1,len(mapList)-1)
        if(mapList[y][x]==0):
            dir=random.randint(0,3)
            mapList[y][x]=4
            break

    print("done!")
    clear()
    renderMapList(mapList,"final map:")
    input("press enter to finish the demo")









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









def mainMenu():
    global MAPWIDTH
    global MAPHEIGHT
    global PATHS
    global TREES
    global SEEDS
    global OWLPIC
    tkinter_renderer.initTkinterWindow(MAPWIDTH,MAPHEIGHT,16,"ookpik map generation engine tech demo v2.0")
    while True:
        userInput=multipleChoiceScreen("ookpik map generation engine tech demo v2.0"+"\n\n"+OWLPIC,("(s)tart generation","(q)uit"),("s","q","e"),1)

        if(userInput==1):
            mapListSizeCheck=multipleChoiceScreen("please select the map size to generate",("(b)ig map","(s)mall map"),("b","s"),1)
            clear()

            print("starting generation...")
            ln()


            mapListSize=(mapListSizeCheck==1)

            mapList=generatemapList(MAPWIDTH, MAPHEIGHT, PATHS[mapListSize], TREES[mapListSize], SEEDS[mapListSize])



        elif(userInput>1):
            clear()
            print("thank you for runnign ookpik map generation engine tech demo v2.0")
            break

mainMenu()

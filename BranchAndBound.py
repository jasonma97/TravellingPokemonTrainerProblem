import kmlPokeDict
import minDist
import itertools
import geneticAlgorithmTSP
from random import sample, randint
import sys

FILENAME = 'pokestopdata2.txt'

MAX_VISITS = [0,1,2]
MERGE_DISTANCE = 400 / 112000
class PokeStop:
    def __init__(self, pokeID, name, loc):
        self.name = name
        self.pokeID = pokeID
        self.loc = loc[0:2]

    def __repr__(self):
        return   self.name 

    def closestNStops( self, N, pokeList, excludeList = []):
        closestStops = []
        farthestStop = 0
        for a0 in range(len(pokeList)):
            if pokeList[a0] == self or pokeList[a0] in excludeList:
                continue
            closestStops.append(pokeList[a0])
            if len(closestStops) > N:
                closestStops = sorted(closestStops, key = lambda stop: self.distanceToStop(stop))
                closestStops = closestStops[:N]
        return closestStops
                

    def distanceToStop(self, other):
        return getDistanceBetweenPokeStops(self, other)

class Trainer:
    def __init__(self, speed = 3):
        self.pathTaken = []
        self.unavailablePokeStops = []
        self.walkingSpeed = speed
        self.distanceWalked = 0.0
        self.fitness = 0.0

    def __repr__(self):
        string = '{'
        string += ''.join([stop.name + ', ' for stop in self.pathTaken])
        if len(string) > 1:
            string = string[:-2]
        string += '}'
        return string

    def updatePath(self, newPath):
        if len(newPath) <= 1:
            raise Exception("This is an empty path, you can't update to an empty path")
            return
        self.pathTaken = newPath
        self.unavailablePokeStops = newPath
        self.distanceWalked = self.calcTrainerPathLength(newPath)
        self.getFitness()


    def calcTrainerPathLength(self, pathL):
        totalDistance = 0
        for stop in range(len(pathL) - 1):
            totalDistance += ((pathL[stop].loc[0] - pathL[stop + 1].loc[0])**2 + (pathL[stop].loc[1] - pathL[stop + 1].loc[1])**2)**0.5
        return totalDistance * 112

    def updateDistanceWalked(self):
        return distanceWalked

    def getCurrentCity(self):
        return pathTaken[-1]

    def getUnweightedFitness(self):
        return len(self.pathTaken) / self.distanceWalked

    def getFitness(self):
        #print()
        #print(self.fitness)
        #print(self.pathTaken)
        #self.fitness = (len(self.pathTaken)) / self.distanceWalked #* (len(self.pathTaken) - 3)/len(self.pathTaken)
        self.fitness = (len(self.pathTaken) + 1)/ (self.distanceWalked + getDistanceBetweenPokeStops(self.pathTaken[0], self.pathTaken[-1]))
        self.fitness *= (len(self.pathTaken) - 2)/len(self.pathTaken)
        return self.fitness

    def distanceWalked(self):
        distance = 0
        for stop in range(len(self.pathTaken)):
            if stop == len(self.pathTaken):
                distance += distanceBetweenPoints(self.pathTaken[-1].loc, self.pathTaken[0])
            else:
                distance += distanceBetweenPoints(self.pathTaken[stop].loc, self.pathTaken[stop + 1].loc)
        return distance 

    def timeToTraverse(self):
        return self.distanceWalked/self.speed


def getDict():
    file = open(FILENAME, 'r')
    string = file.read()
    string = string.replace('{', ',')
    string = string.replace('\n', ',')
    string= string.split(',')
    string = [thing for thing in string if thing != '']
    #print(string)
    file.close
    pokeDict = {}
    for ind in range(0, len(string), 3):
        pokeDict[string[ind]] = (float(string[ind + 2]),float(string[ind + 1]),0.0)
    #print(pokeDict)
    KMLDict= kmlPokeDict.getKMLStops()
    #print(KMLDict)
    return KMLDict, pokeDict

def getDistanceBetweenPokeStops(startPoint, endPoint):
    return ((startPoint.loc[0] - endPoint.loc[0])**2 + (startPoint.loc[1] - endPoint.loc[1])**2)**0.5 

def getPathLength(pathList):
    totalDistance = 0
    for stopNumber in range(len(pathList) - 1):
        totalDistance+= getDistanceBetweenPokeStops( pathList[stopNumber], pathList[stopNumber + 1])
    return totalDistance

def mergeStops(pokeList):
    newL = pokeList[:]
    counter= 0
    while(True):
        newL2 = []
        usedStops = []
        changesMade = False
        for stop1 in newL:
            stopUsed = False
            for stop2 in newL:
                if stop1 != stop2:
                    if getDistanceBetweenPokeStops(stop1, stop2) < 0.0004 and stop1 not in usedStops and stop2 not in usedStops:
                        newStop = averageStopLocation(stop1, stop2)
                        changesMade = True
                        stopUsed = True
                        newL2.append(newStop)
                        usedStops.append(stop1)
                        usedStops.append(stop2)
                        #print(stop1)
                        #print(stop2)
                        counter+=1
            if not stopUsed and stop1 not in usedStops:
                newL2.append(stop1)
                usedStops.append(stop1)
        if not changesMade:
            return newL2
            break
        newL = newL2[:]
    return newL

def inEdges( edgeL, stop ):
    counter = 0
    for edge in edgeL:
        if stop == edge[0]:
            #print("hello")
            counter += 1
        if stop == edge[1]:
            #print("world")
            counter += 1
    return counter

def calcLowerBound(pokeList):
    totalD = 0
    for stop in pokeList:
        closestTwoStops = stop.closestNStops( 2, pokeList)
        for closeStop in closestTwoStops:
            totalD += getDistanceBetweenPokeStops( closeStop, stop )
    return totalD/2

def calcLowerBoundWithDefaultEdges(pokeList, usedEdges = [], excludedEdges = [] ):
    totalD = 0
    n = 2
    #counter = 0 
    for stop in pokeList:
        n = 2 - inEdges(usedEdges, stop)
        if n < 0:
            n = 0
        closestTwoStops = stop.closestNStops( n, pokeList, usedEdges + excludedEdges)
        for closeStop in closestTwoStops:
            #counter += 1
            totalD += getDistanceBetweenPokeStops( closeStop, stop )
    #print(usedEdges)
    #print(counter)
    for edge in usedEdges:
        #print(edge)
        totalD += 2 * getDistanceBetweenPokeStops( edge[0], edge[1])
    return totalD/2

def getAllEdges(pokeList):
    return [[stop1, stop2] for stop1 in pokeList for stop2 in pokeList if stop1 != stop2]


def filterEdgeL(pokeList, edgeL, inPathL, viewL):
    pokestopCounter = {}
    availableEdgeL = []
    edgesLeft = {}
    leftOverEdges = [edge for edge in edgeL if edge not in inPathL]

    for stop in pokeList:
        pokestopCounter[stop] = 0
    for edge in inPathL:
        pokestopCounter[edge[0]] += 1
        pokestopCounter[edge[1]] += 1
    for edge in edgeL:
        #Note MAX_VISITS = [0,1,2]. This tests to see if the number of times each node has been visited is less than 2, but greater than 0
        if (pokestopCounter[edge[0]] in MAX_VISITS or pokestopCounter[edge[1]] in MAX_VISITS) and edge not in viewL:
            availableEdgeL.append(edge)
    return availableEdgeL

def getNeighborStops( edgeL, stop ):
    neighborL = []
    for edge in edgeL:
        if edge[0] == stop and edge[1] not in neighborL:
            neighborL.append(edge[1])
        if edge[1] == stop and edge[0] not in neighborL:
            neighborL.append(edge[0])
    return neighborL

def branchAndBound(pokeList, edgeL, analyzedL = [], useL = [], minimumDist = None):
    lowBound = calcLowerBound(pokeList)
    #useL = [0 for stop in pokeList]
    chosenEdge = sample(edgeL, 1)[0]
    #print(lowBound)
    lowerBoundWithEdge = calcLowerBoundWithDefaultEdges(pokeList, [chosenEdge], [])
    lowerBoundWithoutEdge = calcLowerBoundWithDefaultEdges(pokeList, [], [chosenEdge])

    #print(lowerBoundWithEdge)
    #print(lowerBoundWithoutEdge)

    if lowerBoundWithEdge <= lowerBoundWithoutEdge:
        #print("Used withEdge")
        WEdgeL = branchAndBoundHelper(pokeList, edgeL, None, [chosenEdge], [chosenEdge])
        WOEdgeL = branchAndBoundHelper(pokeList, edgeL, getPathLength(generatePath(WEdgeL)), [chosenEdge], [])
    else:
        #print("Use withoutEdge")
        WOEdgeL = branchAndBoundHelper(pokeList, edgeL, None, [chosenEdge], [])
        WEdgeL = branchAndBoundHelper(pokeList, edgeL, getPathLength(generatePath(WOEdgeL)), [chosenEdge], [chosenEdge])
    WOPath = generatePath(WOEdgeL)
    WPath = generatePath(WEdgeL)
    if getPathLength(WPath) <= getPathLength(WOPath):
        return WPath, WOPath
    else:
        return WOPath, WPath

def branchAndBoundHelper(pokeList, edgeL, minimumDist = None, viewedL = [], inPathL = [], depth = []):
    #print(inPathL)
    depth += [1]
    if len(inPathL) == len(pokeList):
        return inPathL
    print(len(depth))
    #print("Path:")
    #print(inPathL)
    availableEdgeL = filterEdgeL(pokeList, edgeL, inPathL, viewedL)
    #print("Available Edges:" + str(len(availableEdgeL)))
    #print(availableEdgeL)
    
    if availableEdgeL == []:
        #print(inPathL)
        #print(viewedL)
        if inPathL == []:
            return viewedL
        return inPathL 
    chosenEdge = sample(availableEdgeL, 1)[0]
    withOutEdge = inPathL[:]
    withEdge = inPathL[:]
    withEdge.append(chosenEdge)
    viewedL.append(chosenEdge)
    hasLeftOver = False
    #print(withEdge)
    #print(withoutEdgeL)
    lowerBoundWithEdge = calcLowerBoundWithDefaultEdges(pokeList, withEdge, [edge for edge in viewedL if edge not in withEdge])
    lowerBoundWithoutEdge = calcLowerBoundWithDefaultEdges(pokeList, withOutEdge, [edge for edge in viewedL if edge not in withOutEdge])
    if minimumDist != None and lowerBoundWithoutEdge > minimumDist:
        lowerBoundWithoutEdge = lowerBoundWithEdge
    if lowerBoundWithEdge <= lowerBoundWithoutEdge:
        withEdgeL = branchAndBoundHelper(pokeList, edgeL, minimumDist, viewedL, withEdge)
        pathWithEdge = generatePath(withEdgeL)
        if minimumDist == None:
            withoutEdgeL = branchAndBoundHelper(pokeList, edgeL, getPathLength(pathWithEdge), viewedL, withOutEdge)
            #print(withoutEdgeL)
            pathWithoutEdge = generatePath(withoutEdgeL)
        elif minimumDist > getPathLength(pathWithEdge):
            withoutEdgeL = branchAndBoundHelper(pokeList, edgeL, getPathLength(pathWithEdge), viewedL, withOutEdge)
            #rint(withoutEdgeL)
            pathWithoutEdge = generatePath(withoutEdgeL)
        else:
            withoutEdgeL = branchAndBoundHelper(pokeList, edgeL, minimumDist, viewedL, withOutEdge)
            #print(withoutEdgeL)
            pathWithoutEdge = generatePath(withoutEdgeL)
    else:
        withoutEdgeL = branchAndBoundHelper(pokeList, edgeL, minimumDist, viewedL, withOutEdge)
        #print("Without")
        #print(withoutEdgeL)
        pathWithoutEdge = generatePath(withoutEdgeL)
        if minimumDist == None:
            #print(pathWithoutEdge)
            withEdgeL = branchAndBoundHelper(pokeList, edgeL, getPathLength(pathWithoutEdge), viewedL, withEdge)
            pathWithEdge = generatePath(withEdgeL)
        elif minimumDist > getPathLength(pathWithoutEdge):
            withEdgeL = branchAndBoundHelper(pokeList, edgeL, getPathLength(pathWithoutEdge), viewedL, withEdge)
            pathWithEdge = generatePath(withEdgeL)
        else:
            withEdgeL = branchAndBoundHelper(pokeList, edgeL, minimumDist, viewedL, withEdge)
            pathWithEdge = generatePath(withEdgeL)

    #print(withEdgeL)
    #print(withoutEdgeL)
    if pathWithEdge == []:
        if pathWithoutEdge == []:
            return viewedL
        return printWithoutEdge
    elif pathWithoutEdge == []:
        if pathWithEdge == []:
            return viewedL
        return pathWithEdge
    if getPathLength(pathWithEdge) < getPathLength(pathWithoutEdge):
        return withEdgeL
    elif getPathLength(pathWithEdge) > getPathLength(pathWithoutEdge):
        return withoutEdgeL
    else:
        return withEdgeL
    



def generatePath(edgeL):
    #print(edgeL)
    ########################################################################################################################
    #This is for path construction after everything is finished running
    ########################################################################################################################
    #print("EdgeL: ")
    #print(edgeL)
    if edgeL == []:
        return []
    path = [edgeL[0][0]]
    edgeUsed = []
    while(True):
        changesMade = False
        for edge in edgeL:
            if edge[0] == path[-1] and edge[1] not in path and edge not in edgeUsed:
                path.append(edge[1])
                changesMade = True
                edgeUsed.append(edge)
            elif edge[1] == path[-1] and edge[0] not in path and edge not in edgeUsed:
                path.append(edge[0])
                changesMade = True
                edgeUsed.append(edge)
            elif edge[0] == path[0] and edge[1] not in path and edge not in edgeUsed:
                path = [edge[1]] + path
                changesMade = True
                edgeUsed.append(edge)
            elif edge[1]  == path[0] and edge[0] not in path and edge not in edgeUsed:
                path = [edge[0]] + path
                changesMade = True
                edgeUsed.append(edge)
        if not changesMade:
            break
    #print(path)
    #print(withEdge)
    
    #print("Path: ")
    #print(path)
    return path



def main():
    sys.setrecursionlimit(10000)
    KMLDict, pokeDict = getDict()
    pokeList = [PokeStop(elem, key, KMLDict[key]) for key in KMLDict.keys() for elem in pokeDict.keys() if pokeDict[elem] == KMLDict[key]]
    #pokeList = filterList("Mudd", pokeList)

    #print(len(pokeList))
    #pokeList = mergeStops(pokeList)
    pokeList = []
    for a0 in range(10):
        pokeList.append(PokeStop(str(a0) * 3, str(a0), [randint(0,10), randint(0,10)]))
    #print(pokeList)
    path = branchAndBound(pokeList, getAllEdges(pokeList))
    print(path)
    #print(getPathLength(pokeList))


def filterList( schoolName, pokeList):
    if schoolName == 'Mudd':
        return [pokestop for pokestop in pokeList if (pokestop.loc[1] > 34.10540 and pokestop.loc[0] > -117.71325)]
    elif schoolName == 'Scripps':
        return [pokestop for pokestop in pokeList if (pokestop.loc[1] < 34.10540 and pokestop.loc[0] < -117.70830 and pokestop.loc[1] > 34.10260 and pokestop.loc[0] > -117.71150)]
    elif schoolName == "Pitzer":
        return [pokestop for pokestop in pokeList if (pokestop.loc[1] > 34.1025 and pokestop.loc[1] < 34.10518 and pokestop.loc[0] > -117.70730 and pokestop.loc[0] < -117.7040)]
    elif schoolName == "Pomona":
        return [pokestop for pokestop in pokeList if (pokestop.loc[0] > -117.71500 and pokestop.loc[0] < -117.70700 and pokestop.loc[1] < 34.09983) \
                or (pokestop.loc[0] > -117.71640 and pokestop.loc[0] < -117.7096 and pokestop.loc[1] > 34.0977 and pokestop.loc[1] < 34.10137) \
                or (pokestop.loc[0] > -117.71355 and pokestop.loc[0] < -117.7116 and pokestop.loc[1] > 34.10136 and pokestop.loc[1] < 34.10248)]
    elif schoolName == "CMC":
        return [pokeStop for pokeStop in pokeList if (pokeStop.loc[1] < 34.10257 and pokeStop.loc[1] > 34.09964 and pokeStop.loc[0] < -117.70712 and pokeStop.loc[0] > -117.70929) or \
            (pokeStop.loc[1] > 34.10138 and pokeStop.loc[1] < 34.10266 and pokeStop.loc[0] > -117.71305 and pokeStop.loc[0] < -117.70696)]
    elif schoolName == "Village":
        return [pokestop for pokestop in pokeList if (pokestop.loc[1] < 34.09695 and pokestop.loc[0] < -117.71552)]
    else:
        return []

if __name__ == '__main__':
    main()
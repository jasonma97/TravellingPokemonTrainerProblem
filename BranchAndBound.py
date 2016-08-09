import kmlPokeDict
import minDist
import itertools
import geneticAlgorithmTSP
from random import sample

FILENAME = 'pokestopdata2.txt'

class PokeStop:
    def __init__(self, pokeID, name, loc):
        self.name = name
        self.pokeID = pokeID
        self.loc = loc[0:2]

    def __repr__(self):
        return   self.name + ':' +  str(self.loc)

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

def getDistanceDictionary(pokeList):
    listOfCoors = [(stop.loc[0], stop.loc[1], stop.name) for stop in pokeList]
    distDict = {}
    refDict= {}
    for i in range(len(listOfCoors)):
        for j in range(len(listOfCoors)):
            if i != j:
                distDict[(listOfCoors[i][2], listOfCoors[j][2])] = distanceBetweenPoints(listOfCoors[i], listOfCoors[j])
                distDict[(listOfCoors[j][2], listOfCoors[i][2])] = distanceBetweenPoints(listOfCoors[i], listOfCoors[j])
                refDict[i] = listOfCoors[i][2]
                refDict[j] = listOfCoors[j][2]
            else:
                distDict[(listOfCoors[i][2],listOfCoors[j][2])] = 100000
    return distDict, refDict

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

def calcLowerBound(pokeList):
    totalD = 0
    for stop in pokeList:
        closestTwoStops = stop.closestNStops( 2, pokeList)
        for closeStop in closestTwoStops:
            totalD += getDistanceBetweenPokeStops( closeStop, stop )
    return totalD/2

def involvedInList( edgeL, stop ):
    if lst == None:
        return False
    else:
        for edge in edgeL:
            if edge[0] == stop or edge[1] == stop:
                return True
        return False

def calcLowerBoundWithDefaultEdges(pokeList, usedEdges = [], excludedEdges = [] ):
    totalD = 0
    for stop in pokeList:
        closestTwoStops = stop.closestNStops( n, pokeList, usedEdges + excludedEdges)
        for closeStop in closestTwoStops:
            totalD += getDistanceBetweenPokeStops( closeStop, stop )
    for edge in usedEdges:
        totalD += 2 * getDistanceBetweenPokeStops( edge[0], edge[1])
    return totalD/2

def getAllEdges(pokeList):
    return [[stop1, stop2] for stop1 in pokeList for stop2 in pokeList if stop1 != stop2]

def branchAndBound(pokeList, edgeL, pokestopUsedCounter, analyzedL = [], useL = []):
    if len(usedL) == len(pokeList):
        return usedL
    print(calcLowerBound(pokeList))
    lowBound = calcLowerBound(pokeList)
    usedL = [0 for stop in pokeList]
    while(True):
        chosenEdge = sample(edgeL, 1)
        if chosenEdge not in analyzedL:
            break
    withEdge = usedL[:]
    withEdge.append(chosenEdge)
    newLowBound = calcLowerBoundWithDefaultEdges(pokeList, withEdge, [])
    otherNewLowBound = calcLowerBoundWithDefaultEdges(pokeList, useL, chosenEdge)
    return

def main():
    KMLDict, pokeDict = getDict()
    pokeList = [PokeStop(elem, key, KMLDict[key]) for key in KMLDict.keys() for elem in pokeDict.keys() if pokeDict[elem] == KMLDict[key]]
    #pokeList = filterList("Mudd", pokeList)

    #print(len(pokeList))
    #pokeList = mergeStops(pokeList)
    pokestopUsedCounter = {}
    for stop in pokeList:
        pokestopUsedCounter[stop] = 0
    path = branchAndBound(pokeList, getAllEdges(pokeList), pokestopUsedCounter)
    print(getPathLength(pokeList))


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
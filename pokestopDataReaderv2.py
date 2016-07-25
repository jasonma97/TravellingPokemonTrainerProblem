import kmlPokeDict
import minDist
import math
from random import *
from time import *
import itertools

FILENAME = 'pokestopdata2.txt'
class PokeStop:
    def __init__(self, pokeID, name, loc):
        self.name = name
        self.pokeID = pokeID
        self.loc = loc
    def __repr__(self):
        return "I am called '" + self.name + "' and I am located at " + str(self.loc)

class Trainer:
    def __init__(self, speed = 3):
        self.pathTaken = []
        self.pokeStopsVisited = []
        self.unavailablePokeStops = []
        self.walkingSpeed = speed
        self.distanceWalked = 0

    def updateDistanceWalked():
        return distanceWalked

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
        pokeDict[string[ind]] = (float(string[ind + 1]),float(string[ind + 2]),0.0)
    #print(pokeDict)
    KMLDict= kmlPokeDict.getKMLStops()
    return KMLDict, pokeDict

def getDistance(startPoint, endPoint, dictionary):
    return ((startPoint[0] - endPoint[0])**2 + (startPoint[1] - endPoint[1])**2)**0.5

def getDistDict( pokeDict ):
    distDict = {}
    for start in pokeDict.keys():
        for end in pokeDict.keys():
            if start != end and (start,end) not in distDict.keys():
                dist = getDistance(pokeDict[start], pokeDict[end], pokeDict)
                distDict[(start,end)] = dist
                distDict[(end,start)] = dist
    return distDict

def distanceBetweenPoints(point1, point2):
    return ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)**0.5

def getDistanceDictionary(pokeList):
    listOfCoors = [(stop.loc[0], stop.loc[1]) for stop in pokeList]

    distDict = {}
    for i in range(len(listOfCoors)):
        for j in range(len(listOfCoors)):
            if i != j:
                if (i,j) not in distDict.keys():
                    distDict[(i,j)] = distanceBetweenPoints(listOfCoors[i], listOfCoors[j])
            else:
                distDict[(i,j)] = None

    refDict = []
    for coor in range(len(listOfCoors)):
        for elem in pokeList:
            if listOfCoors == (elem.loc[0],elem.loc[1]):
                refDict[coor] = elem
    return distDict, refDict

def getPathLength(distDict, pathList):
    totalDistance = 0
    for stopNumber in range(len(pathList) - 1):
        totalDistance+= distDict[pathList[stopNumber], pathList[stopNumber + 1]]
    return totalDistance

def allPathGenerator( numOfStops ):
    return itertools.chain(*map(lambda x: itertools.combinations(numOfStops, x), range(0, len(numOfStops) + 1)))

def bruteForce(distDict, pokeList):
    highestEfficiency = 0
    bestPath = []
    bestPathDict = {}
    dictIndex = 0
    counter = 0
    allCombinations = allPathGenerator( list( range( len(pokeList) ) ) )
    excludablePaths = 10
    #max(int(float(len(pokeList))  * 0.1), 1)
    for combination in allCombinations:
        pathList = list(combination)
        #print(len(pathList))
        if len(pathList) > excludablePaths:
            currentPathDistance = getPathLength(distDict, pathList)
            efficiency = float(len(pathList)) / currentPathDistance
            #print(efficiency)
            #print(efficiency > highestEfficiency)
            if efficiency > highestEfficiency:
                print("New Best Path = " + str(dictIndex))
                print("Efficiency: " + str(efficiency / 100))
                print("Length of Path = " + str(currentPathDistance))
                print("Number of Stops = " + str(len(pathList)))
                print("Path = " + str(pathList))
                print(counter)
                print()

                highestEfficiency = efficiency
                bestPath = pathList
                bestPathDict[dictIndex] = (pathList, efficiency)
                dictIndex+=1
        print(counter)
        counter += 1
    return bestPath

        


def main():
    KMLDict, pokeDict = getDict()
    pokeList = [PokeStop(elem, key, KMLDict[key]) for key in KMLDict.keys() for elem in pokeDict.keys() if pokeDict[elem] == KMLDict[key]]
    pokeList = pokeList[:30]

    distDict, referenceDict = getDistanceDictionary(pokeList)
    #sol1 = bruteForce(distDict, pokeList)
    #print(sol1)

    # file = open('output.txt', 'w')

    # # for elem in pokeList:
    # #     file.write((str((elem.loc[0])) + ',' + str(-1 *(elem.loc[1])) + '\n'))
    # # file.close()
 
def getNamedPath(pathList, pokeList):
    namedPath = []
    for stop in pathList:
        foundName = False
        for name in pokeList:
            # print(stop[0])
            # print(name.loc[0])
            # print(stop[1])
            # print(name.loc[1])
            if stop[0] == name.loc[0] and stop[1] == -1 * name.loc[1]:
                namedPath.append(name.name)
                foundName = True
        #print(foundName)
        if not foundName:
            print(stop)
            raise Exception("Yo this pokestop isn't in our list. Get a new path")
    return namedPath

if __name__ == '__main__':
    main()
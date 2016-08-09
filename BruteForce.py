
import kmlPokeDict
import minDist
from math import *
from random import *
from time import *
import itertools
import geneticAlgorithmTSP
from pokestopDataReaderv2 import *

def main():
    """Runs the brute force method of finding the optimal path if this file is run as master"""
    #getDict is imported from pokeStopDataReaderv2
    KMLDict, pokeDict = getDict()
    pokeList = [PokeStop(elem, key, KMLDict[key]) for key in KMLDict.keys() for elem in pokeDict.keys() if pokeDict[elem] == KMLDict[key]]
    
    #Both function calls below are from pokestopDataReaderv2
    pokeList = filterList("Mudd", pokeList)
    pokeList = mergeStops(pokeList)
    #path = bruteForce(pokeList, 15)

    listOfCoors = [[stop.loc[0],stop.loc[1]] for stop in pokeList]
    path = minDist.travelling_salesman(listOfCoors)
    #Also imported from pokeStopDataReaderv2
    path = getNamedPath(path, pokeList)
    print(path)
    kmlPokeDict.writeKMLFile('OptimalMuddPath.kml', path)

# This is a brute force method
# DO NOT TOUCH
def allPathGenerator( numOfStops ):
    """Returns a generator of all possible combination of numbers from 0 to numOfStops"""
    return itertools.chain(*map(lambda x: itertools.combinations(numOfStops, x), range(0, len(numOfStops) + 1)))

def bruteForce( pokeList, pathSize = None):
    """Accepts a list of pokestop objects and a minimum pathSize int
        Uses a generator to generate every combination of pokeStops to
        test to see which is the most efficient grouping of stops. 
        Returns the path with the best efficiency
        """
    highestEfficiency = 0
    bestPath = []
    bestPathDict = {}
    dictIndex = 0
    counter = 0
    allCombinations = allPathGenerator( list( range( len(pokeList) ) ) )
    if pathSize == None:
        excludablePaths = 2
    else:
        excludablePaths = pathSize - 1
    #max(int(float(len(pokeList))  * 0.1), 1)
    for combination in allCombinations:
        pathList = list(combination)
        #print(pathList)
        #print(len(pathList))
        if len(pathList) > excludablePaths:
            newPath = []
            for fill in pathList:
                newPath.append(pokeList[fill])
            currentPathDistance = getPathLength( newPath )
            efficiency = float(len(pathList) + 1) / (currentPathDistance + getDistanceBetweenPokeStops(newPath[0], newPath[-1]))
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
                bestPath = newPath
                bestPathDict[dictIndex] = (pathList, efficiency)
                dictIndex+=1
        #print(counter)
        counter += 1
    #print(len(bestPath))
    return bestPath


if __name__ == '__main__':
    main()
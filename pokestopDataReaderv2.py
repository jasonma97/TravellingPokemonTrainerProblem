import kmlPokeDict
import minDist
from math import *
from random import *
from time import *
import itertools
import geneticAlgorithmTSP

FILENAME = 'pokestopdata2.txt'
MAXPOKESTOPS = 20
#A path length of 1 is staying put
#I'm not counting paths of length 1
MINPATHLENGTH = 2
#Needed to find the most optimal subsections of paths
#Set limit, so we don't try anything above 10!, we brute force it (yea I know it's bad)
SUBPATHLIMIT = 10
CHARACTERISTICLENGTH = 4
class PokeStop:
    def __init__(self, pokeID, name, loc):
        self.name = name
        self.pokeID = pokeID
        self.loc = loc[0:2]

    def __repr__(self):
        return   self.name + ':' +  str(self.loc)

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

    def highestScoringSubset(self):
        bestPath = bruteForce( self.pathTaken )
        return bestPath

    def calcTrainerPathLength(self, pathL):
        totalDistance = 0
        for stop in range(len(pathL) - 1):
            totalDistance += ((pathL[stop].loc[0] - pathL[stop + 1].loc[0])**2 + (pathL[stop].loc[1] - pathL[stop + 1].loc[1])**2)**0.5
        return totalDistance * 112

    def updateDistanceWalked(self):
        return distanceWalked

    def optimizeCurrentPath(self):
        self.updatePath(optimizePath(self.pathTaken))

    def getCurrentCity(self):
        return pathTaken[-1]

    def getUnweightedFitness(self):
        return len(self.pathTaken) / self.distanceWalked

    def getFitness(self):
        #print()
        #print(self.fitness)
        #print(self.pathTaken)
        self.fitness = (len(self.pathTaken) + 1)/ (self.distanceWalked + getDistanceBetweenPokeStops(self.pathTaken[0], self.pathTaken[-1])) * ((len(self.pathTaken) - MINPATHLENGTH) / len(self.pathTaken))
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

class Generation:
    def __init__(self, genSize = 50, mutProb = 0.05, trainerL = None, keep = 0, matingProb = 0, pokeList = [], distDict = None):
        if not trainerL:
            self.trainerL = [Trainer() for a0 in range(genSize)]
        else:
            self.trainerL = trainerL
        self.genSize = genSize
        self.mutProb = mutProb
        self.individualsToKeep = keep
        self.matingProb = matingProb
        self.pokeList = pokeList
        self.distDict = distDict

    def nextGen(self):
        nextGenL = self.bestTrainers()[:self.individualsToKeep]
        remainingTrainers = [trainer for trainer in self.trainerL if trainer not in nextGenL]
        for ind in range(len(remainingTrainers)):
            nextGenL.append(self.mutateTrainer(remainingTrainers[ind]))
        return nextGenL

    def bestTrainers(self):
        sortedTrainerL = sorted(self.trainerL, key = lambda trainer: trainer.fitness)
        return sortedTrainerL[-self.individualsToKeep:]

    def evolveGen(self):
        self.trainerL = self.nextGen()
        self.cull()

    def mutateTrainer(self, trainer):
        seed(time())
        newPath = []
        for stop in range(len(trainer.pathTaken)):
            if random() < self.mutProb and len(newPath) > 1:
                stopNotFound  = True
                while(stopNotFound):
                    nextStops = sample(self.pokeList, 5)
                    nextStops = [thing for thing in nextStops if thing not in newPath for a0 in range(int(1/getDistanceBetweenPokeStops(thing, newPath[-1]))) ]
                    if len(nextStops) > 0:
                        newStop = choice(nextStops) 
                        if newStop not in trainer.pathTaken and newStop not in newPath:
                            newPath.append(newStop)
                            stopNotFound = False
            else:
                if trainer.pathTaken[stop] not in newPath:
                    newPath.append(trainer.pathTaken[stop])
                else:
                    stopNotFound  = True
                    while(stopNotFound):
                        newStop = choice(self.pokeList)
                        if newStop not in newPath:
                            newPath.append(newStop)
                            stopNotFound = False
        trainer.updatePath(newPath)
        return trainer

    def spawn(self):
        for trainer in self.trainerL:
            trainerStartPath = randint(MINPATHLENGTH, MAXPOKESTOPS)
            trainerPath = sample(self.pokeList, trainerStartPath)
            trainer.updatePath( trainerPath )

    def cull(self):
        mean = self.meanFitness()
        stdDev = self.stdDev()
        newTrainerL = [trainer for trainer in self.trainerL if (trainer.fitness - mean) < -stdDev]
        #self.trainerL = newTrainerL
        while(len(newTrainerL) < self.genSize):
            newTrainerL.append(self.mate())
        self.trainerL = newTrainerL
        return newTrainerL

    def genOffspring( self ):
        if random() > 0.5:
            trainer = Trainer()
            newPath = []
            newPath = sample(self.pokeList, int(MAXPOKESTOPS/2) + 2)
            trainer.updatePath(newPath)
            return trainer
        else:
            bestTrainer = self.bestTrainers()[-1]
            trainer = Trainer()
            if len(bestTrainer.pathTaken) < SUBPATHLIMIT:
                newPath = bestTrainer.highestScoringSubset()
            else:
                newPath = []
            newPathExtra = [thing for thing in sample(self.pokeList, int(MAXPOKESTOPS/2)) if thing not in newPath]
            newPath+= newPathExtra
            trainer.updatePath(newPath)
            return trainer

    def mate(self):
        sortedTrainerL = sorted(self.trainerL, key = lambda trainer: trainer.fitness)
        #print(len(self.trainerL))
        #twoMates = sample(sortedTrainerL, 2)
        return self.genOffspring()

    def meanFitness(self):
        fitnessL = [trainer.fitness for trainer in self.trainerL]
        return (sum(fitnessL) * 1.0) / self.genSize

    def stdDev(self):
        meanFit = self.meanFitness()
        variance = 0
        for trainer in self.trainerL:
            variance += (trainer.fitness - meanFit)**2
        return (variance/self.genSize)**0.5


def optimizePath(pathL):
    return bruteForce( pathL )


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

#Depracated
# def getDistDict( pokeDict ):
#     distDict = {}
#     for start in pokeDict.keys():
#         for end in pokeDict.keys():
#             if start != end and (start,end) not in distDict.keys():
#                 dist = getDistance(pokeDict[start], pokeDict[end], pokeDict)
#                 distDict[(start,end)] = dist
#                 distDict[(end,start)] = dist
#     return distDict

def distanceBetweenPoints(point1, point2):
    return ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)**0.5

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
        totalDistance+= distDict[ pathList[stopNumber].name, pathList[stopNumber + 1].name ]
    return totalDistance

        
def geneticImp(pokeList):
    tourManager = geneticAlgorithmTSP.TourManager()

    for stop in pokeList:
        city = geneticAlgorithmTSP.City(stop.loc[0], stop.loc[1])
        tourManager.addCity(city)
    pop = geneticAlgorithmTSP.Population(tourManager, 100, True)
    print("Initial distance: " + str(pop.getFittest().getDistance()))
    ga = geneticAlgorithmTSP.GA(tourManager)
    pop = ga.evolvePopulation(pop)
    for i in range(0, 1000):
      pop = ga.evolvePopulation(pop)
    print("Finished")
    print("Final distance: " + str(pop.getFittest().getDistance()))
    print("Solution:")
    print(pop.getFittest())
    return pop.getFittest()


def geneticAlgorithm(pokeList):
    gen = Generation(100, 0.50, None, 1, 0, pokeList, distDict)
    gen.spawn()
    #print(gen.trainerL)
    #print()

    # for trainer in gen.trainerL:
    #     print(trainer)
    # print()
    for a0 in range(100):
        gen.evolveGen()
    # for trainer in gen.trainerL:
    #     print(trainer)
    #     print(trainer.fitness)
    #     print(trainer.distanceWalked)
    # print(gen.cull())
    #print(gen.trainerL[0])
    #print(gen.trainerL[1])
    #print(gen.genOffspring([gen.trainerL[0], gen.trainerL[1]]))
    # print(gen.trainerL)
    bestTrainer = gen.bestTrainers()[-1]
    # print()
    print()
    print(bestTrainer.pathTaken)
    print(bestTrainer.getUnweightedFitness())
    print(bestTrainer.distanceWalked)
    # print(bestTrainer.fitness)
    # print(bestTrainer.highestScoringSubset())
    return bestTrainer

def main():
    KMLDict, pokeDict = getDict()
    pokeList = [PokeStop(elem, key, KMLDict[key]) for key in KMLDict.keys() for elem in pokeDict.keys() if pokeDict[elem] == KMLDict[key]]

    global distDict
    distDict, refDict = getDistanceDictionary(pokeList)
    
    bestTrainerL = [geneticAlgorithm(pokeList) for a0 in range(100)]
    gen = Generation(100, 0.50, bestTrainerL, 5, 0, pokeList, distDict)

    for a0 in range(1000):
        gen.evolveGen()

    bestTrainer = gen.bestTrainers()[-1]
    print(bestTrainer)
    print(bestTrainer.fitness)
    print(bestTrainer.distanceWalked)

    # listOfCoors = [[stop.loc[0],stop.loc[1]] for stop in pokeList]

    # import numpy as np
    # import matplotlib.pyplot as plt
    # from scipy.cluster.vq import kmeans2, whiten

    # coordinates = np.array(listOfCoors)
    # x, y = kmeans2(whiten(coordinates), 20, iter = 25)
    # print(x)
    # print(y)
    # print(coordinates[:,0])
    # plt.scatter(coordinates[:,0], coordinates[:,1], c=y);
    # plt.show()

    # pokeList = pokeList[:10]
    # sol1 = bruteForce( pokeList )
    # print(sol1)

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

# This is a brute force method
# DO NOT TOUCH
def allPathGenerator( numOfStops ):
    return itertools.chain(*map(lambda x: itertools.combinations(numOfStops, x), range(0, len(numOfStops) + 1)))

def bruteForce( pokeList):
    highestEfficiency = 0
    bestPath = []
    bestPathDict = {}
    dictIndex = 0
    counter = 0
    allCombinations = allPathGenerator( list( range( len(pokeList) ) ) )
    excludablePaths = 2
    #max(int(float(len(pokeList))  * 0.1), 1)
    for combination in allCombinations:
        pathList = list(combination)
        #print(len(pathList))
        if len(pathList) > excludablePaths:
            newPath = []
            for fill in pathList:
                newPath.append(pokeList[fill])
            currentPathDistance = getPathLength( newPath )
            efficiency = float(len(pathList)) / currentPathDistance
            #print(efficiency)
            #print(efficiency > highestEfficiency)
            if efficiency > highestEfficiency:
                #print("New Best Path = " + str(dictIndex))
                #print("Efficiency: " + str(efficiency / 100))
                #print("Length of Path = " + str(currentPathDistance))
                #print("Number of Stops = " + str(len(pathList)))
                #print("Path = " + str(pathList))
                #print(counter)
                #print()

                highestEfficiency = efficiency
                bestPath = newPath
                bestPathDict[dictIndex] = (pathList, efficiency)
                dictIndex+=1
        #print(counter)
        counter += 1
    return bestPath


if __name__ == '__main__':
    main()
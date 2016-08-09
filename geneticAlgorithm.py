import kmlPokeDict
import minDist
from math import *
from random import *
from time import *
import itertools
import geneticAlgorithmTSP
from pokestopDataReaderv2 import *

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
        self.updatePath(optimizePath(self.pathTaken, len(self.pathTaken)))

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
        #print(sortedTrainerL[-3:])
        sortedTrainerL[-self.individualsToKeep:]
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
            trainer.optimizeCurrentPath()

    def cull(self):
        mean = self.meanFitness()
        stdDev = self.stdDev()
        newTrainerL = [trainer for trainer in self.trainerL if (trainer.fitness) < mean + stdDev]
        #self.trainerL = newTrainerL
        while(len(newTrainerL) < self.genSize):
            newTrainerL.append(self.mate())
        self.trainerL = newTrainerL
        return newTrainerL

    def genOffspring( self ):
        if random() > 0.4:
            trainer = Trainer()
            newPath = []
            newPath = sample(self.pokeList, int(MAXPOKESTOPS/2) + 2)
            trainer.updatePath(newPath)
            return trainer
        else:
            bestTrainer = choice(self.bestTrainers())
            trainer = Trainer()
            if len(bestTrainer.pathTaken) < SUBPATHLIMIT:
                newPath = bestTrainer.highestScoringSubset()
            else:
                newPath = []
            newPathExtra = [thing for thing in sample(self.pokeList, int(MAXPOKESTOPS/2)) if thing not in newPath]
            newPath+= newPathExtra
            trainer.updatePath(newPath)
            trainer.optimizeCurrentPath()
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

def optimizePath(pathL, sizeRestriction = None):
    """Optimizes the order of a given set of pokestops to visit"""
    return bruteForce( pathL, sizeRestriction )

def geneticImp(pokeList):
    """A genetic implementation for finding our best path"""
    tourManager = geneticAlgorithmTSP.TourManager()

    for stop in pokeList:
        city = geneticAlgorithmTSP.City(stop.loc[0], stop.loc[1])
        tourManager.addCity(city)
    pop = geneticAlgorithmTSP.Population(tourManager, 100, True)
    print("Initial distance: " + str(pop.getFittest().getDistance()))
    ga = geneticAlgorithmTSP.GA(tourManager)
    pop = ga.evolvePopulation(pop)
    for i in range(0, 10000):
      print(i)
      pop = ga.evolvePopulation(pop)
    print("Finished")
    print("Final distance: " + str(pop.getFittest().getDistance()))
    print("Solution:")
    print(pop.getFittest())
    print(119/pop.getFittest().getDistance() /112)
    return pop.getFittest()


def geneticAlgorithm(pokeList):
    gen = Generation(100, 0.05, None, 5, 0, pokeList, distDict)
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

def getPathLength(pathList):
    """Given alist of pokestops that represent the path taken, returns the length of the path"""
    totalDistance = 0
    for stopNumber in range(len(pathList) - 1):
        totalDistance+= distDict[ pathList[stopNumber].name, pathList[stopNumber + 1].name ]
    return totalDistance

def allPathGenerator( numOfStops ):
    """Generator to create all combinations of pokestops"""
    return itertools.chain(*map(lambda x: itertools.permutations(numOfStops, x), range(0, len(numOfStops) + 1)))

def bruteForce( pokeList, pathSize = None):
    """Brute forces the most optimal path to take"""
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
    
def main():
    KMLDict, pokeDict = getDict()
    pokeList = [PokeStop(elem, key, KMLDict[key]) for key in KMLDict.keys() for elem in pokeDict.keys() if pokeDict[elem] == KMLDict[key]]
    pokeList = filterList( "Mudd", pokeList)
    pokeList = mergeStops(pokeList)
    global distDict
    distDict, refDict = getDistanceDictionary(pokeList)
    bestTrainer = geneticAlgorithm(pokeList)
    bestTrainerL = [geneticAlgorithm(pokeList) for a0 in range(100)]
    gen = Generation(100, 0.50, bestTrainerL, 5, 0, pokeList, distDict)

    for a0 in range(100):
        gen.evolveGen()

    bestTrainerL = sorted(gen.trainerL, key = lambda trainer: trainer.fitness)
    bestTrainer = bestTrainerL[-1]



if __name__ == '__main__':
    main()


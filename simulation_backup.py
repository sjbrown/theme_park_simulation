#/usr/bin/python
fullscreen = 1

# standardize on seconds as the time metric
minute = 60
hour = minute*60
fullDay = hour*24
nineAM = hour*9
tenAM = hour*10
noon = hour*12
ninePM = hour*(12+9)
speed = 1
prematureLineExitThreshold = 30

# standardize on meters as the space metric
humanWidth = 0.4
gpsAccuracyRange = 0.8
gpsAccuracyRange = 1.8
pixelsPerMeter=4

from random import Random
rng = Random()

deviceAcceptanceRate = 0.3
capacity = 600
numVisitors = 0

startTime = nineAM
fps = 60
parkBackground = 'bg_parkpanel.png'
	
def InitialNumVisitors( timeOfDay ):
	numVisitors = 0
	return numVisitors

def getEntryRate( timeOfDay ):
	if timeOfDay < nineAM:
		return 0
	if timeOfDay < noon:
		return 5 
	if timeOfDay < ninePM:
		return 2
	if timeOfDay > ninePM:
		return 0

def getExitRate( timeOfDay ):
	if timeOfDay < tenAM:
		return 0
	if timeOfDay < noon:
		return 1
	if timeOfDay < ninePM:
		return 3
	if timeOfDay > ninePM:
		return 10

decisionMakingTime = 120
decisionMakingStdDeviation = 80

__decisionTimes = []
#WARNING: this will be done every 5 seconds
for i in xrange(10):
	t = rng.normalvariate(decisionMakingTime, decisionMakingStdDeviation)
	t = int(t)
	if t <= 0:
		t = 1
	__decisionTimes.append( t )

__decisionTimesIndex = 0
def getNextDecisionDuration():
	global __decisionTimesIndex
	global __decisionTimes
	__decisionTimesIndex +=1
	__decisionTimesIndex %=len(__decisionTimes)
	return __decisionTimes[__decisionTimesIndex]


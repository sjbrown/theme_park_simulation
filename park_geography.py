#! /usr/bin/python

from classes import Ride, Lineup
from pygame.locals import *
import allobjects
from log import log
from pathfinder import HallRect, precompute

try:
	import simulation
except:
	print "COULD NOT FIND SIMULATION DEFINITION"
	print "USING BACKUP INSTEAD"
	import simulation_backup as simulation
rng = simulation.rng

class ParkGeography:
	def __init__(self, name=None):
		self.boundRect = Rect( (0,0,1024,600) )
		self.rides = []
		self.lineups = []
		self.computedPaths = {}
		self.hEmpties = []
		self.name = name
		self.randomDestCounter = 0
		self.entryPointCounter = 0
		self.entryPoints = [(460,394),(500,404)]

	#----------------------------------------------------------------------
	def GetEntryPoint(self):
		return self.entryPoints[self.entryPointCounter]
		self.entryPointCounter += 1

	#----------------------------------------------------------------------
	def InitRect(self,boundRect):
		self.boundRect = boundRect

	#----------------------------------------------------------------------
	def PlaceVisitor( self, visitor, pos=None ):
		if pos:
			x = pos[0]
			y = pos[1]
		else:
			x = rng.uniform(self.boundRect.x, self.boundRect.width)
			y = rng.uniform(self.boundRect.y, self.boundRect.height)

		visitor.rect.center = [x,y]

	#----------------------------------------------------------------------
	def AddRide( self, ride, pos=None ):
		self.rides.append( ride )


	#----------------------------------------------------------------------
	def AddLineup( self, lineup ):
		self.lineups.append( lineup )
		if lineup.rect.left < self.boundRect.left:
			lineup.rect.left = self.boundRect.left
		if lineup.rect.top < self.boundRect.top:
			lineup.rect.top = self.boundRect.top
		if lineup.rect.right > self.boundRect.right:
			lineup.rect.right = self.boundRect.right
		if lineup.rect.bottom > self.boundRect.bottom:
			lineup.rect.bottom = self.boundRect.bottom

	#----------------------------------------------------------------------
	def SavePaths( self ):
		saveString = '\npaths = \\\n'
		saveString += str( self.computedPaths )
		saveString += '\n'
		saveString += '\nhEmpties = [\n'
		for h in self.hEmpties:
			saveString += '"""'+ h.GetSaveRepr() +'""",\n'
		saveString += '\n]\n'

		fname = self.name +'_paths.py'
		#fname = 'computedPaths.py'
		f = file( fname, 'w' )
		f.write( saveString )
		f.close()

	#----------------------------------------------------------------------
	def ComputeHallRects( self ):
		from rectdiff import GetEmptyRects
		from pathfinder import precompute, MakeHallRects
		fulls = [ x.rect for x in self.lineups ]
		fulls += [ x.rect for x in self.rides ]
		empties = GetEmptyRects(self.boundRect, fulls)
		self.hEmpties = MakeHallRects( empties )
		if not self.hEmpties:
			raise Exception("Park Geog could not MakeHallRects")

	#----------------------------------------------------------------------
	def ComputePaths( self ):
		self.computedPaths = {}

		for spot in [x.hotspot for x in self.lineups]:
			subDict = precompute( self.hEmpties, spot )
			self.computedPaths[spot] = subDict

		try:
			self.SavePaths()
		except Exception, e:
			print 'Could not save paths'
			print e
			

	#----------------------------------------------------------------------
	def _LoadHallRectsFromPreviousSave( self ):
		print 'loading from prev save...'
		import computedPaths
		self.hEmpties = computedPaths.hEmpties[self.name]
		if not self.hEmpties:
			raise Exception("Park could not load hall rects")
	#----------------------------------------------------------------------
	def _LoadHallRectsFromCWPark( self ):
		print 'loading from cw park...'
		import cw_park
		self.hEmpties = []
		for r in cw_park.hallways:
			self.hEmpties.append( HallRect(Rect(r)) )
		if not self.hEmpties:
			raise Exception("Park could not load CW hall rects")
	#----------------------------------------------------------------------
	def LoadHallRects( self ):
		try:
			self._LoadHallRectsFromCWPark()
			return
		except Exception, e:
			print "Hall Rects not defined for CW.  Try save file..."
			print "ERROR: this should not happen for CW!!"
			print e
		try:
			self._LoadHallRectsFromPreviousSave()
		except Exception, e:
			print "Hall Rects not previously saved.  Computing..."
			print "ERROR: this should not happen for CW!!"
			from time import sleep
			sleep(3)
			print e
			self.ComputeHallRects()

	#----------------------------------------------------------------------
	def LoadPaths( self ):
		try:
			import computedPaths
			self.computedPaths = computedPaths.paths[ self.name ]
		except Exception, e:
			print "Path was not saved.  Computing..."
			print e
			self.ComputePaths()

	#----------------------------------------------------------------------
	def GetDestPoint( self, currentPt, hotspot ):
		if not self.computedPaths:
			self.LoadHallRects()
			self.LoadPaths()

		from pathfinder import GetNextDest
		try:
			return GetNextDest( self.computedPaths, hotspot, 
			                    currentPt, self.hEmpties )
		except:
			print "some problem with the precomputed path!"
			self.LoadHallRects()
			self.ComputePaths()
			self.LoadPaths()

	#----------------------------------------------------------------------
	def GetRandomDestPoint( self, currentPt ):
		containerRect = None
		if not self.computedPaths:
			self.LoadHallRects()
			self.LoadPaths()

		for h in self.hEmpties:
			r = h.rect
			if r.collidepoint( currentPt ):
				containerRect = r
				break

		if not containerRect:
			return None
		case = { 0: containerRect.topleft,
		         1: containerRect.midtop,
		         2: containerRect.topright,
		         3: containerRect.midright,
		         4: containerRect.bottomright,
		         5: containerRect.midbottom,
		         6: containerRect.bottomleft,
		         7: containerRect.midleft,
		         8: containerRect.center,
		}
		self.randomDestCounter += 1
		self.randomDestCounter %= len(case)
		return case[self.randomDestCounter]


def getRandomPark():
	randomPark = ParkGeography()
	for i in xrange( 4 ):
		x = rng.uniform(self.boundRect.x+40, self.boundRect.width-40)
		y = rng.uniform(self.boundRect.y+40, self.boundRect.height-40)
		ride = Ride( (x,y) )
		allobjects.allRides.append( ride )
		randomPark.AddRide( ride )

		lineup = ride.MakeLineup()
		allobjects.allLineups.append( lineup )
		randomPark.AddLineup( lineup )
	return randomPark

def getFixedPark():
	fixedPark = ParkGeography()
	ridePositions = [
	                  [60,100], [700,200], [150,400], [400,450]
	                ]
	linePositions = [
	                  [100,120], [610,270], [190,300], [360,300]
	                ]
	for i in xrange( 4 ):
		ride = Ride( ridePositions[i] )
		allobjects.allRides.append( ride )
		fixedPark.AddRide( ride )

		lineup = ride.MakeLineup()
		lineup.rect.topleft = linePositions[i]
		lineup.SetHotspot( (lineup.rect.right+1,lineup.rect.bottom) )
		allobjects.allLineups.append( lineup )
		fixedPark.AddLineup( lineup )
	allobjects.park = fixedPark
	return fixedPark

def getCWPark():
	fixedPark = ParkGeography('cw')
	fixedPark.InitRect( Rect(0,0,1024,500) )
	import cw_park
	reload(cw_park)
	rideDimensions = cw_park.rideDimensions
	rideNames = cw_park.rideNames
	lineSizes = cw_park.lineSizes
	lineMatricies = cw_park.lineMatricies
	linePositions = cw_park.linePositions
	hotspotPositions = cw_park.hotspotPositions
	ejectPositions = cw_park.ejectPositions

	for i in xrange( len(rideDimensions) ):
		ride = Ride( rideDimensions[i][0], rideDimensions[i][1] )
		ride.name = rideNames[i]
		ride.SetEjectLocation( ejectPositions[i] )
		allobjects.allRides.append( ride )
		fixedPark.AddRide( ride )

		#print lineSizes[i]
		lineup = Lineup( lineSizes[i], lineMatricies[i] )
		ride.SetLineup( lineup )
		lineup.rect.topleft= linePositions[i]
		lineup.SetHotspot( tuple(hotspotPositions[i]) )
		allobjects.allLineups.append( lineup )
		fixedPark.AddLineup( lineup )

	allobjects.park = fixedPark
	return fixedPark


if __name__ == '__main__':
	print 'Do Tests'
	from rectdiff import GetEmptyRects
	from pygame.locals import *
	import pygame

	def load_park():
		fixedPark = getCWPark()
		boundRect = fixedPark.boundRect
		fulls = [x.rect for x in fixedPark.rides] 
		fulls += [x.rect for x in fixedPark.lineups]
		fixedPark.LoadHallRects()
		fixedPark.LoadPaths()
		#empties = GetEmptyRects( fixedPark.boundRect, fulls )
		print fixedPark.hEmpties
		halls = [x.rect for x in fixedPark.hEmpties]
		#halls = [x.rect for x in fixedPark.hEmpties]
		spots = [x.hotspot for x in fixedPark.lineups]
		drops = [x.GetEjectLocation() for x in fixedPark.rides]
		return fixedPark, boundRect, fulls, halls, spots, drops

	fixedPark, boundRect, fulls, halls, spots, drops  = load_park()

	global screen
	pygame.init()
	print 'setting reso', boundRect.size
	screen = pygame.display.set_mode(boundRect.size)

	#Display The Background
	screen.fill( (0,0,0) )
	#screen.blit(bgMangr.GetBackground(), (0, 0))
	pygame.display.flip()

	blue = (0,0,200)
	red = (200,0,200)
	green = (0,200,0)
	orange = (255,200,0)
	quit = 0
	i = 0
	color = list(blue)

	while not quit:
		i+=1
		import time
		#Handle Input Events
		remainingEvents = pygame.event.get()
		for event in remainingEvents:
			if event.type == QUIT or ( event.type == KEYDOWN and event.key == K_ESCAPE):
				quit = 1
		e = halls[ i%len(halls) ]
		s = pygame.Surface( e.size )
		color[1] = (color[1]+60)%256
		s.fill( color )
		screen.blit( s, e.topleft )
		pygame.display.flip()
		if not i%5:
			for f in fulls:
				s = pygame.Surface( f.size )
				s.fill( red )
				screen.blit( s, f.topleft )
		for spot in spots:
			s = pygame.Surface( (1,1) )
			s.fill( green )
			screen.blit( s, spot )
		for drop in drops:
			s = pygame.Surface( (1,1) )
			s.fill( orange )
			screen.blit( s, drop )
		time.sleep(0.5)
		pygame.display.flip()

		if not i%22:
			#reload( 'cw_park' )
			fixedPark, boundRect, fulls, halls, spots, drops = load_park()
			screen.fill( (0,0,0) )
			pygame.display.flip()


	pygame.quit()

#! /usr/bin/python
from sets import Set
from pygame import Rect
from rectintersect import IntersectRect
from pickle import loads, dumps
from math import sqrt

#------------------------------------------------------------------------------
def GetDistanceBetween( aPoint, bPoint ):
	xLength = aPoint[0] - bPoint[0]
	yLength = aPoint[1] - bPoint[1]
	return sqrt( yLength**2 + yLength**2 )

#------------------------------------------------------------------------------
def LoadHallRect( saveRepr ):
	return loads(saveRepr)
#------------------------------------------------------------------------------
class HallRect:
	def __init__( self, rect ):
		self.rect = rect

		# [ neighborRect, neighborRect, ... ]
		self.neighbors = Set()
		# { neighbor: linkToGetThere, ... }
		self.linkToNeighbor = {}
		# { hotspot: destinationCorner, ... }
		self.paths = {}

		self.distances = {}

	def __repr__( self ):
		return str(self.rect)
		
	def __str__( self ):
		return str(self.rect) + str(self.paths) + '\nnei:'+str(self.neighbors)

	def collidepoint( self, point ):
		return self.rect.collidepoint( point )

	def GetSaveRepr( self ):
		return dumps( self )
		
		

#------------------------------------------------------------------------------
def FindCollidingRect( hallRects, point ):
	containRect = None
	for r in hallRects:
		if r.collidepoint( point ):
			containRect = r
			break
	return containRect
	
#------------------------------------------------------------------------------
def FillPaths( curRect, visitedRects, hotspot ):
	nextRects = []
	for n in curRect.neighbors:
		distanceBetween = GetDistanceBetween(curRect.paths[hotspot],
		                                     n.linkToNeighbor[curRect])
		distanceToHotspot = curRect.distances[hotspot] + distanceBetween
		if n in visitedRects:
			if n.distances[hotspot] <= distanceToHotspot:
				continue
		n.paths[hotspot] = n.linkToNeighbor[curRect]
		n.distances[hotspot] = distanceToHotspot
		visitedRects.append(n)
		nextRects.append(n)
	for n in nextRects:
		FillPaths( n, visitedRects, hotspot )
		

#------------------------------------------------------------------------------
def MakeHallRects( hallRects ):
	hrects = []
	for r in hallRects:
		if not isinstance(r, HallRect):
			h = HallRect( r )
			hrects.append( h )
		else:
			hrects.append( r )
	return hrects

#------------------------------------------------------------------------------
def GetNextDest( computedList, finalHotspot, currentPos, hallRects ):
	try:
		subDict = computedList[finalHotspot]
		return subDict[currentPos] 
	except KeyError:
		for r in hallRects:
			if r.collidepoint( currentPos ):
				try:
					return r.paths[finalHotspot]
				except KeyError, e:
					print "KEY ERROR", e
					print "Perhaps the computed path is old"
					print "( try deleting cw_paths.py* )"
					raise e
	return None

#------------------------------------------------------------------------------
def precompute( hallRects, hotspot ):
	# find the containing rect
	containRect = FindCollidingRect(hallRects, hotspot)
	if not containRect:
		print 'no rect contains that hotspot', hotspot
		print 'rect candidates:', [x.rect for x in hallRects]
		return
	containRect.paths[hotspot] = list(hotspot)
	containRect.distances[hotspot] = 0
	
	if not containRect:
		print "hotspot was not in the given rectangles"
		return
	
	# populate the neighbors
	for r in hallRects:
		inflatedRect = r.rect.inflate(2,2)
		neighborIndexes = inflatedRect.collidelistall( hallRects )
		for i in neighborIndexes:
			if r == hallRects[i]:
				continue
			intersection = IntersectRect( inflatedRect, 
			                              hallRects[i].rect )
			r.neighbors.add( hallRects[i] )
			r.linkToNeighbor[hallRects[i]] = intersection.center
			#print 'added neighbor', r

	visitedRects = [containRect]
	FillPaths( containRect, visitedRects, hotspot )

	computedList = {}
	for r in hallRects:
		for n in r.neighbors:
			computedList[ r.linkToNeighbor[n] ] = n.paths[hotspot]

	return computedList

if __name__ == '__main__':
	print "Do Tests"
	halls = [HallRect(Rect(0, 0, 800, 40)), HallRect(Rect(0, 640, 800, 160)), HallRect(Rect(0, 440, 500, 200)), HallRect(Rect(600, 440, 200, 200)), HallRect(Rect(0, 40, 100, 400)), HallRect(Rect(200, 140, 300, 300)), HallRect(Rect(600, 140, 200, 300)), HallRect(Rect(300, 40, 200, 100)), HallRect(Rect(600, 40, 200, 100))]
	dest = (1,1)

	try:
		import cw_park
		halls = []
		for i in range(len(cw_park.hallways)):
			r = Rect( cw_park.hallways[i] )
			if i == 0:
				dest = r.center
			halls.append( HallRect( r ) )

	except Exception,e:
		print 'tried but failed to import hallways defined in cw_park'
		print 'Exception', type(e), e

	computedList = precompute( halls, dest )

	f = file( '/tmp/pathtest.py', 'w' )
	f.write( 'l = [\n' )
	for r in halls:
		print r
		f.write( '\n"""'+ r.GetSaveRepr() + '""",\n' )
	f.write( '\n]\n' )
	f.close()

	#from pprint import pprint
	#pprint (computedList)


	#Initialize Everything
	from pygame.locals import *
	import pygame
	global screen
	pygame.init()
	RESOLUTION = (800,800)
	screen = pygame.display.set_mode(RESOLUTION)

	#Display The Background
	screen.fill( (0,0,0) )
	#screen.blit(bgMangr.GetBackground(), (0, 0))
	pygame.display.flip()

	blue = (0,0,200)
	red = (200,0,200)
	quit = 0
	i = 0

	color = list(blue)

	from random import Random
	rng = Random()

	while not quit:
		i+=1
		import time

		#Handle Input Events
		remainingEvents = pygame.event.get()
		for event in remainingEvents:
			if event.type == QUIT:
				quit = 1
			elif event.type == KEYDOWN and event.key == K_ESCAPE:
				quit = 1
		e = halls[ i%len(halls) ].rect
		s = pygame.Surface( e.size )
		color[1] = (color[1]+61)%256
		s.fill( color )
		screen.blit( s, e.topleft )
		pygame.display.flip()

		# every 8th time through, draw a red path
		if not i%8:
			startHall = rng.choice( halls )
			startPos = startHall.rect.center
			nextDest = dest
			for j in range( len(halls) ):
				nextDest = GetNextDest( computedList, dest, 
			                                startPos, halls )
				pygame.draw.line( screen, red, 
				                  startPos, nextDest)
				startPos = nextDest

		# sleep a little bit so we can watch what's going on
		time.sleep(0.5)
		pygame.display.flip()


	pygame.quit()

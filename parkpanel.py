#! /usr/bin/python

from pygame.sprite import RenderUpdates, Group, Sprite
from pygame.locals import *
from pygame import Rect, Surface
import pygame
from classes import UnGuidedVisitor, GuidedVisitor
from lineup import Lineup
from ride import Ride, Car
from park_geography import getRandomPark
from park_geography import getFixedPark
from park_geography import getCWPark
import allobjects
import events
from log import log

try:
	import simulation
except:
	print "COULD NOT FIND SIMULATION DEFINITION"
	print "USING BACKUP INSTEAD"
	import simulation_backup as simulation

parkGenerationFunction = getCWPark

#-----------------------------------------------------------------------------
class ParkPanel:
	def __init__(self,bgImage, pos):
		self.isDone = 0
		self.boundRect = bgImage.get_rect()

		self.deviceGroup = RenderUpdates()
		self.rideGroup = RenderUpdates()
		self.carGroup = RenderUpdates()
		self.lineupGroup = RenderUpdates()
		self.highlightGroup = RenderUpdates()
		self.redVisitorGroup = RenderUpdates()
		self.greenVisitorGroup = RenderUpdates()
		self.parkGeography = parkGenerationFunction()
		allobjects.timeOfDay = simulation.startTime

		self.bgImage = bgImage

		for r in self.parkGeography.rides:
			self.rideGroup.add( r )
			self.carGroup.add( r.idleCars )

		for l in self.parkGeography.lineups:
			self.lineupGroup.add( l )
			

		totalVisitors = simulation.InitialNumVisitors(0)
		numGreen = int(totalVisitors*simulation.deviceAcceptanceRate)
		numRed = totalVisitors - numGreen
		for i in xrange( numGreen ):
			device = allobjects.server.NewDevice()
			if device:
				self.deviceGroup.add( device )
				newGuy = GuidedVisitor( device )
			else:
				newGuy = UnGuidedVisitor()
			self.AddVisitor( newGuy )
		for i in xrange( numRed ):
			newGuy = UnGuidedVisitor()
			self.AddVisitor( newGuy )

		events.AddListener( self )
		events.AddEvent( "SelectVisitor" )
		events.AddEvent( "UnSelectVisitor" )
		events.AddEvent( "HighlightRide" )
		events.AddEvent( "UnHighlightRide" )
		events.AddEvent( "HighlightLineup" )
		events.AddEvent( "UnHighlightLineup" )
		self.paused = False
		self.showRed = True
		self.justToggledShowRed = False
		self.showServer = True
		self.justToggledShowServer = False
		self.showGreen = True
		self.justToggledShowGreen = False

		self.redCircle = Surface( (17,17),SRCALPHA,32 )
		pygame.draw.circle( self.redCircle, (255,0,0), (8,8), 8, 1  )
		self.greenCircle = Surface( (17,17),SRCALPHA,32 )
		pygame.draw.circle( self.greenCircle, (0,255,0), (8,8), 8, 1 )

		self.highlight = Sprite()
		self.highlight.image = self.greenCircle
		self.highlight.rect = self.greenCircle.get_rect()

		self.selection = Sprite()
		self.selection.image = self.greenCircle
		self.selection.rect = self.greenCircle.get_rect()

		self.highlightVisitor = None
		self.selectedVisitor = None

	#---------------------------------------------------------------------
	def On_Pause(self):
		log.info( 'parkpanel pause' )
		self.paused = not self.paused

	#---------------------------------------------------------------------
	def On_ShowRed(self):
		self.showRed = not self.showRed
		self.justToggledShowRed = True

	#---------------------------------------------------------------------
	def On_ShowGreen(self):
		self.showGreen = not self.showGreen
		self.justToggledShowGreen = True

	#---------------------------------------------------------------------
	def On_ShowServer(self):
		self.showServer = not self.showServer
		self.justToggledShowServer = True

	#---------------------------------------------------------------------
	def On_MouseClick(self,pos):
		if not self.boundRect.collidepoint( pos ):
			return
		if self.selectedVisitor:
			events.Fire( "UnSelectVisitor", self.selectedVisitor )
			self.selectedVisitor = None
			self.highlightGroup.remove( self.selection )

		self.selectedVisitor = self.FindVisitorNear(pos)

		if not self.selectedVisitor:
			return

		self.highlightGroup.add( self.selection )

		if hasattr( self.selectedVisitor, 'device' ):
			self.selection.image = self.greenCircle
		else:
			self.selection.image = self.redCircle

		events.Fire( "SelectVisitor", self.selectedVisitor )

	#---------------------------------------------------------------------
	def UpdateHighlightGroup(self):
		if self.selectedVisitor:
			self.selection.rect.center = self.selectedVisitor.rect.center
		self.highlightGroup.update()

	#---------------------------------------------------------------------
	def On_MouseMove(self,event):
		pos = event.pos
		if not self.boundRect.collidepoint( pos ):
			return

		self.highlightVisitor = self.FindVisitorNear(pos)
		self.HighlightRideNear(pos)
		self.HighlightLineupNear(pos)

		if not self.highlightVisitor:
			self.highlightGroup.remove( self.highlight )
			return

		if hasattr( self.highlightVisitor, 'device' ):
			self.highlight.image = self.greenCircle
		else:
			self.highlight.image = self.redCircle

		self.highlight.rect.center = self.highlightVisitor.rect.center
		self.highlightGroup.add( self.highlight )

	#---------------------------------------------------------------------
	def AddVisitor(self, visitor, pos=None):
		if hasattr( visitor, "device" ):
			self.greenVisitorGroup.add( visitor )
		else:
			self.redVisitorGroup.add( visitor )
		self.parkGeography.PlaceVisitor( visitor, pos )
		allobjects.allVisitors.add( visitor )

	#---------------------------------------------------------------------
	def DoVisitorEntries( self ):
		if len( allobjects.allVisitors ) >= simulation.capacity:
			return

		totalVisitors = simulation.getEntryRate( allobjects.timeOfDay )
		#print "entering ", totalVisitors
		numGreen = int(totalVisitors*simulation.deviceAcceptanceRate)
		if not allobjects.thousandCounter%2:
			numGreen += 1
		numRed = totalVisitors - numGreen
		pos = self.parkGeography.GetEntryPoint()
		for i in xrange( numGreen ):
			device = allobjects.server.NewDevice()
			if device:
				self.deviceGroup.add( device )
				newGuy = GuidedVisitor( device )
			else:
				newGuy = UnGuidedVisitor()
			self.AddVisitor( newGuy, pos )
		for i in xrange( numRed ):
			newGuy = UnGuidedVisitor()
			self.AddVisitor( newGuy, pos )

	#---------------------------------------------------------------------
	def DoVisitorExits( self ):
		if not allobjects.allVisitors:
			return
		totalVisitors = simulation.getExitRate( allobjects.timeOfDay )
		for i in xrange( totalVisitors ):
			allobjects.allVisitors.sprites()[i].LeaveThePark()

	#---------------------------------------------------------------------
	def RemoveVisitor(self, visitor):
		visitor.kill()

	#---------------------------------------------------------------------
	def FindVisitorNear(self,pos,radius=4):
		for v in self.greenVisitorGroup.sprites():
			if abs( v.rect.centerx - pos[0] ) < radius \
			  and abs( v.rect.centery - pos[1] ) < radius:
				return v
		for v in self.redVisitorGroup.sprites():
			if abs( v.rect.centerx - pos[0] ) < radius \
			  and abs( v.rect.centery - pos[1] ) < radius:
			  	return v
		return None

	#---------------------------------------------------------------------
	def HighlightRideNear(self,pos):
		events.Fire( "UnHighlightRide" )

		for r in self.rideGroup.sprites():
			if r.rect.collidepoint( pos ):
				events.Fire( "HighlightRide", r )
				return

	#---------------------------------------------------------------------
	def HighlightLineupNear(self,pos):
		events.Fire( "UnHighlightLineup" )

		for l in self.lineupGroup.sprites():
			if l.rect.collidepoint( pos ):
				events.Fire( "HighlightLineup", l )
				return

	#---------------------------------------------------------------------
	def SignalKey( self, event, remainingEvents ):
		pass

	#---------------------------------------------------------------------
	def Click( self, pos ):
		pass
	#---------------------------------------------------------------------
	def MouseOver( self, event ):
		pass
		
	#---------------------------------------------------------------------
	def DoGraphics( self, screen, display, timeChange ):
		if self.justToggledShowRed  \
		   or self.justToggledShowGreen \
		   or self.justToggledShowServer:
			screen.blit( self.bgImage, self.boundRect )
			display.flip()
			self.justToggledShowRed = False
			self.justToggledShowGreen = False
			self.justToggledShowServer = False
		else:
			bg = self.bgImage

			self.rideGroup.clear(screen, self.bgImage)
			self.lineupGroup.clear(screen, self.bgImage)
			self.highlightGroup.clear( screen, self.bgImage )
			if self.showRed:
				self.redVisitorGroup.clear( screen, bg )
			if self.showGreen:
				self.greenVisitorGroup.clear( screen, bg )
			if self.showServer:
				self.deviceGroup.clear(screen, self.bgImage )

		self.UpdateHighlightGroup()
		if not allobjects.thousandCounter % 30:
			self.DoVisitorEntries()
			self.DoVisitorExits()

		if not self.paused:
			allobjects.timeOfDay += simulation.speed
			self.carGroup.update()
			self.rideGroup.update()
			self.lineupGroup.update()
			self.redVisitorGroup.update()
			self.greenVisitorGroup.update()
			if self.showServer:
				self.deviceGroup.update()

		changedRects =  self.highlightGroup.draw(screen)
		changedRects += self.rideGroup.draw(screen)
		changedRects += self.carGroup.draw(screen)
		changedRects += self.lineupGroup.draw(screen)
		if self.showRed:
			changedRects += self.redVisitorGroup.draw(screen)
		if self.showGreen:
			changedRects += self.greenVisitorGroup.draw(screen)
		if self.showServer:
			changedRects += self.deviceGroup.draw(screen)

		display.update( changedRects )



if __name__ == '__main__':
	from pygame.locals import *
	from pygame.sprite import Group, Sprite

	RESOLUTION = (850,400)
	#Attempt to optimize with psyco
	try:
		import psyco
		psyco.full()
	except Exception, e:
		pass
		#print "no psyco for you!", e

	#Initialize Everything
	#global screen
	screen = None
	pygame.init()
	screen = pygame.display.set_mode(RESOLUTION)
	pygame.display.set_caption('Park Simulation')

	#Display The Background
	screen.fill( (0,0,0) )
	try:
		bgSurf = pygame.image.load( simulation.parkBackground )
		screen.blit(bgSurf, (0, 0))
		pygame.display.flip()
	except:
		bgSurf = Surface( RESOLUTION )
		bgSurf.fill( (0,0,0) )
		print "could not load / blit the background image"

	#Prepare Game Objects
	allobjects.server = TravelBuddyServer()
	displayer  = ParkPanel(bgSurf)

	#Main Loop
	clock = pygame.time.Clock()
	lastReload = 0
	oldfps = 0

	while 1:
		timeChange = clock.tick(simulation.fps)
		lastReload += timeChange
		if lastReload > 5000:
			lastReload = 0
			reload(simulation)
		newfps = int(clock.get_fps())
		#if newfps != oldfps:
			#print "fps: ", newfps
			#oldfps = newfps

		#Handle Input Events
		remainingEvents = pygame.event.get()
		for event in remainingEvents:
			upKeys = [x for x in  remainingEvents if x.type==KEYUP ]
			if event.type == QUIT:
				displayer.isDone = 1
			elif event.type == KEYDOWN and event.key == K_ESCAPE:
				displayer.isDone = 1
			elif event.type == KEYDOWN or event.type == KEYUP:
				displayer.SignalKey( event, upKeys )
			elif event.type == MOUSEBUTTONDOWN:
				displayer.Click(event.pos)
			if event.type == MOUSEMOTION:
				displayer.MouseOver(event)

		#Draw Everything
		displayer.DoGraphics( screen, pygame.display, timeChange )

		# if the displayer is done, it's time to switch to 
		# a different displayer.  Sometimes the displayer doesn't
		# know what should come after it is done.
		# If we can't figure it out, default to the Main Menu
		if displayer.isDone:
			break



	#Game Over
	print "Game is over"

	pygame.quit()

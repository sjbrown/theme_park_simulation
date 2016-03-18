#! /usr/bin/python

import pygame
import events
from pygame.sprite import RenderUpdates, Group, Sprite
from pygame.locals import *
from utils import load_png
import allobjects

try:
	import simulation
except:
	print "COULD NOT FIND SIMULATION DEFINITION"
	print "USING BACKUP INSTEAD"
	import simulation_backup as simulation

from toggle_button import ToggleButtonSprite
import poutine.gui_widgets
gui = poutine.gui_widgets
gui.FONTSIZE = 26
gui.INACTIVE_COLOR = (100,100,100)
LabelSprite, ButtonSprite = gui.LabelSprite, gui.ButtonSprite, 
font = pygame.font.Font(gui.FONTFACE, gui.FONTSIZE)
ascent = font.get_ascent()

def formatTime( seconds ):
	hours = seconds / simulation.hour
	mins = (seconds%simulation.hour) / simulation.minute
	return '%02d'%hours  +":"+ '%02d'%mins

def ride_cmp( rideA, rideB ):
	return cmp( rideA.lineup.GetGuess(), rideB.lineup.GetGuess() )

#-----------------------------------------------------------------------------
#events.AddEvent( "RemoveRideReq" )
#events.AddEvent( "AddRideReq" )
class DeviceSprite(Sprite):
	def __init__( self ):
		Sprite.__init__(self)
		#self.image = load_png( 'device.png' )
		#self.origImg = self.image.convert_alpha()
		#self.rect = self.image.get_rect()
		self.rect = Rect( 0, 0, 330, 158 )

		#self.internalDrawRect = Rect( 45, 100, 130, 158 )
		self.image = pygame.Surface( self.rect.size )
		self.image.fill( (255,255,255) )
		self.origImg = self.image.convert()
		self.visitor = None
		self.onRides = []
		self.offRides = []

	def SetVisitor( self, visitor ):
		if not visitor:
			return
		self.visitor = visitor
		self.onRides = visitor.desiredRides[:]
		self.onRides.sort( ride_cmp )
		self.image = self.origImg.convert()
		color = gui.BLACK
		pos = [0,0]
		tpos = [ self.rect.width -60, 0 ]

		for r in self.onRides:
			image = font.render( r.name, 1, color )
			self.image.blit( image, pos )

			time = formatTime( r.lineup.GetGuess() )
			image = font.render( time, 1, color )
			self.image.blit( image, tpos )

			pos[1] += ascent
			tpos[1] += ascent

		allRides = allobjects.allRides[:]
		self.offRides = [x for x in allRides if x not in self.onRides]

		color = gui.INACTIVE_COLOR
		for r in self.offRides:
			text = r.name
			image = font.render( text, 1, color )
			self.image.blit( image, pos )
			pos[1] += ascent

	def update( self ):
		self.SetVisitor( self.visitor )

	def OnMouseClick( self, pos ):
		if not self.rect.collidepoint( pos ):
			return
		internalPos = (pos[0] - self.rect.x, pos[1] - self.rect.y)
		numRidesOnScreen = self.rect.height / ascent
		index = internalPos[1] / (numRidesOnScreen*2)

		if index < len( self.onRides ):
			ride = self.onRides[index]
			#events.Fire( "RemoveRideReq", ride, self.visitor )
			self.visitor.RemoveRide( ride )
		else:
			try:
				ride = self.offRides[index-len(self.onRides)]
			except IndexError:
				return
			#events.Fire( "AddRideReq", ride, self.visitor )
			self.visitor.AddRide( ride )

class PopCounter:
	def GetInfo( self ):
		return "Population: "+ \
		       str( len( allobjects.allVisitors ) )

#-----------------------------------------------------------------------------
class UIPanel:
	def __init__( self, bgImage, boundRect):
		self.isDone = 0
		self.isDirty = 1
		self.bgImage = bgImage
		self.boundRect = boundRect
		#print self.boundRect

		self.needsReBlit = True
		self.UIGroup = RenderUpdates()

		self.infoObj = None

		yPad = 4

		#labels
		self.todLabel = LabelSprite( "00:00" )
		self.todLabel.rect.midbottom = self.boundRect.midbottom
		self.todLabel.rect.move_ip( -160, -90 )
		self.UIGroup.add( self.todLabel )

		self.infoLabel = LabelSprite( " - " )
		self.infoLabel.rect.x = self.todLabel.rect.x
		self.infoLabel.rect.y = self.todLabel.rect.y + ascent + yPad
		self.UIGroup.add( self.infoLabel )

		self.fpsLabel = LabelSprite( "FPS: 0" )
		self.fpsLabel.rect.x = self.infoLabel.rect.x
		self.fpsLabel.rect.y = self.infoLabel.rect.y + ascent + yPad
		self.UIGroup.add( self.fpsLabel )


		#buttons
		self.pauseButton = ToggleButtonSprite( "pause" )
		self.pauseButton.onClickCallback = self.Pause
		self.pauseButton.rect.topleft = self.boundRect.topleft
		self.pauseButton.rect.move_ip( 0, 10 )
		self.UIGroup.add( self.pauseButton )

		self.rTogButton = ToggleButtonSprite( "red" )
		self.rTogButton.onClickCallback = self.ShowRed
		self.rTogButton.rect.x = self.boundRect.x
		self.rTogButton.rect.y = self.pauseButton.rect.bottom + yPad
		self.UIGroup.add( self.rTogButton )

		self.gTogButton = ToggleButtonSprite( "green" )
		self.gTogButton.onClickCallback = self.ShowGreen
		self.gTogButton.rect.x = self.boundRect.x
		self.gTogButton.rect.y = self.rTogButton.rect.bottom + yPad
		self.UIGroup.add( self.gTogButton )

		self.servButton = ToggleButtonSprite( "server" )
		self.servButton.onClickCallback = self.ShowServer
		self.servButton.rect.x = self.boundRect.x
		self.servButton.rect.y = self.gTogButton.rect.bottom + yPad
		self.UIGroup.add( self.servButton )


		self.device = DeviceSprite()
		self.device.rect.bottomright = self.boundRect.bottomright
		self.device.rect.move_ip( -170, -80 )
		self.UIGroup.add( self.device )

		events.AddListener( self )
		events.AddEvent( "Pause" )
		events.AddEvent( "ShowRed" )
		events.AddEvent( "ShowGreen" )
		events.AddEvent( "ShowServer" )


	#---------------------------------------------------------------------
	def On_FPSChange( self, newfps ):
		self.isDirty = 1
		self.fpsLabel.SetText( "FPS: "+ str(newfps) )

	#---------------------------------------------------------------------
	def On_MouseClick( self, pos ):
		self.isDirty = 1
		self.device.OnMouseClick( pos )
		self.pauseButton.OnMouseClick( pos )
		self.gTogButton.OnMouseClick( pos )
		self.rTogButton.OnMouseClick( pos )
		self.servButton.OnMouseClick( pos )

	#---------------------------------------------------------------------
	def On_MouseMove( self, event ):
		self.isDirty = 1
		self.pauseButton.OnMouseMove( event.pos )
		self.rTogButton.OnMouseMove( event.pos )
		self.gTogButton.OnMouseMove( event.pos )
		self.servButton.OnMouseMove( event.pos )

		if self.infoLabel.rect.collidepoint( event.pos ):
			self.isDirty = 1
			self.infoObj = PopCounter()
			self.infoLabel.SetText( "Population: " + \
			                  str(len(allobjects.allVisitors)) )

	#---------------------------------------------------------------------
	def On_SelectVisitor( self, visitor ):
		self.isDirty = 1
		self.infoObj = visitor
		self.device.SetVisitor( visitor )

	#---------------------------------------------------------------------
	def On_HighlightRide( self, ride ):
		self.isDirty = 1
		self.infoObj = ride

	#---------------------------------------------------------------------
	def On_UnHighlightRide( self ):
		self.isDirty = 1

	#---------------------------------------------------------------------
	def On_HighlightLineup( self, lineup ):
		self.isDirty = 1
		self.infoObj = lineup

	#---------------------------------------------------------------------
	def On_UnHighlightLineup( self ):
		return

	#---------------------------------------------------------------------
	def Click( self, pos ):
		pass
	#---------------------------------------------------------------------
	def MouseOver( self, event ):
		pass

	#---------------------------------------------------------------------
	def Pause( self ):
		events.Fire( "Pause" )

	#---------------------------------------------------------------------
	def ShowRed( self ):
		events.Fire( "ShowRed" )

	#---------------------------------------------------------------------
	def ShowGreen( self ):
		events.Fire( "ShowGreen" )

	#---------------------------------------------------------------------
	def ShowServer( self ):
		events.Fire( "ShowServer" )
		
	#---------------------------------------------------------------------
	def UpdateTimeOfDay( self ):
		self.todLabel.SetText( formatTime( allobjects.timeOfDay ) )
		
	#---------------------------------------------------------------------
	def BGWipe( self, screen, clearArea ):
		srcArea = Rect( clearArea )
		srcArea.move_ip( (-self.boundRect.x, -self.boundRect.y) )
		screen.blit( self.bgImage, clearArea, srcArea )
	#---------------------------------------------------------------------
	def DoGraphics( self, screen, display, timeChange ):
		if self.needsReBlit:
			print 'blitting on screen', self.bgImage, self.boundRect
			screen.blit( self.bgImage, self.boundRect )
			display.flip()
			self.needsReBlit = False

		if self.infoObj:
			self.infoLabel.SetText( self.infoObj.GetInfo() )

		self.UpdateTimeOfDay()

		if not self.isDirty:
			return

		allobjects.server.Tick()

		self.UIGroup.clear(screen, self.BGWipe)

		self.UIGroup.update()

		changedRects =  self.UIGroup.draw(screen)
		display.update( changedRects )
		self.isDirty = 0



if __name__ == '__main__':
	print "Do Tests"
	from pygame.locals import *
	from pygame.sprite import Group, Sprite
	from pygame import Surface
	from classes import TravelBuddyServer

	RESOLUTION = (850,300)

	#Initialize Everything
	#global screen
	screen = None
	pygame.init()
	screen = pygame.display.set_mode(RESOLUTION)
	pygame.display.set_caption('Park Simulation: UI Panel Test')

	#Display The Background
	screen.fill( (0,0,0) )
	try:
		bgSurf = pygame.image.load( simulation.uiBackground )
		screen.blit(bgSurf, (0, 0))
		pygame.display.flip()
	except:
		bgSurf = Surface( RESOLUTION )
		bgSurf.fill( (0,0,0) )
		print "could not load / blit the background image"

	#Prepare Game Objects
	clock = pygame.time.Clock()

	events.AddEvent( "FPSChange" )

	displayer  = UIPanel( bgSurf, Rect(0,0,*RESOLUTION) )
	allobjects.server = TravelBuddyServer()
	lastReload = 0

	#Main Loop
	oldfps = 0

	while 1:
		timeChange = clock.tick(simulation.fps)
		lastReload += timeChange
		if lastReload > 5000:
			lastReload = 0
			reload(simulation)
		newfps = int(clock.get_fps())
		if newfps != oldfps:
			events.Fire( "FPSChange", newfps )
			oldfps = newfps

		#Handle Input Events
		remainingEvents = pygame.event.get()
		for event in remainingEvents:
			if event.type == QUIT:
				displayer.isDone = 1
			elif event.type == KEYDOWN and event.key == K_ESCAPE:
				displayer.isDone = 1
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

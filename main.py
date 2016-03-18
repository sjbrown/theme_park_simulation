#!/usr/bin/env python
#Import Modules
#import SiGL
import os, pygame, operator, math
from copy import copy
from inspect import isclass
from pygame.locals import *
from pygame import Surface
from pygame.sprite import Group, Sprite

from log import log

RESOLUTION = (1024,768)


from park_geography import ParkGeography
from parkpanel import ParkPanel
from classes import TravelBuddyServer
import allobjects
import events

try:
	import simulation
except:
	print "COULD NOT FIND SIMULATION DEFINITION"
	print "USING BACKUP INSTEAD"
	import simulation_backup as simulation

#-----------------------------------------------------------------------------
def main():
	"""this function is called when the program starts.
	   it initializes everything it needs, then runs in
	   a loop until the function returns."""
	#Attempt to optimize with psyco
	try:
		import psyco
		psyco.full()
	except Exception, e:
		print "no psyco for you!", e


	#Initialize Everything
	global screen
	screen = None
	pygame.init()

	#UI Panel must be imported after pygame.init()
	from uipanel import UIPanel
	from utils import load_png

	if simulation.fullscreen:
		screen = pygame.display.set_mode(RESOLUTION, 
		                                 HWSURFACE|DOUBLEBUF|FULLSCREEN)
	else:
		screen = pygame.display.set_mode(RESOLUTION, 
		                                 HWSURFACE|DOUBLEBUF)
	pygame.display.set_caption('Park Simulation')

	#Display The Background

        try:
                bgSurf = pygame.image.load( simulation.parkBackground )
                screen.blit(bgSurf, (0,0))
                pygame.display.flip()
        except:
                bgSurf = Surface( RESOLUTION )
                bgSurf.fill( (0,0,0) )
                print "could not load / blit the background image"

	uiSurf = Surface( RESOLUTION )
	uiSurf.fill( (50,50,250) )
	uiSurf = load_png( 'ui_bg.png' )


	#Prepare game objects
	allobjects.server = TravelBuddyServer()
	parkPanel  = ParkPanel(bgSurf, (0,0) )
	uiPanel = UIPanel( uiSurf, Rect(0,parkPanel.boundRect.bottom,
	                   RESOLUTION[0],
	                   RESOLUTION[1]-parkPanel.boundRect.height) )
	fauxScreen = Surface( (screen.get_width(), uiPanel.boundRect.height) )


	events.AddEvent( "FPSChange" )
	events.AddEvent( "MouseMove" )
	events.AddEvent( "MouseClick" )

	lastReload = 0
	clock = pygame.time.Clock()
	oldfps = 0
	nextGUIRefresh = 1
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

		allobjects.thousandCounter += 1
		allobjects.thousandCounter %= 1000

		#Handle Input Events
		remainingEvents = pygame.event.get()
		for event in remainingEvents:
			upKeys = [x for x in remainingEvents if x.type == KEYUP]
			if event.type == QUIT:
				return
			elif event.type == KEYDOWN and event.key == K_ESCAPE:
				return
			elif event.type == KEYDOWN or event.type == KEYUP:
				parkPanel.SignalKey( event, upKeys )
			elif event.type == MOUSEBUTTONDOWN:
				events.Fire( "MouseClick", event.pos )
			if event.type == MOUSEMOTION:
				events.Fire( "MouseMove", event )

		#Draw Everything
		parkPanel.DoGraphics( screen, pygame.display, timeChange )
		if allobjects.thousandCounter == nextGUIRefresh:
			uiPanel.DoGraphics( screen, pygame.display, timeChange )
			nextGUIRefresh += 30
			nextGUIRefresh %= 1000


		# if the displayer is done, it's time to switch to 
		# a different displayer.  Sometimes the displayer doesn't
		# know what should come after it is done.
		# If we can't figure it out, default to the Main Menu
		if parkPanel.isDone:
			log.debug( "DISPLAYER IS DONE" )
			#if the displayer was the quit screen, we should quit
			if isinstance( parkPanel, QuitScreen ):
				break

			# clear out the old blitted image
			bgMangr.GetBgSurface(screen, screen.get_rect())
			pygame.display.flip()

			nextDisplayer = parkPanel.replacementDisplayerClass
			if isclass( nextDisplayer ):
				parkPanel = nextDisplayer(bgMangr, musicMangr)
			else:
				parkPanel = MainMenu(bgMangr, musicMangr)



	#Game Over
	print "Game is over"

	pygame.quit()

#this calls the 'main' function when this script is executed
if __name__ == '__main__': main()

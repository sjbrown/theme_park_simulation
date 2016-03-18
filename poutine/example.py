#!/usr/bin/env python
#Import Modules
#import SiGL
import os, pygame, string
from pygame.locals import *
from pygame.sprite import Group, Sprite, RenderUpdates
from gui_widgets import *
RESOLUTION = (800,600)
BGCOLOR = (100,100,100)


	
#-----------------------------------------------------------------------------
def main():
	"""this function is called when the program starts.
	   it initializes everything it needs, then runs in
	   a loop until the function returns."""
#Initialize Everything
	global screen
	screen = None
	pygame.init()
	screen = pygame.display.set_mode(RESOLUTION)
	pygame.display.set_caption('Example Poutine Window')

#Create The Backgound
	bg = pygame.Surface( RESOLUTION )
	bg.fill( BGCOLOR )

#Display The Background
	screen.blit(bg, (0, 0))
	pygame.display.flip()

#Prepare Game Objects
	clock = pygame.time.Clock()

	label = LabelSprite( 'foo' )
	label.rect.move_ip( 100, 100 )
	#this will be the callback function of the button
	def buttonWasClicked():
		print "button clicked"
	button = ButtonSprite( 'bar', None, buttonWasClicked )
	button.rect.move_ip( 100, 300 )

	tEntry = TextEntrySprite('textentry')
	tEntry.rect.move_ip( 100, 400 )

	allWidgets = RenderUpdates()
	allWidgets.add( label )
	allWidgets.add( button )
	allWidgets.add( tEntry )



#Main Loop
	while 1:
		timeChange = clock.tick(40)

	#Handle Input Events
		oldEvents = []
		remainingEvents = pygame.event.get()
		for event in remainingEvents:
			oldEvents.append( remainingEvents.pop(0) )
			if event.type == QUIT:
				return
			elif event.type == KEYDOWN and event.key == K_ESCAPE:
				return

			elif event.type == KEYDOWN:
				key = event.unicode.encode("ascii")
				if key and key in string.printable:
					for s in  allWidgets.sprites():
						if hasattr( s, "OnKeyPressed" ):
							s.OnKeyPressed( key )
				else:
					key = event.key
					for s in  allWidgets.sprites():
						if hasattr( s, "OnMetaPressed"):
							s.OnMetaPressed( key )
			elif event.type == MOUSEMOTION:
				for sprite in  allWidgets.sprites():
					if hasattr( sprite, "OnMouseMove" ):
						sprite.OnMouseMove( event.pos )
			elif event.type == MOUSEBUTTONDOWN:
				for sprite in  allWidgets.sprites():
					if hasattr( sprite, "OnMouseClick" ):
						sprite.OnMouseClick( event.pos )

	#Draw Everything
		allWidgets.clear( screen, bg )
		allWidgets.update( )
		changedRects =  allWidgets.draw(screen)
		pygame.display.update( changedRects )


#Game Over
	pygame.quit()


#this calls the 'main' function when this script is executed
if __name__ == '__main__': main()

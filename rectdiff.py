#! /usr/bin/python

from pygame import Rect

def GetEmptyRects( masterRect, subRects ):
	masterRects = [ masterRect ]
	for r in subRects:
		newMasters = []
		for m in masterRects:
			#print 'splitting', m, 'by', r
			results = SubtractRect( m, r )
			#print 'result', results
			newMasters += results
		masterRects = newMasters
		#print ""
		#print 'new masters', newMasters

	return masterRects
	
	

def SubtractRect( masterRect, containedRect ):
	if not masterRect.colliderect( containedRect ):
		return [masterRect]
	result = []
	topBun = Rect( masterRect.x, masterRect.y, 
	               masterRect.width,
	               (containedRect.y - masterRect.top) )
	if topBun.height > 0:
		result.append( topBun )

	bottomBun = Rect( masterRect.x, containedRect.bottom,
	                  masterRect.width,
	                  (masterRect.bottom - containedRect.bottom) )
	if bottomBun.height > 0:
		result.append( bottomBun )

	topMaximum = max(masterRect.top,containedRect.top)
	botMinimum = min(containedRect.bottom, masterRect.bottom)

	#print 'bmin - tmax', botMinimum, topMaximum, botMinimum-topMaximum

	leftMeat = Rect( masterRect.x, 
	                 topMaximum,
	                 containedRect.left - masterRect.left,
	                 botMinimum-topMaximum
	               )
	if leftMeat.width > 0:
		result.append( leftMeat )

	rightMeat = Rect( containedRect.right, 
	                  topMaximum,
	                  (masterRect.right - containedRect.right),
	                  botMinimum-topMaximum
	                )
	if rightMeat.width > 0:
		result.append( rightMeat )

	return result


if __name__ == '__main__':
	print 'Do Tests'
	r1 = Rect( 0,0,800,800 )
	r2 = Rect( 50,50,10,10 )
	r3 = Rect( -100,0,200,200 )
	r4 = Rect( 500,500,100,100 )
	r5 = Rect( 620,400,100,200 )
	r6 = Rect( 100,40,100,400 )
	r7 = Rect( 200,40,100,100 )
	r8 = Rect( 500,40,100,600 )

	fulls = [r2,r3]
	fulls = [r2]
	fulls = [r2,r4]
	fulls = [r4,r5]
	fulls = [r6,r7,r8]
	#print GetEmptyRects( r1, fulls )

	empties= GetEmptyRects( r1, fulls )
	#print 'empties', empties

	#Initialize Everything
	from pygame.locals import *
	import pygame
	global screen
	pygame.init()
	screen = pygame.display.set_mode((r1.width, r1.height))

	#Display The Background
	screen.fill( (0,0,0) )
	#screen.blit(bgMangr.GetBackground(), (0, 0))
	pygame.display.flip()

	blue = (0,0,200)
	red = (200,0,200)
	quit = 0
	i = 0

	color = list(blue)

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
		e = empties[ i%len(empties) ]
		s = pygame.Surface( e.size )
		color[1] = (color[1]+61)%256
		s.fill( color )
		screen.blit( s, e.topleft )
		pygame.display.flip()
		if not i%8:
			for f in fulls:
				s = pygame.Surface( f.size )
				s.fill( red )
				screen.blit( s, f.topleft )
		time.sleep(0.5)
		pygame.display.flip()


	pygame.quit()

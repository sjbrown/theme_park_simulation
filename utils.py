#!/usr/bin/env python
from pygame.locals import *
from log import log
import pygame
import os

#-----------------------------------------------------------------------------
def vectorSum ( a, b ):
	return [a[0]+b[0], a[1]+b[1]]

datadir = '.'
#-----------------------------------------------------------------------------
def load_png(name, extradirs=None):
	if extradirs:
		fullname = os.path.join(datadir, extradirs, name)
	else:
		fullname = os.path.join(datadir, name)
	try:
		image = pygame.image.load(fullname)
		if image.get_alpha is None:
			image = image.convert()
		else:
			image = image.convert_alpha()
	except pygame.error, message:
		log.debug( ' Cannot load image: '+ fullname )
		log.debug( 'Raising: '+ str(message) )
		raise message
	return image

#this calls the 'main' function when this script is executed
if __name__ == '__main__': print "didn't expect that!"

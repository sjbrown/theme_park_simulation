#!/usr/bin/env python
"""
The utils module is basically just a handy load_png function
"""


#Import Modules
import os, pygame
from pygame.locals import *

	

#-----------------------------------------------------------------------------
def load_png(name, extradir=''):
    """Handy function to load a PNG.  Stolen from Chimp Tutorial.
    Expects PNG files to be in a subdirectory named data/"""

    if isinstance(name, list):
	    fullname = 'data'
	    for component in name:
	    	fullname = os.path.join(fullname, component)
    else:
    	fullname = os.path.join('data', extradir, name)
    try:
        image = pygame.image.load(fullname)
	if image.get_alpha is None:
		image = image.convert()
	else:
		image = image.convert_alpha()
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    return image


#this calls the 'main' function when this script is executed
if __name__ == '__main__': print "didn't expect that!"

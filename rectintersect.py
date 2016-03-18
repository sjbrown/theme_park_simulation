#! /usr/bin/python

from pygame import Rect

def IntersectRect( rectA, rectB ):
	if not rectA.colliderect( rectB ):
		print 'no collision', rectA, rectB
		return None

	x = max( rectA.x, rectB.x )
	y = max( rectA.y, rectB.y )
	width = min( rectA.right, rectB.right ) - x
	height = min( rectA.bottom, rectB.bottom ) - y

	return Rect( x,y,width,height )


if __name__ == '__main__':
	print 'Do Tests'

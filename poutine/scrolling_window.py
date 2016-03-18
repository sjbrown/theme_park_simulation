import pygame
from pygame.locals import *

from gui_widgets import *
from utils import load_png
from copy import copy

DARKGREY = (90,90,90)

#------------------------------------------------------------------------------
class ScrolledIconWindow( WidgetAndContainer ):
	"""This is a simple scrolling widget that has left and right 
	scrollbuttons and can only scroll left to right, not up & down"""
	#----------------------------------------------------------------------
	def __init__(self, widgets, container=None, dimensions=(400,150) ):
		WidgetAndContainer.__init__( self, container )

		self.image = pygame.Surface( dimensions, SRCALPHA )
		self.image.fill( DARKGREY )
		self.rect = self.image.get_rect()
		#copy the rect
		self.scrollState = self.rect.move( 0,0 )

		self.leftButton = ScrollButton( self, self.OnScrollLeftRequest,
		                                'left' )
		self.widgets.append( self.leftButton )
		self.rightButton = ScrollButton(self, self.OnScrollRightRequest,
		                                'right' )
		self.widgets.append( self.rightButton )

		self.widgets += widgets
		
		# find the dimensions of the scrollSurface.  Note this window
		# only scrolls left to right, so we don't have to add up the
		# heights, only the widths
		self.xPadding = 4
		self.yPadding = 4
		maxHeight = 0
		maxWidth  = 0
		for sprite in self.widgets:
			maxWidth += sprite.rect.width + self.xPadding
			maxHeight = max( sprite.rect.height, maxHeight )
		maxHeight += self.yPadding
		self.scrollSurface = pygame.Surface((maxWidth, maxHeight), SRCALPHA)

		self.ArrangeWidgets()
		self.update()

	#----------------------------------------------------------------------
	def ArrangeWidgets(self):
		self.dirty = 1
		xOffset = 0
		yOffset = 0
		xMax = self.scrollSurface.get_width()
		yMax = self.scrollSurface.get_height()
		xCounter = xOffset

		self.widgets[0].rect.bottomleft = (0,self.rect.height)
		self.widgets[1].rect.bottomright = (self.rect.width,self.rect.height)

		#the first two widgets are the left and right buttons,
		#so we just need to arrange the remainder
		for wid in self.widgets[2:]:
			wid.rect.x = xCounter + self.xPadding
			wid.rect.y = yOffset 
			xCounter = wid.rect.right
			print "put ", wid, "at ", wid.rect.x

			#Check to see if we didn't screw it up...
			if wid.rect.left > xMax \
			  or wid.rect.top > yMax:
				print wid, self
				raise Exception( "ScrolledWindow Wrong Size")


	#----------------------------------------------------------------------
	def update(self):
		if not self.dirty:
			return

		for sprite in self.widgets[2:]:
			sprite.update()
			self.scrollSurface.blit( sprite.image, sprite.rect )

		self.image.blit( self.scrollSurface, (0,0), self.scrollState )
		self.image.blit( self.leftButton.image, self.leftButton.rect )
		self.image.blit( self.rightButton.image, self.rightButton.rect )

	#----------------------------------------------------------------------
	def OnScrollRequest( self, amount ):
		self.dirty = 1

		self.scrollState.x += amount
		boundLeft = 0
		boundRight = self.scrollSurface.get_width()
		if self.scrollState.left < boundLeft:
			self.scrollState.left = boundLeft
		if self.scrollState.right > boundRight:
			self.scrollState.right = boundRight

	#----------------------------------------------------------------------
	def OnScrollLeftRequest( self ):
		return OnScrollRequest( -5 )
	#----------------------------------------------------------------------
	def OnScrollRightRequest( self ):
		return OnScrollRequest( 5 )

	#----------------------------------------------------------------------
 	def OnMouseClick(self, pos):
		if self.rect.collidepoint( pos ):
			self.PassMouseEventThrough( "OnMouseClick", pos )
		elif self.focused:
			self.SetFocus(0)

	#----------------------------------------------------------------------
 	def OnMouseMove(self, pos):
		if self.rect.collidepoint( pos ):
			self.SetHoverHighlight(1)
			self.PassMouseEventThrough( "OnMouseClick", pos )
		elif self.highlighted:
			self.SetHoverHighlight(0)

	#----------------------------------------------------------------------
 	def PassMouseEventThrough(self, eventName, pos):
		"""Passes the event through to the widgets contained inside
		the scrolling window"""
		pos = list(pos)
		pos[0] = pos[0] - self.rect.x
		pos[1] = pos[1] - self.rect.y
		#if the mouse event isn't on the scrollbar...
		if pos[1] < self.leftButton.rect.top:
			pos[0] = pos[0] + self.scrollState.x
			pos[1] = pos[1] + self.scrollState.y
		pos = tuple(pos)

		for widget in self.widgets:
			if widget.__dict__.has_key( eventName ):
				widget.__dict__[ eventName ]( pos )

		
#------------------------------------------------------------------------------
class ScrollButton(ButtonSprite):
	"""A button to be placed at the end of the scrollbar (or anywhere,
	really - it's up to the developer) that controls the current view
	offset of the ScrollingWindow.  Clicking on it scrolls the view
	to the left or the right (actually that's controlled by the callback
	sent to the constructor"""
	#----------------------------------------------------------------------
	def __init__(self, container=None, onClickEvent, direction ):
		ButtonSprite.__init__( self, container, onClickEvent )

		assert( direction in ['up','right','down','left'] )

		# Tries to load an image that looks like scroll_up.png
		try:
			self.image = load_png( 'scroll_'+ direction +'.png' )
		except:	
			#TODO: make some font image with ^>V<
			pass
		self.rect = self.image.get_rect()

		self.originalRect = None

	#----------------------------------------------------------------------
	def update(self):
		#TODO: update() never gets called.  need to add an update call
		# to the parent
		if not self.dirty:
			return

		if self.focused:
			if not self.originalRect:
				self.originalRect = self.rect.move( 0,0 )
			self.rect = self.originalRect.move( 2,2 )	
		else:
			if self.originalRect:
				self.rect.topleft = self.originalRect.topleft
				self.originalRect = None

		self.dirty = 0



if __name__ == "__main__":
	print "that was unexpected"

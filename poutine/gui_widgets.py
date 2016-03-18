import pygame
from pygame.constants import *

vectorSum = lambda a,b: (a[0]+b[0], a[1]+b[1])

FONTFACE = None
FONTSIZE = 18

BLACK             = (0,0,0)
LINE_COLOR        = (0,0,100)
INACTIVE_COLOR    = (200,200,200)
HIGLIGHT_COLOR    = (255,0,0)
FOCUSED_COLOR     = (255,255,0)
NORMAL_COLOR      = (100,0,0)
GREY_COLOR        = (100,100,100)

CONFIRM_KEYS = [ K_SPACE, K_RETURN ]
FOCUS_CYCLE_KEYS = [ K_TAB ]


#------------------------------------------------------------------------------
class Widget(pygame.sprite.Sprite):
	def __init__(self, container=None):
		pygame.sprite.Sprite.__init__(self)

		self.container = container
		self.focused = 0
		self.highlighted = 0
		self.dirty = 1

	#----------------------------------------------------------------------
 	def kill(self):
		self.container = None
		del self.container
		pygame.sprite.Sprite.kill(self)

	#----------------------------------------------------------------------
	def SetFocus(self, val):
		self.focused = val
		self.dirty = 1

	#----------------------------------------------------------------------
 	def SetHoverHighlight(self, value):
		self.highlighted = value
		self.dirty = 1

	#----------------------------------------------------------------------
 	def OnGetFocus(self, event):
		self.SetFocus(1)

	#----------------------------------------------------------------------
 	def OnLoseFocus(self, event):
		self.SetFocus(0)


#------------------------------------------------------------------------------
class LabelSprite(Widget):
	def __init__(self, text, container=None):
		Widget.__init__( self, container)

		self.color = INACTIVE_COLOR
		self.font = pygame.font.Font(FONTFACE, FONTSIZE)
		self.__text = text
		self.image = self.font.render( self.__text, 1, self.color)
		self.rect  = self.image.get_rect()

	#----------------------------------------------------------------------
	def update(self):
		if not self.dirty:
			return

		self.image = self.font.render( self.__text, 1, self.color )
		self.dirty = 0

	#----------------------------------------------------------------------
	def SetText(self, text):
		self.__text = text
		self.dirty = 1


#------------------------------------------------------------------------------
class ButtonSprite(Widget):
	def __init__( self, text, container=None, 
	              onClickCallback=None, callbackArgs=() ):
		Widget.__init__( self, container )

		self.font = pygame.font.Font(FONTFACE, FONTSIZE)
		self.text = text
		self.image = self.font.render( self.text, 1, NORMAL_COLOR )
		self.rect  = self.image.get_rect()


		self.onClickCallback = onClickCallback
		self.callbackArgs = callbackArgs

	#----------------------------------------------------------------------
	def update(self):
		if not self.dirty:
			return

		if self.focused:
			color = FOCUSED_COLOR
		elif self.highlighted:
			color = HIGLIGHT_COLOR
		else:
			color = NORMAL_COLOR
		self.image = self.font.render( self.text, 1, color )
		#self.rect  = self.image.get_rect()

		self.dirty = 0

	#----------------------------------------------------------------------
	def Click(self):
		self.dirty = 1
		if self.onClickCallback:
			self.onClickCallback( *self.callbackArgs )

	#----------------------------------------------------------------------
 	def OnKeyPressed(self, key):
		if self.focused and key in CONFIRMKEYS:
			self.Click()

	#----------------------------------------------------------------------
 	def OnMouseClick(self, pos):
		if self.rect.collidepoint( pos ):
			self.Click()
		elif self.focused:
			self.SetFocus(0)

	#----------------------------------------------------------------------
 	def OnMouseMove(self, pos):
		if self.rect.collidepoint( pos ):
			self.SetHoverHighlight(1)
		elif self.highlighted:
			self.SetHoverHighlight(0)

			
#------------------------------------------------------------------------------
class TextBoxSprite(Widget):
	def __init__(self, width, container=None ):
		Widget.__init__( self, container)

		self.font = pygame.font.Font(FONTFACE, FONTSIZE)
		linesize = self.font.get_linesize()

		self.rect = pygame.Rect( (0,0,width, linesize +4) )
		boxImg = pygame.Surface( self.rect.size ).convert_alpha()
		color = LINE_COLOR
		pygame.draw.rect( boxImg, color, self.rect, 4 )

		self.emptyImg = boxImg.convert_alpha()
		self.image = boxImg

		self.highlighted = 0
		self.text = ''
		self.textPos = (22, 2)

	#----------------------------------------------------------------------
	def update(self):
		if not self.dirty:
			return

		text = self.text
		if self.focused:
			text += '|'
			color = FOCUSED_COLOR
		elif self.highlighted:
			color = HIGLIGHT_COLOR
		else: 
			color = NORMAL_COLOR

		textImg = self.font.render( text, 1, color )
		self.image.blit( self.emptyImg, (0,0) )
		self.image.blit( textImg, self.textPos )

		self.dirty = 0

	#----------------------------------------------------------------------
	def Click(self):
		self.focused = 1
		self.dirty = 1

	#----------------------------------------------------------------------
	def SetText(self, newText):
		self.text = newText
		self.dirty = 1

	#----------------------------------------------------------------------
 	def OnKeyPressed(self, key):
		newText = self.text + key
		self.SetText( newText )

	#----------------------------------------------------------------------
	def OnMetaPressed( self, key ):
		if self.focused and key in FOCUS_CYCLE_KEYS:
			#don't respond to the focus cycle keys
			return
		if self.focused and key == K_BACKSPACE:
		  	#strip of last character
		  	newText = self.text[:-1]
			self.SetText( newText )

	#----------------------------------------------------------------------
 	def OnMouseClick(self, pos):
		if self.rect.collidepoint( pos ):
			self.Click()
		elif self.focused:
			self.SetFocus(0)

	#----------------------------------------------------------------------
 	def OnMouseMove(self, pos):
		if self.rect.collidepoint( pos ):
			self.SetHoverHighlight(1)
		elif self.highlighted:
			self.SetHoverHighlight(0)


#------------------------------------------------------------------------------
class WidgetContainer:
	def __init__(self, rect):
		self.rect = rect

		self.widgets = [ ]

	#----------------------------------------------------------------------
 	def kill(self):
		for sprite in self.widgets:
			sprite.kill()
		while len( self.widgets ) > 0:
			wid = self.widgets.pop()
			del wid
		del self.widgets

	#----------------------------------------------------------------------
 	def ArrangeWidgets(self, xPadding=20, yPadding=100):
		xOffset = self.rect.x
		yOffset = self.rect.y

		xStep = 1
		yStep = 1
		for wid in self.widgets:
			wid.rect.x = xOffset + (xPadding*xStep)
			wid.rect.y = yOffset + (yPadding*yStep)

			#Check to see if we didn't screw it up...
			if wid.rect.left > self.rect.right \
			  or wid.rect.top > self.rect.bottom:
				print wid, self
				print wid.rect, self.rect
				raise Exception( "Widget Outside Container")

			yStep += 1
			if yStep*yPadding > self.rect.height:
				yStep = 1
				xStep += 1

	#----------------------------------------------------------------------
 	def ChangeFocusedWidget(self, change):
		currentlyFocused = None

		for wid in self.widgets:
			if wid.focused:
				currentlyFocused = self.widgets.index(wid)
				break

		#no widget was focused
		if currentlyFocused == None:
			currentlyFocused = 0
			self.widgets[currentlyFocused].SetFocus(1)
			return

		widgetToFocus = currentlyFocused + change

		# the desired index is out of range
		# ( subclasses might want to change focus to sibling
		#   WidgetContainer instances in this case )
		if widgetToFocus <= -1  \
		  or widgetToFocus >= len( self.widgets ):
			widgetToFocus = widgetToFocus % len(self.widgets)

		self.widgets[currentlyFocused].SetFocus(0)
		self.widgets[widgetToFocus].SetFocus(1)


	#----------------------------------------------------------------------
	def OnKeyPressed( self, key ):
		if key in FOCUS_CYCLE_KEYS:
			self.ChangeFocusedWidget(1)
			#todo: check for shift
			#self.ChangeFocusedWidget(-1)
	#----------------------------------------------------------------------
	def OnMetaPressed( self, key ):
		if key in FOCUS_CYCLE_KEYS:
			self.ChangeFocusedWidget(1)
			#todo: check for shift
			#self.ChangeFocusedWidget(-1)



#------------------------------------------------------------------------------
class WidgetAndContainer( Widget, WidgetContainer ):
	#----------------------------------------------------------------------
	def __init__(self, container):
		Widget.__init__( self, container)

		self.widgets = [ ]

	#----------------------------------------------------------------------
 	def kill(self):
		WidgetContainer.kill(self)
		Widget.kill(self)


#------------------------------------------------------------------------------
class TextEntrySprite(WidgetAndContainer):
	def __init__(self, labelText, container=None ):
		WidgetAndContainer.__init__( self, container )


		self.widgets = [ LabelSprite( labelText, container=self ),
		                 TextBoxSprite( 200, container=self ),
		               ]
		width = self.widgets[0].rect.width \
		        + self.widgets[1].rect.width + 10
		height = self.widgets[1].rect.height

		self.image = pygame.Surface( (width, height) )
		self.image.fill( BLACK )

		self.background = self.image.convert_alpha()
		self.rect = self.image.get_rect()

	#----------------------------------------------------------------------
	def update(self):
		if not self.dirty:
			return

		self.ArrangeWidgets()

		self.image.blit( self.background, [0,0] )
		for wid in self.widgets:
			wid.update()
			destpos = [wid.rect.x - self.rect.x,
				   wid.rect.y - self.rect.y ]
			self.image.blit( wid.image, destpos )

		self.dirty = 0

	#----------------------------------------------------------------------
 	def ArrangeWidgets(self):
		xyOffset = ( self.rect.x, self.rect.y )
		self.widgets[0].rect.topleft = vectorSum( xyOffset, (0,0) ) 
		x = self.widgets[0].rect.width + 10
		self.widgets[1].rect.topleft = vectorSum( xyOffset, (x,0) ) 

	#----------------------------------------------------------------------
 	def CheckDirty(self):
		#See if we're dirty
		for wid in self.widgets:
			if wid.dirty:
				self.dirty = 1
				break

	#----------------------------------------------------------------------
 	def OnMouseClick(self, pos):
		if self.rect.collidepoint( pos ):
			self.SetFocus(1)
			for wid in self.widgets:
				if hasattr( wid, 'OnMouseClick' ):
					wid.OnMouseClick( pos )
		elif self.focused:
			self.SetFocus(0)
		self.CheckDirty()

	#----------------------------------------------------------------------
 	def OnMouseMove(self, pos):
		if self.rect.collidepoint( pos ):
			self.SetHoverHighlight(1)
			for wid in self.widgets:
				if hasattr( wid, 'OnMouseMove' ):
					wid.OnMouseMove( pos )
		elif self.highlighted:
			self.SetHoverHighlight(0)
		self.CheckDirty()

	#----------------------------------------------------------------------
 	def OnKeyPressed(self, key):
		WidgetAndContainer.OnKeyPressed( self, key )
		if self.focused:
			for wid in self.widgets:
				if hasattr( wid, 'OnKeyPressed' ):
					wid.OnKeyPressed( key )
		self.CheckDirty()

	#----------------------------------------------------------------------
 	def OnMetaPressed(self, key):
		WidgetAndContainer.OnMetaPressed( self, key )
		if self.focused:
			for wid in self.widgets:
				if hasattr( wid, 'OnMetaPressed' ):
					wid.OnMetaPressed( key )
		self.CheckDirty()



if __name__ == "__main__":
	print "that was unexpected"

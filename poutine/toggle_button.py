
#------------------------------------------------------------------------------
class ToggleButtonSprite(ButtonSprite):
	def __init__( self, text, container=None, 
	              onClickCallback=None, callbackArgs=() ):
		ButtonSprite.__init__( self, container,
		                       onClickCallback, callbackArgs )

		self.toggleState = False
		self.image = self.font.render( self.text, 1, GREY_COLOR )
		self.rect  = self.image.get_rect()

	#----------------------------------------------------------------------
	def update(self):
		if not self.dirty:
			return

		if self.focused:
			color = FOCUSED_COLOR
		elif self.highlighted:
			color = HIGLIGHT_COLOR
		elif self.toggleState:
			color = NORMAL_COLOR
		else:
			color = GREY_COLOR
		self.image = self.font.render( self.text, 1, color )

		self.dirty = 0

	#----------------------------------------------------------------------
	def Click(self):
		self.toggleState = not self.toggleState
		ButtonSprite.Click(self)

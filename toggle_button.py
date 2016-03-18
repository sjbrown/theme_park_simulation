from poutine.gui_widgets import ButtonSprite
from utils import load_png
#------------------------------------------------------------------------------
class ToggleButtonSprite(ButtonSprite):
	def __init__( self, name, container=None, 
	              onClickCallback=None, callbackArgs=(),
	              ):
		ButtonSprite.__init__( self, container,
		                       onClickCallback, callbackArgs )

		self.toggleState = False
		self.onImage = load_png( 'btn_tog_'+ name +'_on.png' )
		self.offImage = load_png( 'btn_tog_'+ name +'_off.png' )
		self.image = self.offImage
		self.rect  = self.image.get_rect()

	#----------------------------------------------------------------------
	def update(self):
		if not self.dirty:
			return

		if self.toggleState:
			self.image = self.onImage
		else:
			self.image = self.offImage

		self.dirty = 0

	#----------------------------------------------------------------------
	def Click(self):
		self.toggleState = not self.toggleState
		ButtonSprite.Click(self)

#! /usr/bin/python

from move_matrix import MoveMatrix
import allobjects
from pygame.locals import *
from pygame.sprite import Sprite
from pygame import Rect, Surface
import pygame

try:
	import simulation
except:
	print "COULD NOT FIND SIMULATION DEFINITION"
	print "USING BACKUP INSTEAD"
	import simulation_backup as simulation

class Lineup(Sprite):
	def __init__(self, size=[20,12], lineType=None):
		Sprite.__init__(self)
		width = size[0] * simulation.pixelsPerMeter
		height = size[1] * simulation.pixelsPerMeter
		self.rect = Rect( 0,0, width, height )
		self.image = Surface( self.rect.size, pygame.SRCALPHA, 32 )
		self.image.fill( (10,10,10,50) )
		pygame.draw.rect( self.image, (20,0,200,200), self.rect, 8 )

		self.visitors = []
		self.ride = None
		self.hotspot = self.rect.center

		self.analysisGuess = 0
		self.trendGuessDict = { 0:0 }
		self.durationGuess = 0

		if lineType == None:
			lineType = longSparseLine
		self._mMatrix = MoveMatrix(lineType)

	def __str__( self ):
		return "Lineup"+ str(id(self)) +str(self.rect.center)

	def GetEntryPoint( self ):
		return self.GetMoveMatrix().GetStartPos()

	def SetHotspot( self, hotspot ):
		self.hotspot = hotspot

	def GetMoveMatrix( self ):
		self._mMatrix.transform( self.rect )
		return self._mMatrix

	def GetFrontOfLineVisitors( self, howMany ):
		head = self.visitors[:howMany]
		turnstiles = self._mMatrix.GetLast( howMany )
		legitRiders = [v for v in head if v.rect.center in turnstiles]
		#if len(popGroup) != len(legitRiders):
			###print "werent' that many legit riders"
			###print head
			###print legitRiders
			###print self._mMatrix.GetLast(howMany)
			###print "---------------"
			#pass
		return legitRiders

	def GetLength( self ):
		return len( self.visitors )

	def GetGuess( self ):
		return self.durationGuess

		#TODO: the rest of this fn

		try:
			trendGuess = self.trendGuessDict[allobjects.timeOfDay]
		except KeyError:
			trendGuess = None
		#TODO: trendGuess

		guess = (self.analysisGuess + self.durationGuess ) /2

		return guess

	def GetInfo(self):
		return "Length: " + str(self.GetLength())

	def AddVisitor( self, visitor ):
		self.visitors.append( visitor )

	def PopVisitors( self, howMany=1 ):
		folVisitors = self.GetFrontOfLineVisitors(howMany)
		#if folVisitors:
			#print 'frontofline visitors:', folVisitors
		for v in folVisitors:
			self.visitors.remove( v )
		return folVisitors


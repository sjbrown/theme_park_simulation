#! /usr/bin/python

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

class Car(Sprite):
	IDLE = 0
	RUNNING = 1
	def __init__(self, ride, centerPos):
		Sprite.__init__(self)
		self.visitors = []
		self.ride = ride
		self.duration = ride.carDuration
		self.state = Car.IDLE
		self.seatCounter = 0

		from classes import Visitor
		capacity = ride.carCapacity
		width = Visitor.size[0]+2
		length = (Visitor.size[1]+1)*capacity + 1
		self.image = Surface( (width, length) )
		self.image.fill( (0,0,0) )
		self.rect = self.image.get_rect()
		self.rect.center = centerPos

	def __repr__(self):
		return "Car "+ str(id(self)) +' '+ str(self.rect.center)

	def update(self):
		if self.state == Car.IDLE:
			return
		self.duration -= 1
		if self.duration <= 0:
			self.ride.LandCar( self )
			self.duration = self.ride.carDuration

	def Empty(self):
		self.visitors = []
		self.seatCounter = 0

	def TakeSeat(self):
		self.seatCounter += 1
		from classes import Visitor
		return (self.rect.centerx, self.rect.top+(1+Visitor.size[1])*self.seatCounter)

class Ride(Sprite):
	def __init__( self, topleft, size=[20,50] ):
		Sprite.__init__(self)
		width = size[0] * simulation.pixelsPerMeter
		height = size[1] * simulation.pixelsPerMeter
		self.rect = Rect( 0,0, width, height )
		self.image = Surface( self.rect.size, pygame.SRCALPHA, 32 )
		self.image.fill( (10,10,10,0) )
		pygame.draw.rect( self.image, (200,0,200,200), self.rect, 8 )

		self.rect.topleft = topleft

		self.carDuration = 150
		self.carCapacity = 5
		self.numCars = 3
		self.minimumCarPadding = 60
		self.rideDuration = 120
		self.idleCars = []
		self.runningCars = []

		carPosition = [self.rect.x+4, self.rect.centery]
		from classes import Visitor
		for i in range(self.numCars):
			self.idleCars.append( Car(self, carPosition) )
			carPosition[0] = carPosition[0] + Visitor.size[0]+5

		self.carPaddingCounter = self.minimumCarPadding

		self.lineup = None
		self.name = str(self.rect)

		self.ejectLocation = None

	def __str__( self ):
		return "Ride"+ str(id(self)) +str(self.rect.center)

	def SetEjectLocation(self, pos):
		self.ejectLocation = pos
	def GetEjectLocation(self):
		if not self.ejectLocation:
			return self.rect.bottomright
		return self.ejectLocation

	def LaunchCar(self):
		if not self.idleCars:
			#no cars are currently idle
			#print "no cars are currently idle", self
			#print "idlecars", self.idleCars
			return
		popGroup = self.lineup.PopVisitors(self.carCapacity)
		if not popGroup:
			#print "nobody in line", self
			return

		nextCar = self.idleCars.pop()

		self.carPaddingCounter = self.minimumCarPadding

		for v in popGroup:
			v.BoardCar( nextCar )
		nextCar.visitors = popGroup
		nextCar.state = Car.RUNNING
		self.runningCars.append( nextCar )

	def LandCar(self,car):
		self.runningCars.remove( car )
		visitors = car.visitors
		car.Empty()
		car.state = Car.IDLE
		self.idleCars.append( car )
		#print "ejecting", visitors, " at", self.GetEjectLocation()
		for v in visitors:
			v.EjectFromRide( self.GetEjectLocation() )


	def SetLineup(self, lineup):
		self.lineup = lineup
		self.lineup.ride = self

	def MakeLineup(self):
		lineup = Lineup()
		lineup.ride = self
		corners = ["topleft", 
		           "topright",
		           "bottomleft", 
		           "bottomright",
		          ]
		choice = rng.choice( corners )
		rideCorner = getattr( self.rect, choice )
		corners.remove( choice )
		lineCorner = getattr( lineup.rect, rng.choice( corners ) )
		difference = ( rideCorner[0]-lineCorner[0],
		               rideCorner[1]-lineCorner[1] )

		lineup.rect.move_ip( difference )

		self.lineup = lineup
		return lineup

	def update( self ):
		self.carPaddingCounter -= 1
		if self.carPaddingCounter <= 0:
			self.LaunchCar()

	def GetInfo(self):
		return self.name


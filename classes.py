#/usr/bin/python

from pygame.sprite import Sprite, spritecollide
from pygame import Surface, Rect
import pygame
from move_matrix import MoveMatrix 
from lineup import Lineup
from ride import Ride, Car
import allobjects
from log import log

from math import sqrt

try:
	import simulation
except:
	print "COULD NOT FIND SIMULATION DEFINITION"
	print "USING BACKUP INSTEAD"
	import simulation_backup as simulation

rng = simulation.rng

def EfficientCollisionDetect( visitor, desiredPos ):
	if not visitor.InLineup():
		return False
	colliders = visitor.lineup.visitors
	for c in colliders:
		if c.rect.center == desiredPos:
			return True

class MyRect:
	def __init__(self, rect):
		self.pX = float( rect.x )
		self.pY = float( rect.y )
	
	def move_ip( self, diffX, diffY ):
		oldX = self.pX
		oldY = self.pY
		self.pX += diffX
		self.pY += diffY
		intDiffX = int(self.pX) - int(oldX)
		intDiffY = int(self.pY) - int(oldY)
		return intDiffX, intDiffY

	def Round( self ):
		self.pX = float(int(self.pX))
		self.pY = float(int(self.pY))

def ALengthGivenBLengthAndHypotenuse( bLength, hypotenuse ):
	return sqrt( hypotenuse**2 - bLength**2 )
def GetHypotenuse( aLength, bLength ):
	return sqrt( aLength**2 + bLength**2 )


#-----------------------------------------------------------------------------
class Visitor(Sprite):
	size = (3,3)
	def __init__(self, color):
		Sprite.__init__(self)
		self.color = color
		self.rect = pygame.Rect( 0,0,Visitor.size[0],Visitor.size[1] )
		self.realPos = MyRect( self.rect )
		self.image = Surface( self.rect.size )
		self.image.fill( self.color )
		self.speed = 0.5
		self.shouldLeaveThePark = False

		self.desiredRides = []
		self.timeEnteredRecentLine = None
		self.attractionBoredomTimeout = 300
		self.lineupPadding = simulation.humanWidth*2
		self.lineup = None
		self.car = None
		self.carSeat = None
		self.ejectLocation = None
		self.moveDirection = None

		self.currentDestination = None
		self.currentDestPoint = None
		self.wanderMode = True
		self.nextDecisionCounter = 0
		self.correctionCounter = 0

	def __str__( self ):
		return self.__class__.__name__ + str( self.rect.center )

	def GetInfo( self ):
		return "Visitor at "+ str( self.rect.center )

	def LeaveThePark( self ):
		self.shouldLeaveThePark = True

	def InLineup( self ):
		return self.lineup != None
	def InCar( self ):
		return self.car != None
	def JustEjected( self ):
		return self.ejectLocation != None

	def HeadToParkExit( self ):
		self.kill()
		allobjects.allVisitors.remove( self )

	def BoardCar( self, car ):
		self.carSeat = car.TakeSeat()
		self.lineup = None
		self.car = car

	def EjectFromRide( self, ejectLocation ):
		self.lineup = None
		self.wanderMode = True
		self.car = None
		self.carSeat = None
		self.ejectLocation = ejectLocation
	
	def HitDestination( self ):
		return self.HitLineup( self.currentDestination )

	def HitLineup( self, lineup ):
		self.lineup = lineup
		self.lineup.AddVisitor(self)
		self.realPos.Round()
		self.desiredRides.remove( lineup.ride )
		self.ChooseNextRides()

	def AddRide( self, ride ):
		self.desiredRides.append( ride )
	def RemoveRide( self, ride ):
		self.desiredRides.remove( ride )
		self.ChooseNextRides()
		

	def ChooseNextRides( self ):
		dRides = self.desiredRides
		if dRides:
			lineups = [r.lineup for r in dRides]

			self.currentDestination = [lin for lin in lineups if \
			lin.GetGuess() == min([l.GetGuess() for l in lineups])
			][0]

			#minLine = None
			#for r in dRides:
			#	if minLine == None:
			#		minLine = r.lineup
			#	elif r.lineup.GetGuess() < minLine.GetGuess():
			#		minLine = r.lineup
			#self.currentDestination = minLine
		else:
			for i in range( rng.randint(1,4) ):
				nextRide = rng.choice( allobjects.allRides )
				self.AddRide( nextRide )
			self.currentDestination = dRides[0].lineup

	def CalcMoveDirection( self, destPoint ):
		diffX = destPoint[0] - self.rect.centerx
		diffY = destPoint[1] - self.rect.centery
		try:
			scale = float( self.speed ) / GetHypotenuse(diffX,diffY)
		except ZeroDivisionError:
			scale = 1
		self.moveDirection = [diffX*scale, diffY*scale]
		return diffX, diffY

	def CorrectCourse( self ):
		self.correctionCounter -= 1
		if self.correctionCounter > 0 and self.currentDestPoint:
			return

		hotspot = self.currentDestination.hotspot
		park = allobjects.park
		if not self.currentDestPoint:
			self.currentDestPoint = park.GetDestPoint(self.rect.center, hotspot )
			if not self.currentDestPoint:
				#print "dest point failed", self.rect.center
				#print "dest point failed", hotspot
				self.wanderMode = True
				self.moveDirection = [0.5,0.5]
				return
			self.currentDestPoint = tuple( self.currentDestPoint )

		diffX,diffY = self.CalcMoveDirection( self.currentDestPoint )

		if abs(diffX) < 2 and abs(diffY) < 2:
			self.correctionCounter = 0
		else:
			self.correctionCounter = 100


	def update( self ):
		s_rect = self.rect
		s_dest = self.currentDestination

		if self.InCar():
			if self.rect.center != self.carSeat:
				self.MoveTo( self.carSeat )
		elif self.JustEjected():
			self.MoveTo( self.ejectLocation )
			self.ejectLocation = None
		elif self.InLineup():
			#print "in a lineup", self
			oldCenter = self.rect.center
			moveMatrix = self.lineup.GetMoveMatrix()
			#try to move 3 spots ahead
			spot2 = None
			try:
				spot1 = moveMatrix[s_rect.center]
				spot2 = moveMatrix[spot1]
				spot3 = moveMatrix[spot2]
				nextSpot = spot3
			except KeyError:
				nextSpot = self.lineup.GetEntryPoint()
				#print "key error!", nextSpot
			self.MoveTo( nextSpot, spot2 )

		elif s_dest and not self.wanderMode:
			override = False

			#first check if we're already in our destination
			if self.currentDestPoint == s_rect.center:
				if s_rect.center == self.currentDestination.hotspot:
					self.HitDestination()
					return
				self.currentDestPoint = None

			self.CorrectCourse()

			self.Move( *self.moveDirection )

		elif self.shouldLeaveThePark and self.nextDecisionCounter:
			self.HeadToParkExit()

		elif self.nextDecisionCounter:
			self.nextDecisionCounter -= 1
			#wander mode
			if not self.nextDecisionCounter%6 or \
			   not self.moveDirection:
				park = allobjects.park
				d = park.GetRandomDestPoint(self.rect.center)
				if not d:
					#log.debug( "Couldn't get Random Dest" )
					d = park.GetEntryPoint()
				self.CalcMoveDirection( d )
			self.Move( *self.moveDirection )
			if self.nextDecisionCounter == 0:
				self.wanderMode = False
				self.ChooseNextRides()
		else:
			self.nextDecisionCounter = simulation.getNextDecisionDuration()

	def Move( self, xDiff, yDiff ):
		intDiff = self.realPos.move_ip(xDiff, yDiff)
		self.rect.move_ip( intDiff[0], intDiff[1] )
	def MoveTo( self, pos, failPos=None ):
		if EfficientCollisionDetect( self, pos ):
			if failPos:
				pos = failPos
				if EfficientCollisionDetect( self, pos ):
					return
		self.Move( pos[0]-self.rect.centerx, pos[1]-self.rect.centery )
			

#-----------------------------------------------------------------------------
class UnGuidedVisitor(Visitor):
	def __init__(self):
		Visitor.__init__( self, (255,0,0) )
	def __repr__( self ):
		return Visitor.__str__(self)


#-----------------------------------------------------------------------------
class GuidedVisitor(Visitor):
	def __init__(self, device):
		Visitor.__init__( self, (0,255,0) )
		self.guessedTimeEnteredRecentLine = None
		self.device = device
		self.device.SetVisitor( self )

	def __repr__( self ):
		return Visitor.__str__(self)

	def update( self ):
		Visitor.update(self)
		self.device.update()

	def EjectFromRide( self, ejectLocation ):
		Visitor.EjectFromRide(self, ejectLocation)
		self.device.Notify()
	
	def HitDestination( self ):
		Visitor.HitDestination(self)
		self.device.Notify()
	def HeadToParkExit( self ):
		Visitor.HeadToParkExit( self )
		self.device.Return()

#-----------------------------------------------------------------------------
class Show:
	def __init__(self):
		self.playTimes = []
		self.duration = 150
		self.capacity = 50

#-----------------------------------------------------------------------------
class Device(Sprite):
	def __init__(self):
		Sprite.__init__(self)
		self.pollRate = 30
		self.pollCounter = 0
		self.notifyCounter = 0
		self.visitor = None
		self.reportedPositions = []
		self.enteredLineTime = None
		self.exitedLineTime = None
		self.lineup = None
		self.justExitedLineup = False
		self.justReturned = False

		self.rect = Rect( 0,0, *Visitor.size )
		self.image = Surface( Visitor.size )
		self.image.fill( (150,255,150) )

	def SetVisitor( self, visitor ):
		self.visitor = visitor

	def Return( self ):
		self.visitor = None
		allobjects.server.ReturnDevice( self )
		self.justReturned = True

	def update( self ):
		if self.justReturned:
			self.justReturned = False
			return

		self.pollCounter += 1
		if self.pollCounter == self.pollRate:
			self.rect.center = self.ReportPosition()
			self.pollCounter = 0

		if self.notifyCounter:
			self.notifyCounter -= 1
			if not self.notifyCounter%4:
				self.CheckLineupStatus()


	def SendRidesList( self ):
		allobjects.server.SendDesiredRides( self, 
		                                    self.visitor.desiredRides )

	def ReportPosition( self ):
		pos = self.visitor.rect.center
		accRange = simulation.gpsAccuracyRange
		xDiff = rng.uniform( 0.0, accRange )
		yDiff = ALengthGivenBLengthAndHypotenuse( xDiff, accRange )
		xDiff *= rng.choice( [-1,1] )
		yDiff *= rng.choice( [-1,1] )

		pos = ( pos[0]+xDiff, pos[1]+yDiff )

		allobjects.server.DevicePoll( self, pos )
		self.reportedPositions.append( pos )

		return pos
	
	def Notify( self ):
		self.notifyCounter = 80

	def CheckLineupStatus( self ):
		"""CPU-saving measure:  only try to detect when device enters/
		exits a line when the Visitor notifies us"""
		myPos = self.rect.center
		gpsErr = int(simulation.gpsAccuracyRange)+1
		if self.lineup and not self.justExitedLineup:
			#print 'self.lineup', self.lineup
			outerRect = self.lineup.rect.inflate(gpsErr,gpsErr)
			if not outerRect.collidepoint( myPos ):
				self.exitedLineTime = allobjects.timeOfDay
				# this will be turned off by the server
				self.justExitedLineup = True
				#print 'exited line', myPos
		else:
			#print 'just entered a line??'
			for l in allobjects.allLineups:
				innerRect = l.rect.inflate(-gpsErr,-gpsErr)
				if innerRect.collidepoint( myPos ):
					self.enteredLineTime = allobjects.timeOfDay
					self.justExitedLineup = False
					self.exitedLineTime = None
					self.lineup = l
					#print 'entered line', myPos
	def ServerInspect( self ):
		#print 'server wipes device', self
		self.justExitedLineup = False
		self.lineup = None

#-----------------------------------------------------------------------------
class TravelBuddyServer:
	def __init__(self):
		self.lastTick = 0
		self.reportedPositionsByTime = {}
		self.reportedPositionsByTime[self.lastTick] = []
		self.reportedPositionsByDevice = {}
		self.devices = []

	def NewDevice( self ):
		device = Device()
		self.devices.append(device)
		self.reportedPositionsByDevice[id(device)] = []
		return device

	def ReturnDevice( self, device ):
		self.devices.remove( device )
		device.kill()

	def GetLastReportedPositions( self ):
		print 'who calls this???'
		ps = []
		for k,v in self.reportedPositionsByDevice:
			try:
				ps.append( v[-1] )
			except IndexError:
				pass
		return ps

	def SendDesiredRides( self, device, rideList ):
		pass

	def DevicePoll( self, device, pos ):
		return
		self.reportedPositionsByTime[self.lastTick].append( [pos,device] )
		self.reportedPositionsByDevice[id(device)].append( 
		       [pos, allobjects.timeOfDay, self.lastTick] )

	def Tick( self ):
		devicesThatJustExitedRides = [d for d in self.devices if d.justExitedLineup ]
		#print 'devices that just exited:', devicesThatJustExitedRides
		for d in devicesThatJustExitedRides:
			duration = d.exitedLineTime - d.enteredLineTime
			if duration < simulation.prematureLineExitThreshold:
				#throw this away.  probably a bogus value
				continue
			lineup = d.lineup
			lineup.durationGuess = (lineup.durationGuess+duration)/2
			#print 'altered duration guess', lineup.durationGuess
			d.ServerInspect()


		if self.lastTick % 1000:
			self.CleanUp()

	def CleanUp( self ):
		return
		#prevent the memory leak
		newPs = ( (k,v) for k,v in self.reportedPositionsByTime.items() if k > self.lastTick-200 )
		newDict = {}
		for k,v in newPs:
			newDict[k] = v
		self.reportedPositionsByTime = newDict
		#TODO: prevent the rest of the mem leak

# { 
# (x,y) : (nextX, nextY)
# ...
# }

tinyLine = {
	(0,0): (1,0),
	(1,0): (2,0),
	(2,0): (3,0),
	(3,0): (4,0),
	(4,0): (4,1),
	(4,1): (3,1),
	(3,1): (2,1),
	(2,1): (1,1),
	(1,1): (0,1),
}

class LineDefinition:
	def __init__(self):
		self.lineDict = {}
		self.keysInOrder = []
		self.startKey = (0,0)

	def __getitem__(self, key):
		return self.lineDict[key]

	def Generate(self, xLen, yLen, step=1):
		self.startKey = (0,0)
		numRows = yLen/step
		numCols = xLen/step
		for y in range(numRows):
			for x in range(numCols):
				if y%2:
					xVal = x*step-step
					yVal = y*step
					if x==0:
						xVal = x*step
						yVal = y*step+step
				else:
					xVal = x*step+step
					yVal = y*step
					if x == numCols-1:
						xVal = x*step
						yVal = y*step+step
				key = (x*step,y*step)
				self.lineDict[key] = ( xVal, yVal )

		#set the last key to be itself so that the line stops
		if yLen%2:
			lastPos = (xLen-1, yLen)
		else:
			lastPos = (0,yLen)
		self.lineDict[ lastPos ] = lastPos

		self.keysInOrder = []
		k = self.startKey
		for i in range( len(self.lineDict) ):
			self.keysInOrder.append( k )
			k = self.lineDict[k]

	def Transform(self, transformPos):
		newLineDict= {}
		newKIO = []

		x,y = transformPos
		nextKIO = self.startKey
		for k,v in self.lineDict.items():
			newKey = (k[0]+x, k[1]+y) 
			newVal = (v[0]+x, v[1]+y)
			newLineDict[ newKey ] = newVal

			newKIO.append( (nextKIO[0]+x, nextKIO[1]+y) )
			nextKIO = self.lineDict[nextKIO]

		self.lineDict = newLineDict
		self.keysInOrder = newKIO
		self.startKey = (self.startKey[0]+x, self.startKey[1]+y)


	def GetLast(self, numPositions):
		a = self.keysInOrder[ -numPositions : ]
		if a[0] == a[1]:
			print "ERROR"
			self.Print()
			print self.keysInOrder
			raise 'foo'
		return self.keysInOrder[ -numPositions : ]

	def Print(self, xLen, yLen, step):
		print 'start key', self.startKey
		colRange = [ self.startKey[0], self.startKey[0]+xLen*step ]
		rowRange = [ self.startKey[1], self.startKey[1]+yLen*step ]
		for j in range( *rowRange ):
			for i in range( *colRange ):
				try:
					t = self.lineDict[((i*step),(j*step))] 
					print t[0],t[1],"|",
				except Exception, e:
					print "exception: ", e
					raise e
			print ""
		#print self.keysInOrder


class SparseLine(LineDefinition):
	def Generate(self):
		return LineDefinition.Generate( self, 40, 40, 4 )
	def Print(self):
		return LineDefinition.Print(self, 40, 40, 4)

class DenseLine(LineDefinition):
	def Generate(self):
		return LineDefinition.Generate( self, 40, 20, 1 )
	def Print(self):
		return LineDefinition.Print( self, 40, 20, 1 )

class MoveMatrix:
	def __init__(self,lineType=SparseLine):
		self.matrix = lineType()
		self.matrix.Generate()
		self.alreadyTransformed = False

	def __getitem__(self, key):
		return self.matrix[key]

	def transform(self, tRect):
		if self.alreadyTransformed:
			return
		self.alreadyTransformed = True

		self.matrix.Transform( tRect.topleft )

		#self.matrix.Print()

	def GetStartPos(self):
		return self.matrix.startKey

	def GetLast(self, numPositions):
		return self.matrix.GetLast( numPositions )

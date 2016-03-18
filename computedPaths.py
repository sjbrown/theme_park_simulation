#! /usr/bin/python

# usage : 
#self.computedPaths = computedPaths.paths[ self.name]
#self.hEmpties = computedPaths.hEmpties[ self.name]

from glob import glob

class UserDict(dict): pass

# DynamicCachingLoader is an **ABSTRACT** class.  It must be inherited
# from and the subclas MUST implement LoadResource( attname )
class DynamicCachingLoader(UserDict):
	def __init__(self):
		self._d = {}
	def __getattr__(self, attname):
		try:
			return self.__dict__[attname]
		except KeyError:
			log.debug( 'loader got key err' )
			try:
				return self._d[attname]
			except KeyError:
				self.LoadResource( attname )
				return self._d[attname]

	def __getitem__(self, key):
		try:
			return self._d[key]
		except KeyError:
			self.LoadResource( key )
			return self._d[key]



class AllPaths(DynamicCachingLoader):
	def LoadResource(self, name):
		mod = __import__( name+'_paths', None, None, 'paths')
		self._d[name] = mod.paths

from pathfinder import HallRect, LoadHallRect
class AllHEmpties(DynamicCachingLoader):
	def LoadResource(self, name):
		mod = __import__( name+'_paths', None, None, 'hEmpties')
		hEmpties = []
		hPickles = mod.hEmpties
		for hp in hPickles:
			hEmpties.append( LoadHallRect( hp ) )

		self._d[name] = hEmpties

paths = AllPaths()
hEmpties = AllHEmpties()


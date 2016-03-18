import logging
import sys

DEBUG = 1

log = logging.Logger('parksim')
formatter = logging.Formatter( '%(asctime)s %(levelname)s %(message)s' )

sHandler = logging.StreamHandler( sys.stdout )
sHandler.setFormatter( formatter )


if DEBUG:
	log.addHandler( sHandler )
	log.setLevel( logging.DEBUG )
else:
	try:
		fHandler = logging.FileHandler( '/tmp/parksim.log' )
		fHandler.setFormatter( formatter )
		log.addHandler( fHandler )
		log.setLevel( logging.INFO )
	except:
		pass

from math import *
from sympy import *
from sympy.abc import *
from __future__ import division

ans = 0
last_ANS = 0

print( "#Type 'ans' to refer to the last result." )
print( "#Keep in mind that numeric values differs a lot from symbolic one." )

def evalf( something=None ) : 
	if something is None : return evalf( ans )
	try : 
		return something.evalf()
	except AttributeError :
		try :
			return float( something )
		except ValueError : 
			print( "Error : Unvalid Expression!" ) 

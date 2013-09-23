# -*- coding: utf-8 -*-
############################################################
# I'm a lazy developer.                                    #
# And as a lazy developer sometimes I put shit in my code. #
# Expecially when I'm sure that anyone will read my code.  #
# So, if you're reading this, please...                    #
# ...Don't judge me.                                       #
############################################################

from kivy.app import App
import kivy.graphics as kg
from kivy.lang import Builder
from kivy.properties import *
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from time import time
from math import sqrt, floor
from random import random
from string import join
from sympy import *
from sympy.abc import *
from sympy.utilities.lambdify import lambdify
import sys

from kivyextras import *
from shell import DEBUG

Builder.load_file( "kipycalc.kv" )

ALPHABET = "ABCDEFGHJKILMNOPQRSTUVWXYZ"
FONT_NAME = "res/ubuntu-font-family-0.80/UbuntuMono-R.ttf"
FONT_SIZE = 16
		
class SpecialPoint( Widget ) :
	
	point = ListProperty( [ 0, 0 ] )
	lbl = ObjectProperty( None )
	#line width
	lnw = NumericProperty( 1 ) 
	#line color
	lcolor = ListProperty( [ 0.6, 0.6, 0.6, 1 ] )
	#point color
	pcolor = ListProperty( [ 1, 0, 0, 1 ] ) 

	def __init__( self, **kargs ) :
		super( SpecialPoint, self ).__init__( **kargs )
		if not "label" in kargs : kargs["label"] = str( self.point )
		if not "font_size" in kargs : kargs["font_size"] = FONT_SIZE-2
		self.lbl.text = kargs["label"]
		self.lbl.font_name = FONT_NAME
		self.lbl.font_size = kargs["font_size"]
		self.scale( 0, 0, 1, 1 )
		
	def scale( self, minx, miny, ppx, ppy ) :
		self.pos = [ int((self.point[0]-minx)*ppx), int((self.point[1]-miny)*ppy) ]


class DrawableFunction( Widget ) :

	foo = ObjectProperty( None )
	color = ListProperty( [1,1,1,1] )
	points = ListProperty( [] )
	sPoints = ListProperty( [] )
	
	def __init__( self, **kargs ) :
		super( DrawableFunction, self ).__init__( **kargs )

	def study( self ) :
		spoints = []
		#Function intersections with the x axis.
		try :
			for x_val in solve( self.expr, x ) :
				spoints.append( [ float( x_val ), 0 ] )
		except : pass	
		#Function intersections with the y axis.
		try :
			y_val = self.expr.subs( x, 0 ).evalf()  
			spoints.append( [ 0, float( y_val ) ] )
		except : pass
		#Function stationary points.
		try :
			for x_val in solve( self.expr.diff( x ), x ) :
				spoints.append( [ float( x_val ), self.foo( x_val ) ] )
		except : pass
		#Delete duplicates
		for p in spoints :
			if spoints.count( p ) != 1 : spoints.remove( p )

	def eval( self, xMin, xMax, yMin, yMax, ppx, ppy, step ) :
		points = []
		x = xMin
		while x < xMax : 
			try :
				y = self.foo( x )
				if y.__class__ in ( int, float ) :
					points.append( ( x - xMin ) * ppx )
					points.append( ( y - yMin ) * ppy )
			except : pass
			x += step
		self.points = points

		for point in self.sPoints : 			
			point.scale( xMin, yMin, ppx, ppy )
	
############################################################
# Multi plotter code. 	                                   #
############################################################
	
class Plotter( Widget ) :

	functions = ListProperty( [] )
	#Draw range
	xRange = ListProperty( [-1,1] )
	yRange = ListProperty( [-1,1] )
	#Plotter resolution
	ppx = NumericProperty( 0 )
	ppy = NumericProperty( 0 )
	#indicators
	x_scale_indicators_step = NumericProperty( 1.0 )
	y_scale_indicators_step = NumericProperty( 1.0 )
	indicators = ListProperty( [] )
	#Other things
	pinchS = NumericProperty( 0.1 )
	plotColor = ListProperty( [0,1,0] )
	axisColor = ListProperty( [1,1,1] )
	#List to handle touches
	touches = ListProperty( [] )
	touching = BooleanProperty( False )

	def __init__( self, functions, **kargs ) : 
		super( Plotter, self ).__init__( **kargs )
		self.width, self.height = screen_size()
		self.lblPoints = Label( font_name = FONT_NAME, 
                                font_size = FONT_SIZE )
		self.add_widget( self.lblPoints )
		self.loadFunctions( functions )
		self.setup()
		self.fooStudy()
		self.evalPoints()  
		self.prepareCanvas()

	def loadFunctions( self, functions ) :
		for foo in eval( functions ) :			
			dfoo = DrawableFunction( 
				foo = lambdify( x, evalf( foo ) ), \
				color = [ random(), random(), random(), 1 ]
			) 						
			self.functions.append( dfoo )
	 
	def prepareCanvas( self ) :
		for f in self.functions :
			with self.canvas :
				kg.Color( f.color[0],f.color[1],f.color[2],f.color[3],
                          group="functions" )
				kg.Line( points=f.points, width=2, group="functions" )
				kg.Color( 1, 1, 1, 1, group="axis" )
				kg.Line( points=self.getXAxis(), width=1, group="axis" )
				kg.Line( points=self.getYAxis(), width=1, group="axis" )
					
	def getXAxis( self ) :
		px = ( -self.xRange[0] ) * self.ppx
		p1y = ( self.yRange[1] - self.yRange[0] ) * self.ppy
		p2y = ( self.yRange[0] ) * self.ppy
		return [ px, p1y, px, p2y ]
					
	def getYAxis( self ) :
		py = ( -self.yRange[0] ) * self.ppy
		p1x = ( self.xRange[1] - self.xRange[0] ) * self.ppx
		p2x = ( self.xRange[0] ) * self.ppx
		return [ p1x, py, p2x, py ]

	def restoreCanvas( self ) :
		self.canvas.remove_group( "functions" )
		self.canvas.remove_group( "axis" )
		#self.canvas.remove_group( "sPoints" )

	def evalPoints( self ) :
		for foo in self.functions :
			foo.eval( self.xRange[0], self.xRange[1]*2, 
                      self.yRange[0], self.yRange[1],
                      self.ppx, self.ppy, self.step )
		self.restoreCanvas()
		self.prepareCanvas()

	def setup( self ) : 
		xToDisplay = abs( float( self.xRange[1]-self.xRange[0] ) )
		yToDisplay = abs( float( self.yRange[1]-self.yRange[0] ) )
		self.ppx = self.width / xToDisplay
		self.ppy = self.height / yToDisplay
		self.step = xToDisplay / (self.width*3)
		self.x_scale_indicators_step = 1 + int( xToDisplay / 10 )
		self.y_scale_indicators_step = 1 + int( yToDisplay / 10 )

	def movePlot( self ) :
		dx = ( self.touches[0].px - self.touches[0].x )/( self.ppx )
		dy = ( self.touches[0].py - self.touches[0].y )/( self.ppy )
		self.xRange = self.xRange[0]+dx, self.xRange[1]+dx
		self.yRange = self.yRange[0]+dy, self.yRange[1]+dy
		self.evalPoints()
	 
	def pinchZoom( self ) :
		dpx = abs( self.touches[0].psx - self.touches[1].psx )
		dx  = abs( self.touches[0].sx  - self.touches[1].sx  )
		dpy = abs( self.touches[0].psy - self.touches[1].psy )
		dy  = abs( self.touches[0].sy  - self.touches[1].sy  )
		if dx > self.pinchS : 
			self.xRange = [ xl*dpx/dx for xl in self.xRange ]
		if dy > self.pinchS : 
			self.yRange = [ yl*dpy/dy for yl in self.yRange ]
		self.setup()
		self.evalPoints()
	
	def on_touch_down( self, touch ) :
		self.touches.append( touch )
		return True

	def on_touch_up( self, touch ) :
		for t in self.touches :
			if t.uid == touch.uid:
				self.touches.remove( t )
		self.touching = False

	def on_touch_move( self, touch ) :
		#check if the touch is sigle or multiple
		if len( self.touches ) == 1 :
			self.movePlot()
		elif len( self.touches ) == 2 :
			self.pinchZoom() 

	def getConfig( self ) :
		return { "plotColor" : self.plotColor, \
                 "axisColor" : self.axisColor, \
                 "xRange" : self.xRange, \
                 "yRange" : self.yRange }

	def fooStudy( self ) :
		for foo in self.functions :
			foo.study()			
			for i, p in enumerate( foo.sPoints ) :
				try :
					sp = SpecialPoint( font_size=FONT_SIZE-1, \
                                       point=p, \
									   size=self.size, \
                                       label=ALPHABET[i] )
					self.add_widget( sp )		
					self.lblPoints.text += "\n%s : ( %.3f, %.3f )" % ( ALPHABET[i], p[0], p[1] )
				except : pass

############################################################
# Original plotter code. 	                               #
############################################################

class SinglePlotter( Widget ) :

	#Points to be drawn
	points = ListProperty( [] )
	#Special points
	spoints = ListProperty( [] )
	lblPoints = ObjectProperty( None )
	#Draw range
	xRange = ListProperty( [-1,1] )
	yRange = ListProperty( [-1,1] )
	#Plotter resolution
	ppx = NumericProperty( 0 )
	ppy = NumericProperty( 0 )
	#indicators
	x_scale_indicators_step = NumericProperty( 1.0 )
	y_scale_indicators_step = NumericProperty( 1.0 )
	indicators = ListProperty( [] )
	#Other things
	pinchS = NumericProperty( 0.1 )
	plotColor = ListProperty( [0,1,0] )
	axisColor = ListProperty( [1,1,1] )
	#List to handle touches
	touches = ListProperty( [] )
	touching = BooleanProperty( False )

	def __init__( self, foo, **kargs ) : 
		super( SinglePlotter, self ).__init__( **kargs )
		self.width, self.height = screen_size()
		self.expr = foo
		self.foo = lambdify( x, foo )		
		self.lblPoints.font_name = FONT_NAME
		self.lblPoints.font_size = FONT_SIZE
		self.setup()
		self.fooStudy()
		self.evalPoints()  
		self.setIndicators()

	def evalPoints( self ) :
		points = []
		x = self.xRange[0]
		while x < self.xRange[1] : 
			try :
				y = self.foo( x )
				if y.__class__ in ( int, float ) :
					points.append( ( x - self.xRange[0] ) * self.ppx )
					points.append( ( y - self.yRange[0] ) * self.ppy )
			except : pass
			x += self.step
		self.points = points
		for point in self.spoints : 			
			point.scale( self.xRange[0], self.yRange[0], self.ppx, self.ppy )

	def setup( self ) : 
		xToDisplay = abs( float( self.xRange[1]-self.xRange[0] ) )
		yToDisplay = abs( float( self.yRange[1]-self.yRange[0] ) )
		self.ppx = self.width / xToDisplay
		self.ppy = self.height / yToDisplay
		self.step = xToDisplay / (self.width*3)
		self.x_scale_indicators_step = 1 + int( xToDisplay / 10 )
		self.y_scale_indicators_step = 1 + int( yToDisplay / 10 )
	
	def setIndicators( self ) :
		#Deleting old indicators
		for i in self.indicators : self.remove_widget( i )
		self.indicators = []

		#Setting up x and y values
		y = int( floor( self.yRange[0] ) )
		x = int( floor( self.xRange[0] ) )
		
		#Adding new indicators
		while x <= self.xRange[1] :
			if not self.xNearSpecialPoint( x ) :
				p = SpecialPoint( pcolor = ( 1, 1, 1, 1 ), \
                                  lcolor = ( 0, 0, 0, 0 ), \
                                  point = ( x, 0 ), \
                                  label = str( x ) )
				p.scale( self.xRange[0], self.yRange[0], \
                         self.ppx, self.ppy )
				self.add_widget( p )
				self.indicators.append( p )
			x += self.x_scale_indicators_step

		h = self.height - self.lblPoints.pos[1]
		while y <= self.yRange[1]-h/self.ppy :
			if not self.yNearSpecialPoint( y ) :
				p = SpecialPoint( pcolor = ( 1, 1, 1, 1 ), \
                                  lcolor = ( 0, 0, 0, 0 ), \
                                  point = ( 0, y ), \
                                  label = str( y ) )
				p.scale( self.xRange[0], self.yRange[0], \
                         self.ppx, self.ppy )
				self.add_widget( p )
				self.indicators.append( p )
			y += self.y_scale_indicators_step
	
	def xNearSpecialPoint( self, x ) :
		D = abs( self.xRange[0] - self.xRange[1] ) / 20
		for sp in self.spoints : 
			if abs( sp.point[0] - x ) < D : return True
		return False

	def yNearSpecialPoint( self, y ) :
		D = abs( self.yRange[0] - self.yRange[1] ) / 20
		for sp in self.spoints : 
			if abs( sp.point[1] - y ) < D : return True
		return False

	def movePlot( self ) :
		dx = ( self.touches[0].px - self.touches[0].x )/( self.ppx )
		dy = ( self.touches[0].py - self.touches[0].y )/( self.ppy )
		self.xRange = self.xRange[0]+dx, self.xRange[1]+dx
		self.yRange = self.yRange[0]+dy, self.yRange[1]+dy
		self.evalPoints()
	 
	def pinchZoom( self ) :
		dpx = abs( self.touches[0].psx - self.touches[1].psx )
		dx  = abs( self.touches[0].sx  - self.touches[1].sx  )
		dpy = abs( self.touches[0].psy - self.touches[1].psy )
		dy  = abs( self.touches[0].sy  - self.touches[1].sy  )
		if dx > self.pinchS : self.xRange = [ xl*dpx/dx for xl in self.xRange ]
		if dy > self.pinchS : self.yRange = [ yl*dpy/dy for yl in self.yRange ]
		self.setup()
		self.evalPoints()
	
	def on_touch_down( self, touch ) :
		self.touches.append( touch )
		return True

	def on_touch_up( self, touch ) :
		for t in self.touches :
			if t.uid == touch.uid:
				self.touches.remove( t )
		self.touching = False
		self.setIndicators()		

	def on_touch_move( self, touch ) :
		#check if the touch is sigle or multiple
		if len( self.touches ) == 1 :
			self.movePlot()
		elif len( self.touches ) == 2 :
			self.pinchZoom() 

	def getConfig( self ) :
		return { "plotColor" : self.plotColor, \
                 "axisColor" : self.axisColor, \
                 "xRange" : self.xRange, \
                 "yRange" : self.yRange }

	def fooStudy( self ) :
		spoints = []
		#Function intersections with the x axis.
		try :
			for x_val in solve( self.expr, x ) :
				spoints.append( [ float( x_val ), 0 ] )
		except : pass	
		#Function intersections with the y axis.
		try :
			y_val = self.expr.subs( x, 0 ).evalf()  
			spoints.append( [ 0, float( y_val ) ] )
		except : pass
		#Function stationary points.
		try :
			for x_val in solve( self.expr.diff( x ), x ) :
				spoints.append( [ float( x_val ), self.foo( x_val ) ] )
		except : pass
		#Delete duplicates
		for p in spoints :
			if spoints.count( p ) != 1 : spoints.remove( p )
		#Adding new widgets
		for i, p in enumerate( spoints ) :
			try :
				sp = SpecialPoint( font_size=FONT_SIZE-1, point=p, size=self.size, label=ALPHABET[i])
				self.add_widget( sp )		
				self.spoints.append( sp )
				self.lblPoints.text += "\n%s : ( %.3f, %.3f )" % ( ALPHABET[i], p[0], p[1] )
			except : pass


class PlottingPanel( Popup ) :
	
	expLabel = ObjectProperty( None )

	def __init__( self, onConfirm ) :
		Popup.__init__( self, \
						title = 'Plotting Options', \
						content = self._genContent( onConfirm ), \
						size_hint = ( 0.95,0.95 ) )
		setFont( self.content, FONT_NAME, FONT_SIZE )

	def _genContent( self, onConfirm ) : 
		c = BoxLayout( orientation = "vertical" )
		btnPlot = Button( text="Ok, plot" )
		btnPlot.bind( on_press = onConfirm )
		self.expLabel = Label( text="" )
		c.add_widget( self.expLabel )
		c.add_widget( btnPlot )
		return c
		
	def open( self, shellObj, currentConfig=None ) : 
		shellObj._lastOutput = []
		shellObj.console.push( "evalf(" + shellObj.getInput() + ")" )
		self.expLabel.text = shellObj._lastOutput[-1]
		fullMsg = join( shellObj._lastOutput, "\n" )
		if not "Error" in fullMsg :
			self.expLabel.text = shellObj._lastOutput[-2]
			Popup.open( self )
		
	def dismiss( self ) :
		Popup.dismiss( self )
		return self.expLabel.text






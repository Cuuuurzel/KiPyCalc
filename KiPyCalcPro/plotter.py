# -*- coding: utf-8 -*-

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
from kivyextras import *
from time import time
from math import sqrt, floor
from sympy import *
from sympy.abc import *
from sympy.utilities.lambdify import lambdify
import sys

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
		Widget.__init__( self, **kargs )
		if not "label" in kargs : kargs["label"] = str( self.point )
		if not "font_size" in kargs : kargs["font_size"] = FONT_SIZE-2
		self.lbl.text = kargs["label"]
		self.lbl.font_name = FONT_NAME
		self.lbl.font_size = kargs["font_size"]
		self.scale( 0, 0, 1, 1 )
		
	def scale( self, minx, miny, ppx, ppy ) :
		self.pos = [ int((self.point[0]-minx)*ppx), int((self.point[1]-miny)*ppy) ]

class Plotter( Widget ) :

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
		Widget.__init__( self, **kargs )
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
				p = SpecialPoint( pcolor=(1,1,1,1), lcolor=(0,0,0,0), point=( x, 0 ), label=str(x) )
				p.scale( self.xRange[0], self.yRange[0], self.ppx, self.ppy )
				self.add_widget( p )
				self.indicators.append( p )
			x += self.x_scale_indicators_step
		h = self.height - self.lblPoints.pos[1]
		while y <= self.yRange[1]-h/self.ppy :
			if not self.yNearSpecialPoint( y ) :
				p = SpecialPoint( pcolor=(1,1,1,1), lcolor=(0,0,0,0), point=( 0, y ), label=str(y) )
				p.scale( self.xRange[0], self.yRange[0], self.ppx, self.ppy )
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

class PlottingOptionPanel( Popup ) :

	def __init__( self, onConfirm ) :
		w, h = screen_size()
		frm = BoxLayout( orientation="vertical" )
		cont = BoxLayout( orientation="vertical" )
		cont.spacing = 30

		self.plotColor = ColorChooser( label="Plot Color :", rgb=[ 0, 1, 0 ] )
		self.axisColor = ColorChooser( label="Axis Color :", rgb=[ 1, 1, 1 ] )
		frm.add_widget( self.plotColor )
		frm.add_widget( self.axisColor )

		xRange = BoxLayout( orientation="vertical" )
		xRange.add_widget( Label( text="X range :" ) )
		self.xRangeMin = NumericUpDown( value=-1, vstep=0.1 )
		self.xRangeMax = NumericUpDown( value=1, vstep=0.1 )
		xRange.add_widget( self.xRangeMin )
		xRange.add_widget( self.xRangeMax )

		yRange = BoxLayout( orientation="vertical" )
		yRange.add_widget( Label( text="Y range :" ) )
		self.yRangeMin = NumericUpDown( value=-1, vstep=0.1 )
		self.yRangeMax = NumericUpDown( value=1, vstep=0.1 )
		yRange.add_widget( self.yRangeMin )
		yRange.add_widget( self.yRangeMax )

		btnConfirm = Button( text="Ok, Plot!" )
		btnConfirm.bind( on_press=onConfirm )
		btnConfirm.size_hint = 1, 0.1

		self.expLabel = Label()
		self.expLabel.size_hint = 1, 0.1

		r = BoxLayout( orientation="horizontal" )
		r.spacing = 15
		frm.add_widget( r )
		r.add_widget( xRange )
		r.add_widget( yRange ) 
 
		cont.add_widget( self.expLabel )
		cont.add_widget( frm )
		cont.add_widget( btnConfirm )

		Popup.__init__( self, \
						title = 'Plotting Options', \
						content = cont, \
						size_hint = ( 0.95,0.95 ) )

		setFont( self.content, FONT_NAME, FONT_SIZE )
		self.expLabel.font_size = FONT_SIZE+5

	def open( self, someExpression, shellObj, currentConfig=None ) : 
		if not currentConfig is None :
			self.plotColor.setRGB( currentConfig[ "plotColor" ] )
			self.axisColor.setRGB( currentConfig[ "axisColor" ] )
			self.xRangeMin.value = float( "%.3f" % currentConfig[ "xRange" ][0] )
			self.xRangeMax.value = float( "%.3f" % currentConfig[ "xRange" ][1] )
			self.yRangeMin.value = float( "%.3f" % currentConfig[ "yRange" ][0] )
			self.yRangeMax.value = float( "%.3f" % currentConfig[ "yRange" ][1] )

		shellObj._lastOutput = []
		shellObj.console.push( "evalf(" + someExpression + ")" )
		self.expLabel.text = shellObj._lastOutput[-1]

		fullMsg = ""
		for msgPart in shellObj._lastOutput : fullMsg += "\n" + msgPart

		if not "Error" in fullMsg :
			self.expLabel.text = shellObj._lastOutput[-2]
			Popup.open( self )

	def dismiss( self, forced=False ) :
		Popup.dismiss( self )
		if forced : return
		
		return {"axisColor" : self.axisColor.rgb(), \
				"plotColor" : self.plotColor.rgb(), \
				"xRange"	: (self.xRangeMin.value, self.xRangeMax.value), \
				"yRange"    : (self.yRangeMin.value, self.yRangeMax.value) }, eval( self.expLabel.text )

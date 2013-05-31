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
from kivyextras import ColorChooser, NumericUpDown, screen_size
from time import time
from math import sqrt
from sympy import *
from sympy.abc import *
from sympy.utilities.lambdify import lambdify
import sys
from random import random
from shell import WrappedString

Builder.load_file( "kipycalc.kv" )

def calculate_Points(x1, y1, x2, y2, steps=5):
	dx = x2 - x1
	dy = y2 - y1
	dist = sqrt(dx * dx + dy * dy)
	if dist < steps:
		return None
	o = []
	m = dist / steps
	for i in xrange(1, int(m)):
		mi = i / m
		lastx = x1 + dx * mi
		lasty = y1 + dy * mi
		o.extend([lastx, lasty])
	return o


class Plotter( Widget ) :

	plotColor = ListProperty( [0,1,0] )
	axisColor = ListProperty( [1,1,1] )
	points = ListProperty( [] )
	xRange = ListProperty( [-1,1] )
	yRange = ListProperty( [-1,1] )
	step = NumericProperty( 0 )
	xpp = NumericProperty( 0 )
	ypp = NumericProperty( 0 )
	pinchWeight = NumericProperty( 5 )
	c_fixed = BooleanProperty( False )
	_touches = ListProperty( [] )
	_labels = ListProperty( [] )
	_foo_zeros = ObjectProperty( None )
	_foo_x_to_zero = ObjectProperty( None )
	_derivative_zeros = ObjectProperty( None )
	touching = BooleanProperty( False )

	def __init__( self, foo, **kargs ) : 
		Widget.__init__( self, **kargs )
		self.width, self.height = screen_size()

		try : 
			self._foo_zeros = solve( foo, x )
		except : pass		
		try : 
			self._foo_x_to_zero = foo.subs( x, 0 ).evalf()  
			if not self._foo_x_to_zero.is_real : self._foo_x_to_zero = None
		except : pass
		try : 
			self._derivative_zeros = solve( foo.diff( x ), x )
		except : pass		

		self.foo = lambdify( x, foo )		
		self.setup()
		self.evalPoints()  

	def setup( self ) : 
		xToDisplay = float( self.xRange[1]-self.xRange[0] )
		yToDisplay = float( self.yRange[1]-self.yRange[0] )
		self.xpp = self.width / xToDisplay
		self.ypp = self.height / yToDisplay
		if self.step == 0 :
			self.step = xToDisplay / self.width*3

	def evalSpecialPoints( self ) :
		#cleaning
		self.canvas.remove_group( "intersections" )
		self.canvas.remove_group( "minandmax" )
		for lbl in self._labels : self.remove_widget( lbl ) 
		self.evalIntersections()
		self.evalMinAndMax()

	def evalIntersections( self ) :
		#settings
		dl = 1
		do = 5
		with self.canvas :					 
			kg.Color( self.axisColor, group="intersections" )
		#x axis
		if not self._foo_zeros is None :
			for xi in self._foo_zeros :
				if xi.is_real and self.xRange[0]<xi<self.xRange[1] :
					xi = xi.evalf()
					p = ( int( (xi-self.xRange[0]) * self.xpp ), 0,\
						  int( (xi-self.xRange[0]) * self.xpp ), self.height )				  
					t = "[color=ff0000]%.2f[/color]" % ( xi )
					with self.canvas :   
						kg.Line( dash_lenght=dl, dash_offset=do, points=p, group="intersections" )
						kg.Point( pointsize=2, group="intersections",
								  points=[ (xi-self.xRange[0])*self.xpp, -self.yRange[0]*self.ypp ] )
					lbl = Label( center=(p[0],9*self.height/10.0), text=t, markup=True )
					self._labels.append( lbl )
					self.add_widget( lbl )
		#y axis
		if not self._foo_x_to_zero is None and self._foo_x_to_zero.is_real :
			yi = self._foo_x_to_zero #self._sympyfoo.subs( x, 0 ).evalf()  
			p = ( 0, int( (yi-self.yRange[0]) * self.ypp ),\
				  self.width, int( (yi-self.yRange[0]) * self.ypp ) )			  
			t = "[color=ff0000]%.2f[/color]" % ( yi )
			with self.canvas :   
				kg.Line( dash_lenght=dl, dash_offset=do, points=p, group="intersections" )
				kg.Point( pointsize=2, group="intersections",
						  points=[ -self.xRange[0]*self.xpp, (yi-self.yRange[0])*self.ypp ] )
			lbl = Label( center=(4*self.width/5.0, p[1]), text=t, markup=True )
			self._labels.append( lbl )
			self.add_widget( lbl )
	 
	def evalMinAndMax( self ) : 
		#settings
		dl = 1
		do = 5
		with self.canvas :					 
			kg.Color( self.axisColor, group="minandmax" )
		#stationary points
		if not self._derivative_zeros is None :
			for xi in self._derivative_zeros : 
				if xi.is_real and self.xRange[0]<xi<self.xRange[1] :
					xi = xi.evalf()
					try : 
						yi = self.foo( xi )
						px = ( int( (xi-self.xRange[0]) * self.xpp ), 0,\
							   int( (xi-self.xRange[0]) * self.xpp ), self.height )				  
						tx = "[color=ff0000]%.2f[/color]" % ( xi )
						py = ( 0, int( (yi-self.yRange[0]) * self.ypp ),\
							   self.width, int( (yi-self.yRange[0]) * self.ypp ) )			  
						ty = "[color=ff0000]%.2f[/color]" % ( yi )
						with self.canvas :   
							kg.Line( dash_lenght=dl, dash_offset=do, points=px, group="minandmax" )
							kg.Line( dash_lenght=dl, dash_offset=do, points=py, group="minandmax" )
							kg.Point( pointsize=2, points=[ (xi-self.xRange[0])*self.xpp, (yi-self.yRange[0])*self.ypp ], group="minandmax" )
						lbl = Label( center=(px[0],9*self.height/10.0), text=tx, markup=True )
						self._labels.append( lbl )
						lbl = Label( center=(4*self.width/5.0, py[1]), text=ty, markup=True )
						self._labels.append( lbl )
						self.add_widget( lbl )
					except : pass

	def evalPoints( self ) :
		points = []
		x = self.xRange[0]
		while x < self.xRange[1] : 
			try :
				y = self.foo( x )
				px = ( x - self.xRange[0] ) * self.xpp
				py = ( y - self.yRange[0] ) * self.ypp
				points.append( px )
				points.append( py )
			except : pass
			x += self.step
		self.points = points
		if not self.touching : 
			self.evalSpecialPoints()

	def movePlot( self ) :
		dx = ( self._touches[0].px - self._touches[0].x )/( self.xpp )
		dy = ( self._touches[0].py - self._touches[0].y )/( self.ypp )
		self.xRange = self.xRange[0]+dx, self.xRange[1]+dx
		self.yRange = self.yRange[0]+dy, self.yRange[1]+dy
		self.evalPoints()
	 
	def pinchZoom( self ) :
		d0x = abs( self._touches[0].ox - self._touches[1].ox ) / self.xpp
		d0y = abs( self._touches[0].oy - self._touches[1].oy ) / self.ypp
		d1x = abs( self._touches[0].x - self._touches[1].x ) / self.xpp
		d1y = abs( self._touches[0].y - self._touches[1].y ) / self.ypp
		dx = ( d0x - d1x ) / self.pinchWeight
		dy = ( d0y - d1y ) / self.pinchWeight
		newXRange = self.xRange[0]-dx, self.xRange[1]+dx
		newYRange = self.yRange[0]-dy, self.yRange[1]+dy

		if ( abs(dx) > abs(dy) ) and newXRange[1]-newXRange[0] >= 2 :
			self.xRange = newXRange
		elif ( abs(dy) > abs(dx) ) and newYRange[1]-newYRange[0] >= 2 :
			self.yRange = newYRange
		self.setup()
		self.evalPoints()
	
	def on_touch_down( self, touch ) :
		self._touches.append( touch )
		return True

	def on_touch_up( self, touch ) :
		for t in self._touches :
			if t.uid == touch.uid:
				self._touches.remove( t )
		self.touching = False
		self.evalPoints()

	def on_touch_move( self, touch ) :
		#check if the touch is sigle or multiple
		if not self.c_fixed and len( self._touches ) == 1 :
			self.movePlot()
		elif len( self._touches ) == 2 :
			self.pinchZoom() 

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

		cent = BoxLayout( orientation="vertical" )
		cent.add_widget( Label( text="Center to :" ) )
		self.centx = NumericUpDown( value=0, vstep=0.1 )
		self.centy = NumericUpDown( value=0, vstep=0.1 )
		cent.add_widget( self.centx )
		cent.add_widget( self.centy )

		fixed_cent = BoxLayout( orientation="vertical" )
		fixed_cent.add_widget( Label( text="Fix center?" ) )
		self.fixed_cent = CheckBox( active=False )
		fixed_cent.add_widget( self.fixed_cent )

		step = BoxLayout( orientation="vertical" )
		step.add_widget( Label( text="X Step ( 0=Best ) :" ) )
		self.step = Slider( min=0, value=0, max=10)
		step.add_widget( self.step )

		btnConfirm = Button( text="Ok, Plot!" )
		btnConfirm.bind( on_press=onConfirm )
		btnConfirm.size_hint = 1, 0.1

		self.expLabel = Label()
		self.expLabel.size_hint = 1, 0.1

		r = BoxLayout( orientation="horizontal" )
		r.spacing = 15
		frm.add_widget( r )
		r.add_widget( cent )
		r.add_widget( fixed_cent ) 
		r.add_widget( step )
 
		cont.add_widget( self.expLabel )
		cont.add_widget( frm )
		cont.add_widget( btnConfirm )

		Popup.__init__( self, \
						title = 'Plotting Options', \
						content = cont, \
						size_hint = ( 0.95,0.95 ) )

	def open( self, someExpression, shellObj ) : 
		originalStdout = sys.stdout	  
		sys.stdout = wrString = WrappedString() 
		shellObj.console.push( "evalf(" + someExpression + ")" )
		sys.stdout = originalStdout
		if not wrString.contains( "Error" ) :
			self.expLabel.text = str( wrString )
			Popup.open( self )

	def dismiss( self, forced=False ) :
		Popup.dismiss( self )
		if forced : return
		
		return {"axisColor" : self.axisColor.rgb(), \
				"plotColor" : self.plotColor.rgb(), \
				"origin"	: (self.centx.value, self.centy.value), \
				"c_fixed"   : self.fixed_cent.active , \
				"step"	    : self.step.value }

# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.config import Config
import kivy.graphics as kg
from kivy.lang import Builder
from kivy.properties import BooleanProperty, ListProperty, NumericProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivyextras import ColorChooser, NumericUpDown
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

    bgColor = ListProperty( [0,0,0] )
    plotColor = ListProperty( [0,1,0] )
    axisColor = ListProperty( [1,1,1] )
    plotWidth = NumericProperty( 1 )
    axisWidth = NumericProperty( 1 )
    points = ListProperty( [] )
    xRange = ListProperty( [-1,1] )
    yRange = ListProperty( [-1,1] )
    step = NumericProperty( 0 )
    xpp = NumericProperty( 0 )
    ypp = NumericProperty( 0 )
    pinchWeight = NumericProperty( 5 )
    text = StringProperty( "" )
    _touches = ListProperty( [] )
    _stepAuto = BooleanProperty( True )
    _labels = ListProperty( [] )
    _foo_zeros = ObjectProperty( None )
    _foo_x_to_zero = ObjectProperty( None )
    _derivative_zeros = ObjectProperty( None )
    touching = BooleanProperty( False )

    def __init__( self, foo, config ) : 
        Widget.__init__( self )
        self.width = float( Config.get( 'graphics', 'width' ) )
        self.height = float( Config.get( 'graphics', 'height' ) )
        self.expr = foo

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
        self.setup( config )
        self.evalPoints()  
        self.evalPoints()  

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
                        kg.Line( dash_lenght=dl, dash_offset=do,\
                                 points=p, width=self.axisWidth,\
                                 group="intersections" )
                        kg.Point( pointsize=self.plotWidth*2,\
                                  points=[ (xi-self.xRange[0])*self.xpp, -self.yRange[0]*self.ypp ],\
                                  group="intersections" )
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
                kg.Line( dash_lenght=dl, dash_offset=do,\
                         points=p, width=self.axisWidth,\
                         group="intersections" )
                kg.Point( pointsize=self.plotWidth*2,\
                          points=[ -self.xRange[0]*self.xpp, (yi-self.yRange[0])*self.ypp ],\
                          group="intersections" )
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
                            kg.Line( dash_lenght=dl, dash_offset=do,\
                                     points=px, width=self.axisWidth,\
                                     group="minandmax" )
                            kg.Line( dash_lenght=dl, dash_offset=do,\
                                     points=py, width=self.axisWidth,\
                                     group="minandmax" )
                            kg.Point( pointsize=self.plotWidth*2,\
                                      points=[ (xi-self.xRange[0])*self.xpp, (yi-self.yRange[0])*self.ypp ],\
                                      group="minandmax" )
                        lbl = Label( center=(px[0],9*self.height/10.0), text=tx, markup=True )
                        self._labels.append( lbl )
                        lbl = Label( center=(4*self.width/5.0, py[1]), text=ty, markup=True )
                        self._labels.append( lbl )
                        self.add_widget( lbl )
                    except : pass


    def setup( self, config ) : 
        xToDisplay = 2
        yToDisplay = 2
        try :
            self.bgColor = config[ "bgColor" ]
        except KeyError : pass
        try :
            self.axisColor = config[ "axisColor" ]
        except KeyError : pass
        try :
            self.plotColor = config[ "plotColor" ]
        except KeyError : pass
        try :
            self.plotWidth = config[ "plotWidth" ]
        except KeyError : pass
        try :
            self.axisWidth = config[ "axisWidth" ]
        except KeyError : pass
        try :
            xToDisplay = config[ "x" ]
        except KeyError : 
            xToDisplay = 2
        try :
            yToDisplay = config[ "y" ]
        except KeyError : 
            yToDisplay = 2

        self.xRange = -xToDisplay/2.0, xToDisplay/2.0
        self.yRange = -yToDisplay/2.0, yToDisplay/2.0
        self.setupXYpp( xToDisplay, yToDisplay )
        try :
            if config[ "step" ] > 0 :
                self.step = config[ "step" ]
                self._stepAuto = False
        except KeyError : pass

    def setupXYpp( self, xtd=None, ytd=None ) :
        xToDisplay = xtd or self.xRange[1]-self.xRange[0]
        yToDisplay = ytd or self.yRange[1]-self.yRange[0]
        self.xpp = float( self.width ) / xToDisplay
        self.ypp = float( self.height ) / yToDisplay
        if self._stepAuto :
            self.step = xToDisplay / float( self.width )

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
        self.setupXYpp()
        self.evalPoints()
    
    def on_touch_down( self, touch ) :
        #add the touch to a special list
        self._touches.append( touch )
        #prepare its user data
        ud = touch.ud
        ud['group'] = g = str( touch.uid )
        #add new canvas instructions for it
        with self.canvas:
            ud['color'] = kg.Color( random(), 1, 1, mode='hsv', group=g )
            ud['lines'] = kg.Point( points=(touch.x, touch.y), pointsize=self.axisWidth, group=g )
        #grab it
        touch.grab(self)        
        return True

    def on_touch_up( self, touch ) :
        #remove the touch from the list
        for t in self._touches :
            if t.uid == touch.uid:
                self._touches.remove( t )
        #ungrub it
        if touch.grab_current is not self:
            return
        touch.ungrab( self )
        ud = touch.ud
        #and the delete its canvas instructions
        self.canvas.remove_group( ud['group'] )
        self.touching = False
        self.evalPoints()

    def on_touch_move( self, touch ) :
        self.touching = True
        #check if the touch is attached to this widget and get user data
        if touch.grab_current is not self:
            return
        ud = touch.ud
        #add new points to the canvas 
        points = ud['lines'].points
        oldx, oldy = points[-2], points[-1]
        points = calculate_Points(oldx, oldy, touch.x, touch.y)
        if points:
            try:
                lp = ud['lines'].add_point
                for idx in xrange(0, len(points), 2):
                    lp(points[idx], points[idx+1])
            except kg.GraphicException:
                pass
        #update touch living time
        t = int(time())
        if t not in ud:
            ud[t] = 1
        else:
            ud[t] += 1
        #check if the touch is sigle or multiple
        if len( self._touches ) == 1 :
            self.movePlot()
        elif len( self._touches ) == 2 :
            self.pinchZoom() 


class PlottingOptionPanel( Popup ) :
    
    errorsBefore = BooleanProperty( False )
    wrongExpression = BooleanProperty( False )

    def __init__( self, onConfirm ) :
        w = float( Config.get( 'graphics', 'width' ) )
        h = float( Config.get( 'graphics', 'height' ) )
        frm = BoxLayout( orientation="vertical" )
        cont = BoxLayout( orientation="vertical" )
        cont.spacing = 30

        bgColor = ColorChooser( label="Background Color :", rgb=[ 0, 0, 0 ] )
        plotColor = ColorChooser( label="Plot Color :", rgb=[ 0, 1, 0 ] )
        axisColor = ColorChooser( label="Axis Color :", rgb=[ 1, 1, 1 ] )
        self.colors = [ axisColor, bgColor, plotColor ]
        for x in self.colors : frm.add_widget( x )

        totx = BoxLayout( orientation="vertical" )
        totx.add_widget( Label( text="X to display :" ) )
        self.totx = NumericUpDown( vmin=2, value=w/16, vstep=1 )
        totx.add_widget( self.totx )

        toty = BoxLayout( orientation="vertical" )
        toty.add_widget( Label( text="Y to display :" ) )
        self.toty = NumericUpDown( vmin=2, value=h/16, vstep=1 )
        toty.add_widget( self.toty )

        step = BoxLayout( orientation="vertical" )
        step.add_widget( Label( text="X Step ( 0=Best ) :" ) )
        self.step = NumericUpDown( vmin=0, value=0, vstep=0.1 )
        step.add_widget( self.step )

        btnConfirm = Button( text="Ok, Plot!" )
        btnConfirm.bind( on_press=onConfirm )
        btnConfirm.size_hint = 1, 0.1

        self.expLabel = Label()
        self.expLabel.size_hint = 1, 0.1

        r = BoxLayout( orientation="horizontal" )
        r.spacing = 15
        frm.add_widget( r )
        r.add_widget( totx ) 
        r.add_widget( step )
        r.add_widget( toty )
 
        cont.add_widget( self.expLabel )
        cont.add_widget( frm )
        cont.add_widget( btnConfirm )

        Popup.__init__( self, title = 'Plotting Options', \
                              content = cont, 
                              size_hint = ( 0.95,0.95 ) )

    def open( self, someExpression, shellObj ) : 
        #push stdout
        originalStdout = sys.stdout
        no = WrappedString()            
        sys.stdout = no
        #Result to the WrappedString
        shellObj.console.push( "(" + someExpression + ").evalf()" )
        #check for error
        self.wrongExpression = no.contains( "Error" )
        if not self.wrongExpression :
            self.expLabel.text = str( no )
        else : 
            self.expLabel.text = "The expression is not valid!!" 
        #pop stdout
        sys.stdout = originalStdout
        #display the popup        
        Popup.open( self )
        return str( no )

    def dismiss( self, forced=False ) :
        if not forced : 
            self.errorsBefore = False
            Popup.dismiss( self ) 
            config = { "axisColor" : self.colors[0].rgb(), \
                       "bgColor"   : self.colors[1].rgb(), \
                       "plotColor" : self.colors[2].rgb(), \
                       "x"         : self.totx.value, \
                       "y"         : self.toty.value , \
                       "step"      : self.step.value }
            return config
        else : 
            Popup.dismiss( self )

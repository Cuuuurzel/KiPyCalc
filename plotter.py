# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.config import Config
from kivy.graphics import Color, Rectangle, Point, GraphicException
from kivy.lang import Builder
from kivy.properties import BooleanProperty, ListProperty, NumericProperty
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
from math import sqrt
from sympy.abc import *
from sympy.utilities.lambdify import lambdify
from random import random

Builder.load_file( "kipycalc.kv" )

def calculate_points(x1, y1, x2, y2, steps=5):
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
    _touches = ListProperty( [] )

    def __init__( self, foo, config ) : 
        Widget.__init__( self )
        self.width = float( Config.get( 'graphics', 'width' ) )
        self.height = float( Config.get( 'graphics', 'height' ) )
        self.expr = foo
        self.foo = lambdify( x, foo ) 
        self.setup( config )
        self.evalPoints()  

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

        self.step = xToDisplay / float( self.width )
        self.xpp = float( self.width ) / xToDisplay
        self.ypp = float( self.height ) / yToDisplay
        self.xRange = -xToDisplay/2.0, xToDisplay/2.0
        self.yRange = -yToDisplay/2.0, yToDisplay/2.0

        try :
            if config[ "step" ] > 0 :
                self.step = config[ "step" ]
        except KeyError : pass

    def evalPoints( self ) :
        points = []
        x = self.xRange[0]
        while x < self.xRange[1] : 
            try :
                y = self.foo( x )
                if self.yRange[0] < y < self.yRange[1] :
                    px = ( x - self.xRange[0] ) * self.xpp
                    py = ( y - self.yRange[0] ) * self.ypp
                    points.append( px )
                    points.append( py )
            except Exception : pass
            x += self.step
        self.points = points
    
    def on_touch_down( self, touch ) :
        #add the touch to a special list
        self._touches.append( touch )
        #prepare its user data
        ud = touch.ud
        ud['group'] = g = str( touch.uid )
        #add new canvas instructions for it
        with self.canvas:
            ud['color'] = Color(random(), 1, 1, mode='hsv', group=g)
            ud['lines'] = ( Point( points=(touch.x, touch.y), pointsize=self.axisWidth, group=g ) )
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

    def on_touch_move( self, touch ) :
        #check if the touch is attached to this widget and get user data
        if touch.grab_current is not self:
            return
        ud = touch.ud
        #add new points to the canvas 
        points = ud['lines'].points
        oldx, oldy = points[-2], points[-1]
        points = calculate_points(oldx, oldy, touch.x, touch.y)
        if points:
            try:
                lp = ud['lines'].add_point
                for idx in xrange(0, len(points), 2):
                    lp(points[idx], points[idx+1])
            except GraphicException:
                pass
        #update touch living time
        import time
        t = int(time.time())
        if t not in ud:
            ud[t] = 1
        else:
            ud[t] += 1
        #check if the touch is sigle or multiple
        if len( self._touches ) == 1 :
            self.movePlot()
        elif len( self._touches ) == 2 :
            self.pinchZoom() 

    def movePlot( self ) :
         dx = ( self._touches[0].px - self._touches[0].x )/( self.xpp )
         dy = ( self._touches[0].py - self._touches[0].y )/( self.ypp )
         self.xRange = self.xRange[0]+dx, self.xRange[1]+dx
         self.yRange = self.yRange[0]+dy, self.yRange[1]+dy
         self.evalPoints()

    def pinchZoom( self ) :
         d0x = ( self._touches[0].ox - self._touches[1].ox )
         d0y = ( self._touches[0].oy - self._touches[1].oy )
         d1x = ( self._touches[0].x - self._touches[1].x )
         d1y = ( self._touches[0].y - self._touches[1].y )
         dx = d0x - d1x
         dy = d0x - d1x
         self.xRange = self.xRange[0]-dx/2, self.xRange[1]+dx/2
         self.yRange = self.yRange[0]-dy/2, self.yRange[1]+dy/2
         self.evalPoints()


class PlottingOptionPanel( Popup ) :
    
    errorsBefore = BooleanProperty( False )

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
        self.toty = NumericUpDown( vmin=2, value=h, vstep=1 )
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

    def open( self, someExpression ) : 
        self.expLabel.text = someExpression
        Popup.open( self )

    def dismiss( self, forced=False ) :
        if not forced : 
            try :
                self.errorsBefore = False
                Popup.dismiss( self ) 
                config = { "axisColor" : self.colors[0].rgb(), \
                           "bgColor"   : self.colors[1].rgb(), \
                           "plotColor" : self.colors[2].rgb(), \
                           "x" : self.totx.value, \
                           "y" : self.toty.value , \
                           "step" : self.step.value }
                return config
            except ValueError : 
                if not self.errorsBefore : 
                    self.errorsBefore = True
                    self.expLabel.text += "\nCheck your input please!!"
        else : 
            Popup.dismiss( self )

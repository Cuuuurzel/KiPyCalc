# -*- coding: utf-8 -*-

import kivy
from kivy.app import App
from kivy.graphics import Canvas, Translate, Fbo, ClearColor, ClearBuffers
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
from random import random
from shell import DEBUG
from sympy import *
from sympy.abc import *
from sympy.utilities.lambdify import lambdify
import sys
from time import asctime
import traceback


#kivy.require('1.8.1')
Builder.load_file( "kipycalc.kv" )

ALPHABET = "ABCDEFGHJKILMNOPQRSTUVWXYZ"
FONT_NAME = "res/ubuntu-font-family-0.80/UbuntuMono-R.ttf"
FONT_SIZE = getFontSize()
        
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
        self.sPoints = spoints

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
# Multi plotter code.                                        #
############################################################
    
class Plotter( Widget ) :

    #Screenshots
    #btnss = ObjectProperty( None )

    #Special points
    spoints = ListProperty( [] )
    lblPoints = ObjectProperty( None )

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
    plotColor1 = ListProperty( [0,1,0] )
    plotColor2 = ListProperty( [1,0,0] )
    axisColor = ListProperty( [1,1,1] )
    #indicators
    x_scale_indicators_step = NumericProperty( 1.0 )
    y_scale_indicators_step = NumericProperty( 1.0 )
    indicators = ListProperty( [] )
    #List to handle touches
    touches = ListProperty( [] )
    touching = BooleanProperty( False )

    def __init__( self, functions, **kargs ) : 
        super( Plotter, self ).__init__( **kargs )
    
        self.width, self.height = screen_size()
        self.setConfig( kargs )

        self.lblPoints = Label( text="" )
        self.add_widget( self.lblPoints )
        self.lblPoints.pos = 2*self.width/3, 9*self.height/10

        if not hasattr( functions, '__iter__' ) :
            self.expr = functions
            self.foo = lambdify( x, functions )        
            self.lblPoints.font_name = FONT_NAME
            self.lblPoints.font_size = FONT_SIZE - 1
            self.fooStudy()
            functions = [ functions ]
        else :
            foo = functions[0]
    
        self.setup()
        self.loadFunctions( functions )
        self.evalPoints()  
        self.prepareCanvas()
        self.setIndicators()

    def screenshot( self, instance ) :    
        print( "oooooh" )
        self.get_parent_window().screenshot()
        s = asctime().replace( " ", "-" ) + ".png"
        self.export_to_png( "test.png" ) #Requires kivy 1.8.1 

    def setIndicators( self ) :
        for i in self.indicators : self.remove_widget( i )
        self.indicators = []
        y = int( floor( self.yRange[0] ) )
        x = int( floor( self.xRange[0] ) )
        
        #x indicators
        while x <= self.xRange[1] :
            if x != 0 :
                p = SpecialPoint( pcolor = ( 1, 1, 1, 1 ), \
                                  lcolor = ( 0, 0, 0, 0 ), \
                                  point = ( x, 0 ), \
                                  label = str( x ) )
                p.scale( self.xRange[0], self.yRange[0], \
                         self.ppx, self.ppy )
                self.add_widget( p )
                self.indicators.append( p )
            x += self.x_scale_indicators_step

        #y indicators
        while y <= self.yRange[1] :
            if y != 0 :
                p = SpecialPoint( pcolor = ( 1, 1, 1, 1 ), \
                                  lcolor = ( 0, 0, 0, 0 ), \
                                  point = ( 0, y ), \
                                  label = str( y ) )
                p.scale( self.xRange[0], self.yRange[0], \
                         self.ppx, self.ppy )
                self.add_widget( p )
                self.indicators.append( p )
            y += self.y_scale_indicators_step

    def setup( self ) : 
        xToDisplay = abs( float( self.xRange[1]-self.xRange[0] ) )
        yToDisplay = abs( float( self.yRange[1]-self.yRange[0] ) )
        self.ppx = self.width / xToDisplay
        self.ppy = self.height / yToDisplay
        self.step = xToDisplay / (self.width*3)
        self.x_scale_indicators_step = 1 + int( xToDisplay / 10 )
        self.y_scale_indicators_step = 1 + int( yToDisplay / 10 )
    
    def setColors( self ) :
        n = float( len( self.functions ) )

        #Paint the firt...
        self.functions[0].color = self.plotColor1 + [1]

        #...then shade
        if n > 1 :
            dc = list( map( lambda f,s:(s-f)/(n-1), self.plotColor1, self.plotColor2 ) )
            color = self.plotColor1

            for f in self.functions[1:]:
                color = list( map( lambda a,b:a+b, color, dc ) )
                f.color = color + [1]
        
    def setConfig( self, config ) :
        self.xRange = config[ "xRange" ]
        self.yRange = config[ "yRange" ]
        self.plotColor1 = config[ "plotColor1" ]
        self.plotColor2 = config[ "plotColor2" ]
        self.axisColor = config[ "axisColor" ]        

    def loadFunctions( self, functions ) :
        self.functions = []
        errors = False
        for f in functions :
            try :
                dfoo = DrawableFunction( 
                    foo = lambdify( x, f ), \
                    color = [ 1, 1, 1, 1 ]
                )
                self.functions.append( dfoo )
            except : 
                if DEBUG : print( traceback.format_exc() )         
                else : 
                    print( "Given input contains errors..." )
                    break
     
    def prepareCanvas( self ) :
        self.setColors()
        for f in self.functions :
            with self.canvas :
                kg.Color( f.color[0],f.color[1],f.color[2],f.color[3],
                          group="functions" )
                kg.Line( points=f.points, width=1, group="functions" )
                kg.Color( 1, 1, 1, 1, group="axis" )
                kg.Line( points=self.getXAxis(), width=1, group="axis" )
                kg.Line( points=self.getYAxis(), width=1, group="axis" )

    def getYAxis( self ) :
        return [ -self.xRange[0]*self.ppx, 0, -self.xRange[0]*self.ppx, self.height ]
                    
    def getXAxis( self ) :
        return [ 0, -self.yRange[0]*self.ppy, self.width, -self.yRange[0]*self.ppy ]

    def restoreCanvas( self ) :
        self.canvas.remove_group( "functions" )
        self.canvas.remove_group( "axis" )

    def evalPoints( self ) :
        if len( self.functions ) == 1 :
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
        
        for foo in self.functions :
            foo.eval( self.xRange[0], self.xRange[1], 
                      self.yRange[0], self.yRange[1],
                      self.ppx, self.ppy, self.step )
        self.restoreCanvas()
        self.prepareCanvas()

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
        #if not self.btnss.on_touch_down( touch ) :
        self.touches.append( touch )
        return True

    def on_touch_up( self, touch ) :
        #if not self.btnss.on_touch_up( touch ) :
        for t in self.touches :
            if t.uid == touch.uid:
                self.touches.remove( t )
        self.touching = False
        self.setIndicators()
        return True

    def on_touch_move( self, touch ) :
        if len( self.touches ) == 1 :
            self.movePlot()
        elif len( self.touches ) == 2 :
            self.pinchZoom() 
    
    def getConfig( self ) :
        return {
            "plotColor1" : self.plotColor1, \
            "plotColor2" : self.plotColor2, \
            "axisColor" : self.axisColor, \
            "xRange" : self.xRange, \
            "yRange" : self.yRange 
        }

#Code from the the original plotter
    
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
                #sp = SpecialPoint( font_size=FONT_SIZE-1, point=p, size=self.size, label=ALPHABET[i])
                sp = SpecialPoint( 
                    font_size = FONT_SIZE-1, \
                    point = p, \
                    size = ( self.size[0]*1.5, self.size[1]*1.5 ), \
                    label = ALPHABET[i]
                )
                self.add_widget( sp )        
                self.spoints.append( sp )
                self.lblPoints.text += "\n%s : ( %.3f, %.3f )" % ( ALPHABET[i], p[0], p[1] )
            except : pass


############################################################
# Plotting panel.                                          #
############################################################

class PlottingPanel( Popup ) :
    
    expText = StringProperty( "" )

    def __init__( self, onConfirm ) :
        super( Popup, self ).__init__()
        self.title     = 'Plotting Options'
        self.content   = self._generateContent( onConfirm )
        self.size_hint = ( 0.95, 0.95 )
        setFont( self.content, FONT_NAME, FONT_SIZE )
        self.expLabel.font_size = 5 * FONT_SIZE / 4

    def expLabelFix( self ) :
        width = self.expLabel.width = self.width
        txtLen = len( self.expLabel.text ) * self.expLabel.font_size

        if txtLen > width :
            n = int( width / FONT_SIZE )
            if n < txtLen :
                self.expLabel.text = self.expLabel.text[:n-3] + "..."

    def _generateContent( self, onConfirm ) :
        w, h = screen_size()
        cont = BoxLayout( orientation="vertical" )
        cont.spacing = 30
        cont.add_widget( self._generateExpLabel( cont ) )
        cont.add_widget( self._generateConfirmButton( onConfirm ) )
        """
        colorChoosingZone = self._generateColorChoosingZone()
        areaChoosingZone  = self._generateAreaChoosingZone()
        cont.add_widget( areaChoosingZone )
        cont.add_widget( colorChoosingZone )
        """
        return cont

    def _generateExpLabel( self, cont ) : 
        self.expLabel = Label( 
            text      = '', \
            size_hint = ( 1, 0.3 ), \
            shorten   = True
        )
        return self.expLabel

    def _generateConfirmButton( self, onConfirm ) :
        btnConfirm = Button( text="Ok, Plot!" )
        btnConfirm.bind( on_press=onConfirm )
        btnConfirm.size_hint = 1, 0.3
        return btnConfirm

    def open( self, shellObj, currentConfig=None ) : 
        shellObj._lastOutput = []
        shellObj.console.push( "evalf(" + shellObj.getInput() + ")" )

        if not DEBUG :
            self.expText = self.expLabel.shellObj = shellObj._lastOutput[-1]
            fullMsg = '\n'.join( shellObj._lastOutput )
            if not "Error" in fullMsg :
                self.expText = self.expLabel.text = shellObj._lastOutput[-2]
                Popup.open( self )
        else :
            self.expText = self.expLabel.text = "[ x**2-1, x**2-2, x**2-3 ]" #x
            Popup.open( self )
        self.expLabelFix()

    def dismiss( self ) :
        Popup.dismiss( self )
        if self.expLabel.text[0] in ( "[", "(" ) :
            return list( map( eval, self.expText[1:-1].split( "," ) ) )
        else :
            return eval( self.expText )

    def setConfig( self, config=None ) : pass

    def getConfig( self ) : 
        config = { 
            "axisColor"  : [ 1, 1, 1 ], \
            "plotColor1" : [ 0, 1, 0 ], \
            "plotColor2" : [ 1, 0 ,0 ], \
            "xRange"     : ( -1, 1 ), \
            "yRange"     : ( -1, 1 ) 
        }
        return config

"""
############################################################
# Old, Python 2.7 code for the plotting panel.             #
############################################################

class PlottingPanel( Popup ) :
    
    expText = StringProperty( "" )

    def __init__( self, onConfirm ) :
        super( Popup, self ).__init__( title     = 'Plotting Options', \
                                       content   = self._generateContent( onConfirm ), \
                                       size_hint = ( 0.95, 0.95 ) )
        setFont( self.content, FONT_NAME, FONT_SIZE )
        self.expLabel.font_size = 5 * FONT_SIZE / 4

    def expLabelFix( self ) :
        width = self.expLabel.width = self.width
        txtLen = len( self.expLabel.text ) * self.expLabel.font_size

        if txtLen > width :
            n = int( width / FONT_SIZE )
            if n < txtLen :
                self.expLabel.text = self.expLabel.text[:n-3] + "..."

    def _generateContent( self, onConfirm ) :
        w, h = screen_size()
        cont = BoxLayout( orientation="vertical" )
        cont.spacing = 30

        colorChoosingZone = self._generateColorChoosingZone()
        areaChoosingZone = self._generateAreaChoosingZone()

        cont.add_widget( self._generateExpLabel( cont ) )
        cont.add_widget( areaChoosingZone )
        cont.add_widget( colorChoosingZone )
        cont.add_widget( self._generateConfirmButton( onConfirm ) )
        
        return cont

    def _generateExpLabel( self, cont ) : 
        self.expLabel = Label( 
            size_hint = ( 1, 0.3 ), \
            shorten = True
        )
        return self.expLabel

    def _generateConfirmButton( self, onConfirm ) :
        btnConfirm = Button( text="Ok, Plot!" )
        btnConfirm.bind( on_press=onConfirm )
        btnConfirm.size_hint = 1, 0.3
        return btnConfirm

    def _generateAreaChoosingZone( self ) :
        self.xRangeMin = TextInput( text="-1", multiline=False, size_hint=[0.4,1] )
        self.xRangeMax = TextInput( text="+1", multiline=False, size_hint=[0.4,1] )
        self.yRangeMin = TextInput( text="-1", multiline=False, size_hint=[0.4,1] )
        self.yRangeMax = TextInput( text="+1", multiline=False, size_hint=[0.4,1] )

        r1 = BoxLayout( orientation="horizontal" )
        r1.spacing = 10
        r1.add_widget( Label( text="Var.", size_hint=[0.2,1]  ) )
        r1.add_widget( Label( text="From", size_hint=[0.4,1] ) )
        r1.add_widget( Label( text="To",   size_hint=[0.4,1] ) )

        r2 = BoxLayout( orientation="horizontal" )
        r2.spacing = 10
        r2.add_widget( Label( text="x :", size_hint=[0.2,1] ) )
        r2.add_widget( self.xRangeMin )
        r2.add_widget( self.xRangeMax )

        r3 = BoxLayout( orientation="horizontal" )
        r3.spacing = 10
        r3.add_widget( Label( text="y :", size_hint=[0.2,1] ) )
        r3.add_widget( self.yRangeMin )
        r3.add_widget( self.yRangeMax )
    
        a = BoxLayout( orientation="vertical" )
        a.spacing = 10
        a.add_widget( r1 )
        a.add_widget( r2 )
        a.add_widget( r3 )
        return a

    def _generateColorChoosingZone( self ) :        
        #Axis color
        self.axisColorChooser = ColorChooser( rgb = [ 1, 1, 1 ], \
                                              label = "Axis color :", \
                                              size_hint = ( 0.8, 0.4 ), \
                                              onDone = self.updateAxisColor )
        self.btnAxisColor = ColoredButton( color=[1,1,1] )
        self.btnAxisColor.bind( on_press=self.axisColorChooser.open )
        axisColorZone = BoxLayout()
        axisColorZone.add_widget( Label( text="Axis color : " ) )
        axisColorZone.add_widget( self.btnAxisColor )

        #First plot color
        self.plotColorChooser1 = ColorChooser( rgb = [ 0, 1, 0 ], \
                                               label = "First plot color :", \
                                               size_hint = ( 0.8, 0.4 ), \
                                               onDone = self.updatePlotColor1 )
        self.btnPlotColor1 = ColoredButton( color=[0,1,0] )
        self.btnPlotColor1.bind( on_press=self.plotColorChooser1.open )
        plotColor1Zone = BoxLayout()
        plotColor1Zone.add_widget( Label( text="1st plot color : " ) )
        plotColor1Zone.add_widget( self.btnPlotColor1 )

        #Second plot color
        self.plotColorChooser2 = ColorChooser( rgb = [ 1, 0, 0 ], \
                                               label = "Second plot color :", \
                                               size_hint = ( 0.8, 0.4 ), \
                                               onDone = self.updatePlotColor2 )
        self.btnPlotColor2 = ColoredButton( color=[1,0,0] )
        self.btnPlotColor2.bind( on_press=self.plotColorChooser2.open )
        plotColor2Zone = BoxLayout()
        plotColor2Zone.add_widget( Label( text="2nd plot color :" ) )
        plotColor2Zone.add_widget( self.btnPlotColor2 )
        
        #Packing
        colorChoosingZone = BoxLayout( orientation="vertical" )
        colorChoosingZone.add_widget( axisColorZone )
        colorChoosingZone.add_widget( plotColor1Zone )
        colorChoosingZone.add_widget( plotColor2Zone )
        return colorChoosingZone

    def updateAxisColor( self, instance ) :
        self.btnAxisColor.color = instance.rgb()

    def updatePlotColor1( self, instance ) :
        self.btnPlotColor1.color = instance.rgb()

    def updatePlotColor2( self, instance ) :
        self.btnPlotColor2.color = instance.rgb()

    def open( self, shellObj, currentConfig=None ) : 
        shellObj._lastOutput = []
        shellObj.console.push( "evalf(" + shellObj.getInput() + ")" )

        if not DEBUG :
            self.expText = self.expLabel.text = shellObj._lastOutput[-1]
            fullMsg = join( shellObj._lastOutput, "\n" )
            if not "Error" in fullMsg :
                self.expText = self.expLabel.text = shellObj._lastOutput[-2]
                Popup.open( self )
        else :
            self.expText = self.expLabel.text = "x" #"[ x**2-1, x**2-2, x**2-3 ]"
            Popup.open( self )
        self.expLabelFix()

    def dismiss( self ) :
        if ( self.axisColorChooser.isShown or
             self.plotColorChooser1.isShown or 
             self.plotColorChooser2.isShown ) :
            self.axisColorChooser.dismiss()
            self.plotColorChooser1.dismiss() 
            self.plotColorChooser2.dismiss()
            return None
        else :
            Popup.dismiss( self )
            if self.expLabel.text[0] in ( "[", "(" ) :
                return map( eval, self.expText[1:-1].split( "," ) )
            else :
                return eval( self.expText )

    def setConfig( self, config=None ) :
        if not config is None :
            self.plotColorChooser1.setRGB( config[ "plotColor1" ] )
            self.plotColorChooser2.setRGB( config[ "plotColor2" ] )
            self.axisColorChooser.setRGB( config[ "axisColor" ] )
            self.btnPlotColor1.color = config[ "plotColor1" ]
            self.btnPlotColor2.color = config[ "plotColor2" ]
            self.btnAxisColor.color = config[ "axisColor" ]
            self.xRangeMin.text = str( config[ "xRange" ][0] )
            self.xRangeMax.text = str( config[ "xRange" ][1] )
            self.yRangeMin.text = str( config[ "yRange" ][0] )
            self.yRangeMax.text = str( config[ "yRange" ][1] )

    def getConfig( self ) : 
        config = { 
            "axisColor" : self.axisColorChooser.rgb(), \
            "plotColor1" : self.plotColorChooser1.rgb(), \
            "plotColor2" : self.plotColorChooser2.rgb(), \
               "xRange"    : ( float( self.xRangeMin.text ), float( self.xRangeMax.text ) ), \
            "yRange"    : ( float( self.yRangeMin.text ), float( self.yRangeMax.text ) ) 
        }
        return config
"""

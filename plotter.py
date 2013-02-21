# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.config import Config
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
from sympy import *
from sympy.abc import *
from sympy.utilities.lambdify import lambdify

FONT_NAME = "res/font/ubuntu-mono/UbuntuMono-R.ttf"
FONT_SIZE = 24
Builder.load_file( "kipycalc.kv" )


class Plotter( Widget ) :

    points = ListProperty( [] )
    bgColor = ListProperty( [0,0,0] )
    plotColor = ListProperty( [0,1,0] )
    axisColor = ListProperty( [1,1,1] )
    xRange = ListProperty( [-1,1] )
    plotWidth = NumericProperty( 1 )
    axisWidth = NumericProperty( 1 )
    yscale = NumericProperty( 1 )
    origin = ListProperty( [ 0, 0 ] )

    def __init__( self, foo, origin, config ) : 
        Widget.__init__( self )
        self.foo = lambdify( x, foo ) 
        self.origin = origin
        self.trySetup( config )
        yd = 3 * float( Config.get( 'graphics', 'height' ) ) / 2
        self.yRange = -yd, yd
        self.step = self.goodStep( config )
        self.points = self.evalPoints()

    def trySetup( self, config ) : 
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
            self.yscale = config[ "yscale" ]
        except KeyError : pass
        try :
            self.xRange = config[ "xRange" ]
        except KeyError : pass
 
    def goodStep( self, config ) :
        if "step" in config.keys() and config[ "step" ] != 0 :
            return config[ "step" ]
        else : 
            w = float( Config.get( 'graphics', 'width' ) )
            xd = abs( self.xRange[1] - self.xRange[0] )
            s = float( xd ) / w
        return s 

    def evalPoints( self ) :
        points = []
        x = self.xRange[0]
        while x < self.xRange[1] : 
            y = self.foo( x )
            if self.yRange[0] < y < self.yRange[1] :
                points.append( x/self.step + self.origin[0] )
                points.append( y + self.origin[1] )
            x += self.step
        return points

    def on_touch_move( self, touch ) :
        dx = ( self.origin[0] - touch.x ) * self.step
        self.origin = touch.x, touch.y
        self.xRange = self.xRange[0]+dx, self.xRange[1]+dx

    def on_touch_up( self, touch ) :
        self.on_touch_move( touch )
        self.points = self.evalPoints() 


class PlottingOptionPanel( Popup ) :
    
    errorsBefore = BooleanProperty( False )

    def __init__( self, onConfirm ) :
        cont = BoxLayout( orientation="vertical" )
        optionPanel = BoxLayout( orientation="horizontal" )
        frm1 = BoxLayout( orientation="vertical" )
        frm2 = BoxLayout( orientation="vertical" )
        optionPanel.spacing = 30
        cont.spacing = 30

        bgColor = ColorChooser( label="Background Color :", rgb=[ 0, 0, 0 ] )
        plotColor = ColorChooser( label="Plot Color :", rgb=[ 0, 1, 0 ] )
        axisColor = ColorChooser( label="Axis Color :", rgb=[ 1, 1, 1 ] )
        self.colors = [ axisColor, bgColor, plotColor ]

        xMin = BoxLayout( orientation="vertical" )
        xMin.add_widget( Label( text="Min X : " ) )
        self.xMin = NumericUpDown( value=-100, vstep=0.1 )
        xMin.add_widget( self.xMin )
 
        xMax = BoxLayout( orientation="vertical" )
        xMax.add_widget( Label( text="Max X : " ) )
        self.xMax = NumericUpDown( value=100, vstep=0.1 )
        xMax.add_widget( self.xMax )
 
        step = BoxLayout( orientation="vertical" )
        step.add_widget( Label( text="X-Step ( 0=Best ) : " ) )
        self.step = NumericUpDown( vmin=0, value=0, vstep=0.1 )
        step.add_widget( self.step )

        btnConfirm = Button( text="Ok, Plot!" )
        btnConfirm.bind( on_press=onConfirm )
        btnConfirm.size_hint = 1, 0.1

        self.expLabel = Label()
        self.expLabel.size_hint = 1, 0.1

        for x in self.colors : frm1.add_widget( x )

        frm2.add_widget( step )
        frm2.add_widget( xMin )
        frm2.add_widget( xMax )

        optionPanel.add_widget( frm1 )
        optionPanel.add_widget( frm2 )
        cont.add_widget( self.expLabel )
        cont.add_widget( optionPanel )
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
                           "step"      : self.step.value, \
                           "xRange"    : [ self.xMin.value, self.xMax.value ] }
                return config
            except ValueError : 
                if not self.errorsBefore : 
                    self.errorsBefore = True
                    self.expLabel.text += "\nCheck your input please!!"
        else : 
            Popup.dismiss( self )











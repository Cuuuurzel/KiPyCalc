# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.config import Config
from kivy.lang import Builder
from kivy.properties import ListProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from sympy import *
from sympy.abc import *
from sympy.utilities.lambdify import lambdify

from kivyextras import ColorChooser

FONT_NAME = "res/font/ubuntu-mono/UbuntuMono-R.ttf"
FONT_SIZE = 24
Builder.load_file( "kipycalc.kv" )

class Plotter( Widget ) :

    points = ListProperty( [] )
    bgColor = ListProperty( [0,0,0] )
    plotColor = ListProperty( [0,1,0] )
    axiscolor = ListProperty( [1,1,1] )
    xRange = ListProperty( [-1,1] )
    plotWidth = NumericProperty( 1 )
    axisWidth = NumericProperty( 1 )
    xscale = NumericProperty( 1 )
    yscale = NumericProperty( 1 )

    def __init__( self, foo, origin, yRange, kargs ) : 
        Widget.__init__( self )
        self.foo = lambdify( x, foo ) 
        self.origin = origin
        self.trySetup( kargs )
        self.yRange = yRange
        self.step = self.goodStep()
        self.points = self.evalPoints()

    def trySetup( self, kargs ) : 
        try :
            self.bgColor = kargs[ "bgColor" ]
        except KeyError : pass
        try :
            self.axiscolor = kargs[ "axiscolor" ]
        except KeyError : pass
        try :
            self.plotColor = kargs[ "plotColor" ]
        except KeyError : pass
        try :
            self.plotWidth = kargs[ "plotWidth" ]
        except KeyError : pass
        try :
            self.axisWidth = kargs[ "axisWidth" ]
        except KeyError : pass
        try :
            self.xscale = kargs[ "xscale" ]
        except KeyError : pass
        try :
            self.yscale = kargs[ "yscale" ]
        except KeyError : pass
        try :
            self.xRange = kargs[ "xRange" ]
        except KeyError : pass

    def goodStep( self ) :
        dx = abs( self.xRange[0] - self.xRange[1] )
        w = Config.get( 'graphics', 'width' )
        return 1 

    def evalPoints( self ) :
        print( "Calculating points... " ),
        points = []
        x = self.xRange[0]
        while x < self.xRange[1] : 
            y = self.foo( x )
            if self.yRange[0] < y < self.yRange[1] :
                points.append( x*self.xscale + self.origin[0] )
                points.append( y*self.yscale + self.origin[1] )
            x += self.step
        print "DONE"
        return points


class PlottingOptionPanel( Popup ) :

    def __init__( self, onConfirm ) :
        cont = BoxLayout( orientation="vertical" )
        optionPanel = BoxLayout( orientation="horizontal" )
        frm1 = BoxLayout( orientation="vertical" )
        frm2 = BoxLayout( orientation="vertical" )
        self.errorsBefore = True

        bgColor = ColorChooser( "Background Color :", [ 0, 0, 0 ] )
        bgColor.size_hint = 1, 0.2
        plotColor = ColorChooser( "Plot Color :", [ 0, 1, 0 ] )
        plotColor.size_hint = 1, 0.2
        axisColor = ColorChooser( "Axis Color :", [ 1, 1, 1 ] )
        axisColor.size_hint = 1, 0.2
        self.colors = [ axisColor, bgColor, plotColor ]

        plotwidth = BoxLayout( orientation="horizontal" )
        plotwidth.add_widget( Label( text="Plot width : " ) )
        self.plotWidth = Slider( min=1, max=5, value=1 )
        plotwidth.add_widget( self.plotWidth )
        plotwidth.size_hint = 1, 0.1

        axiswidth = BoxLayout( orientation="horizontal" )
        axiswidth.add_widget( Label( text="Axis width : " ) )
        self.axisWidth = Slider( min=1, max=5, value=1 )
        axiswidth.add_widget( self.axisWidth )
        axiswidth.size_hint = 1, 0.1

        xscale = BoxLayout( orientation="horizontal" )
        xscale.add_widget( Label( text="X Scale : " ) )
        self.xscale = TextInput( text="1" )
        xscale.add_widget( self.xscale )
        xscale.size_hint = 1, 0.1
 
        yscale = BoxLayout( orientation="horizontal" )
        yscale.add_widget( Label( text="Y Scale : " ) )
        self.yscale = TextInput( text="0.05" )
        yscale.add_widget( self.yscale )
        yscale.size_hint = 1, 0.1
 
        xMin = BoxLayout( orientation="horizontal" )
        xMin.add_widget( Label( text="Min X : " ) )
        self.xMin = TextInput( text="-240" )
        xMin.add_widget( self.xMin )
        xMin.size_hint = 1, 0.1
 
        xMax = BoxLayout( orientation="horizontal" )
        xMax.add_widget( Label( text="Max X : " ) )
        self.xMax = TextInput( text="240" )
        xMax.add_widget( self.xMax )
        xMax.size_hint = 1, 0.1

        btnConfirm = Button( text="Ok, Plot!" )
        btnConfirm.bind( on_press=onConfirm )
        btnConfirm.size_hint = 1, 0.1

        self.expLabel = Label()
        self.expLabel.size_hint = 1, 0.1

        for x in self.colors : frm1.add_widget( x )

        frm2.add_widget( plotwidth )
        frm2.add_widget( axiswidth )
        frm2.add_widget( xscale )
        frm2.add_widget( yscale )
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
                minx = float( self.xMin.text )
                maxx = float( self.xMax.text )
                xScale = float( self.xscale.text )
                yScale = float( self.yscale.text )
                self.errorsBefore = False
                Popup.dismiss( self ) 
                config = { "axisColor" : self.colors[0].rgb(), \
                           "bgColor"   : self.colors[1].rgb(), \
                           "plotColor" : self.colors[2].rgb(), \
                           "axisWidth" : self.axisWidth.value, \
                           "plotWidth" : self.plotWidth.value, \
                           "xscale"    : xScale, \
                           "yscale"    : yScale, \
                           "xRange"    : [ minx, maxx ] }
                print( config )
                return config
            except ValueError : 
                if not self.errorsBefore : 
                    self.errorsBefore = True
                    self.expLabel.text += "\nCheck your input please!!"
        else : 
            Popup.dismiss( self )











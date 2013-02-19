# -*- coding: utf-8 -*-

from code import InteractiveConsole
from copy import deepcopy
from kivy.app import App
from kivy.base import EventLoop
from kivy.clock import Clock
from kivy.config import Config
from kivy.graphics import *
from kivy.lang import Builder
from kivy.properties import ListProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from sympy import *
from sympy.abc import *
from sympy.utilities.lambdify import lambdify
import sys

from shell import *
from plotter import *

DEBUG = True
FONT_NAME = "res/font/ubuntu-mono/UbuntuMono-R.ttf"
FONT_SIZE = 24
Builder.load_file( "kipycalc.kv" )

class KiPyCalc( BoxLayout ) :

    def __init__( self, **kargs ) :
        BoxLayout.__init__( self, orientation="vertical" )
        self.shell = PyShell( self.onPlotRequest )
        self.plotter = None
        self.add_widget( self.shell ) 
        self.plotterMode = False
        self.plottingOptionPanel = PlottingOptionPanel( self.onPlotConfirm )

    def start( self ) : 
        self.shell.start()

    def onPlotRequest( self, instance ) : 
        self.plotterMode = True
        print( "Plot Mode On..." )
        exp = self.shell.kb.current.text
        self.plottingOptionPanel.open( exp )

    def onPlotConfirm( self, instance ) :
        options = self.plottingOptionPanel.dismiss()
        if options != None :
            self.plotter = Plotter( eval( self.shell.kb.current.text ), \
                                    [ self.width/2, self.height/2 ], \
                                    [ -self.height/2, self.height/2 ], \
                                    options ) 
            self.clear_widgets()
            self.add_widget( self.plotter )

    def onReturnKey( self ) :
        if self.plotterMode :
            self.plotterMode = False
            print( "Plot Mode Off..." )
            self.clear_widgets()
            self.add_widget( self.shell )
            self.plottingOptionPanel.dismiss( True )


class KiPyCalcApp( App ) : 

    icon = 'res/icon.png'
    title = 'KiPyCalc'
    
    def build( self ) :
        self.kpc = KiPyCalc()
        self.kpc.start()
        EventLoop.window.bind( on_keyboard=self.hook_keyboard )
        return self.kpc

    def hook_keyboard( self, window, key, *largs ):
        if key == 27 :
            self.kpc.onReturnKey() 
            return True 


if __name__ in [ "__android__", "__main__" ] :
    KiPyCalcApp().run()

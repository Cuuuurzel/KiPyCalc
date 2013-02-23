# -*- coding: utf-8 -*-

from code import InteractiveConsole
from kivy.app import App
from kivy.base import EventLoop
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout

from shell import *
from plotter import *
from kivyextras import *

FONT_NAME = "res/font/ubuntu-mono/UbuntuMono-R.ttf"
FONT_SIZE = 24

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
        exp = self.shell.kb.current.text
        self.plottingOptionPanel.open( exp )

    def onPlotConfirm( self, instance ) :
        options = self.plottingOptionPanel.dismiss()
        if options != None :
            self.plotter = Plotter( eval( self.shell.kb.current.text ), \
                                    #[ self.width/2, self.height/2 ], \
                                    options ) 
            self.clear_widgets()
            self.add_widget( self.plotter )

    def onReturnKey( self ) :
        if self.plotterMode :
            self.plotterMode = False
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

    def on_pause( self ) : return True

if __name__ in [ "__android__", "__main__" ] :
    KiPyCalcApp().run()

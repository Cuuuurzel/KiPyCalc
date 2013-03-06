# -*- coding: utf-8 -*-

from code import InteractiveConsole
from kivy.app import App
from kivy.base import EventLoop
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from shell import *
from plotter import *
from kivyextras import *
from tutorial import *


class KiPyCalc( BoxLayout ) :

    def __init__( self, **kargs ) :
        BoxLayout.__init__( self, orientation="vertical" )
        self.shell = PyShell( self.onPlotRequest )
        self.plotter = None
        self.add_widget( self.shell ) 
        self.mode = "calc"
        self.plottingOptionPanel = PlottingOptionPanel( self.onPlotConfirm )      
        self.helpPanel = HelpPanel()        
        self._fooToPlot = None

    def start( self ) : 
        self.shell.start()

    def onPlotRequest( self, instance ) : 
        self.mode = "plot"
        exp = self.shell.kb.current.text
        self._fooToPlot = self.plottingOptionPanel.open( exp, self.shell )  

    def onPlotConfirm( self, instance ) :
        options = self.plottingOptionPanel.dismiss()
        if options != None and not self.plottingOptionPanel.wrongExpression :
            self.plotter = Plotter( eval( self._fooToPlot ), \
                                    options ) 
            self.clear_widgets()
            self.add_widget( self.plotter )

    def onHelpRequest( self ) : 
        self.mode = "help"
        self.helpPanel.open()

    def onReturnKey( self ) :
        if self.mode == "plot" :
            self.mode = "calc"
            self.clear_widgets()
            self.add_widget( self.shell )
            self.plottingOptionPanel.dismiss( True )
            return True
        else : 
            return False

    def onMenuKey( self ) :
        if self.mode == "plot" :
            self.onPlotRequest( None )
            return True
        elif self.mode == "calc" : 
            self.onHelpRequest()
            return True


class KiPyCalcApp( App ) : 

    icon = 'res/icon.png'
    title = 'KiPyCalc'
    
    def build( self ) :
        self.kpc = KiPyCalc()
        self.kpc.start()
        EventLoop.window.bind( on_keyboard=self.hook_keyboard )
        return self.kpc

    def hook_keyboard( self, window, key, *largs ):
        if key == 27 : #return (esc) key
            return self.kpc.onReturnKey() 
        if key == 319 : #menu key
            return self.kpc.onMenuKey() 
        

    def on_pause( self ) : 
         return True

if __name__ in [ "__android__", "__main__" ] :
    KiPyCalcApp().run()

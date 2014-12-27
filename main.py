# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.base import EventLoop
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from shell import *
from plotter import *
from kivyextras import *

from sympy import *
from sympy.abc import *

FONT_NAME = "res/ubuntu-font-family-0.80/UbuntuMono-R.ttf"
FONT_SIZE = getFontSize()

Config.set( 'kivy', 'keyboard', 'system' )

class KiPyCalc( BoxLayout ) :

	def __init__( self, **kargs ) :
		BoxLayout.__init__( self, orientation="vertical" )
		self.shell = PyShell( self.onPlotRequest )
		self.add_widget( self.shell ) 
		self.plotter = None
		self.plotterConfig = None
		self.mode = "calc"
		self.plottingPanel = PlottingPanel( self.onPlotConfirm )	  

	def start( self ) : 
		self.shell.start()

	def onPlotRequest( self, instance ) : 
		self.plottingPanel.setConfig( self.plotterConfig )
		self.plottingPanel.open( self.shell )

	def onPlotConfirm( self, instance ) :
		self.mode = "plot"
		foos = self.plottingPanel.dismiss()
		self.plotterConfig = self.plottingPanel.getConfig()
		self.plotter = self.getPlotter( foos )
		self.clear_widgets()
		self.add_widget( self.plotter )

	def getPlotter( self, foos ) :
		return Plotter( foos, **self.plotterConfig )
		"""
		try : 
			if len( foos ) == 1 :
				return SinglePlotter( foos, **self.plotterConfig )
			return Plotter( foos, **self.plotterConfig )
		except TypeError :
			return SinglePlotter( foos, **self.plotterConfig )
		"""

	def onReturnKey( self ) :
		res = self.plottingPanel.dismiss()		
		if res != None :
			if self.mode == "plot" :
				self.mode = "calc"
				self.clear_widgets()
				self.add_widget( self.shell )
				return True
		else : 
			return True

	def onMenuKey( self ) :
		if self.mode == "plot" :
			self.plotterConfig["xRange"] = self.plotter.xRange
			self.plotterConfig["yRange"] = self.plotter.yRange
			self.onPlotRequest( None )
		return True

class KiPyCalcApp( App ) : 

	icon = 'res/icon.png'
	title = 'Kipycalc'
	
	def build( self ) :
		self.kpc = KiPyCalc()
		self.kpc.start()
		EventLoop.window.bind( on_keyboard=self.hook_keyboard )
		return self.kpc

	def hook_keyboard( self, window, key, *largs ):
		if key == 27 : 
			return self.kpc.onReturnKey() 
		if key == 319 :
			return self.kpc.onMenuKey()		 

	def on_pause( self ) : 
		 return True

if __name__ in [ "__android__", "__main__" ] :
	KiPyCalcApp().run()

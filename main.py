# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.base import EventLoop
from kivy.uix.boxlayout import BoxLayout
from shell import *
from plotter import *
from kivyextras import *

class KiPyCalc( BoxLayout ) :

	def __init__( self, **kargs ) :
		BoxLayout.__init__( self, orientation="vertical" )
		self.shell = PyShell( self.onPlotRequest )
		self.add_widget( self.shell ) 
		self.plotter = None
		self.mode = "calc"
		self.plottingOptionPanel = PlottingOptionPanel( self.onPlotConfirm )	  
		self._fooToPlot = None

	def start( self ) : 
		self.shell.start()

	def onPlotRequest( self, instance ) : 
		self.mode = "plot"
		try :
			self.plottingOptionPanel.open( self.shell.kb.current.text, self.shell, self.plotter.getConfig() )  
		except AttributeError : 
			self.plottingOptionPanel.open( self.shell.kb.current.text, self.shell )  

	def onPlotConfirm( self, instance ) :
		options, foo = self.plottingOptionPanel.dismiss()
		self.plotter = Plotter( foo, **options ) 
		self.clear_widgets()
		self.add_widget( self.plotter )

	def onReturnKey( self ) :
		if self.mode == "plot" :
			self.mode = "calc"
			self.clear_widgets()
			self.add_widget( self.shell )
			self.plottingOptionPanel.dismiss( True )
			return True

	def onMenuKey( self ) :
		if self.mode == "plot" :
			self.onPlotRequest( None )
			return True
		else : 
			AboutMenu().open()
			return True


class AboutMenu( Popup ) :

	def __init__( self ) :
		w, h = screen_size()
		frm = BoxLayout( orientation="vertical" )
		cont = BoxLayout( orientation="vertical" )
		cont.spacing = 30
		lbl = Label( markup=True, text="""
Welcome to the About Panel.

[color=#FFaaaa]If you'd like to
plot more function at once,
or just want to pay me a beer...[/color]
[color=#aaaaFF]Consider buying the paid version this app!
(Also a good rating makes me happy)[/color]

[color=#FFaaaa]For any bug segnalation,
question,
or feature request, 
just write to me : [/color]
[color=#aaaaFF]cuuuurzel@gmail.com[/color]
""")
		cont.add_widget( lbl )
		Popup.__init__( self, \
						title = 'About Menu', \
						content = cont, \
						size_hint = ( 0.95,0.95 ) )

	def dismiss( self ) :
		Popup.dismiss( self )


class KiPyCalcApp( App ) : 

	icon = 'res/icon.png'
	title = 'Kipycalc'
	
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

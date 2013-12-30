# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.base import EventLoop
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from shell import *
from plotter import *
from kivyextras import *

from sympy import *
from sympy.abc import *

FONT_NAME = "res/ubuntu-font-family-0.80/UbuntuMono-R.ttf"
FONT_SIZE = getFontSize()

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
		try : 
			if len( foos ) == 1 :
				return SinglePlotter( foos, **self.plotterConfig )
			return Plotter( foos, **self.plotterConfig )
		except TypeError :
			return SinglePlotter( foos, **self.plotterConfig )

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
		else : 
			AboutMenu().open()
			return True


class AboutMenu( Popup ) :

	def __init__( self ) :
		w, h = screen_size()
		frm = BoxLayout( orientation="vertical" )
		cont = BoxLayout( orientation="vertical" )
		cont.spacing = 30

		self.text1="""
[color=#aaaaFF]Thank you for downloading this app![/color]

[color=#aaFFaa]To plot more function at once,
just list them, and press "plot", for example :
x**3 -4*x, x**3 -3*x, x**3 -2*x 
separated by comma.[/color]

[color=#FFaaaa]For any bug segnalation,
question, 
or feature request, 
just write to me : [/color]
[color=#aaaaFF]cuuuurzel@gmail.com[/color]
"""
		self.text2 = """
[color=#44DD44]More technical details...
The plotter will accept any list-like input!
Some example :
#1. Directly type a list and press plot...
[ x, x+1, x+2, x+3, x+4 ] 

#2. Use Python! Populate a list and the plot it...
myList = []
for i in range(0,5) : 
	myList.append( x+i )

#3. Use Functional Programming!
map( lambda i: x+i, range(0,10) )[/color]
"""
		self.lbl = Label( markup=True, text=self.text1 )
		cont.add_widget( self.lbl )
		btn = Button( text="..." )
		btn.size_hint = 1, 0.1
		btn.bind( on_press=self.more )
		cont.add_widget( btn )
		Popup.__init__( self, \
						title = 'About Menu', \
						content = cont, \
						size_hint = ( 0.95,0.95 ) )
		setFont( self.content, FONT_NAME, FONT_SIZE )

	def more( self, instance ) : 
		if self.lbl.text == self.text1 :
			self.lbl.text = self.text2
		else : 
			self.lbl.text = self.text1

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

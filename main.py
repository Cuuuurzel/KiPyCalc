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
FONT_SIZE = 16

class KiPyCalc( BoxLayout ) :

	def __init__( self, **kargs ) :
		BoxLayout.__init__( self, orientation="vertical" )
		self.shell = PyShell( self.onPlotRequest )
		self.add_widget( self.shell ) 
		self.plotter = None
		self.mode = "calc"
		self.plottingPanel = PlottingPanel( self.onPlotConfirm )	  
		self._fooToPlot = None

	def start( self ) : 
		self.shell.start()

	def onPlotRequest( self, instance ) : 
		self.plottingPanel.open( self.shell )

	def onPlotConfirm( self, instance ) :
		self.mode = "plot"
		foos = self.plottingPanel.dismiss()
		self.plotter = self.getPlotter( foos )
		self.clear_widgets()
		self.add_widget( self.plotter )

	def getPlotter( self, foos ) :
		n = 5
		foos = map( lambda f,i:f-i*x/n, [x**3]*n, range(0,n) )
		foos = x**3 - 3*x
		try : 
			if len( foos ) == 1 :
				return SinglePlotter( foos )
			return Plotter( foos )
		except TypeError :
			return SinglePlotter( foos )

	def onReturnKey( self ) :
		self.plottingPanel.dismiss( True )
		if self.mode == "plot" :
			self.mode = "calc"
			self.clear_widgets()
			self.add_widget( self.shell )
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
for example :
foos = []
for i in range(1,4) :
    foos.append( x**3 - i*x )
and then type "foos" and press plot...
...Or, less trivially :
map( lambda f,i : f - i*x, \\
     [ x**3 ]*10, \\
     range(0,10) )[/color]
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

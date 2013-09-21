from kivy.config import Config
from kivy.lang import Builder
from kivy.properties import *
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.uix.widget import Widget

Builder.load_file( "kivyextras.kv" )

def screen_size() : return float( Config.get( 'graphics', 'width' ) ), float( Config.get( 'graphics', 'height' ) )

def setFont( widget, fn, fs ) :
	try :
		widget.font_name = fn
		widget.font_size = fs
		for child in widget.children :	
			setFont( child, fn, fs )
	except AttributeError : pass

class ColoredButton( Button ) :
	
	color = ListProperty( [0,0,0] )

	def __init__( self, **kargs ) :
		super( ColoredButton, self ).__init__( **kargs )
		self.color = self._getDefaultColor( kargs )

	def _getDefaultColor( self, kargs ) :
		try :
			return kargs[ 'rgb' ]
		except KeyError : 
			return 0,0,0

class ColorChooser( Popup ) :
 
	sldr = ObjectProperty( None )
	sldg = ObjectProperty( None )
	sldb = ObjectProperty( None )
	isShown = BooleanProperty( False )
	originalColor = ListProperty( [0,0,0,1] )
	onDone = ObjectProperty( lambda x=0:x )

	def __init__( self, **kargs ) : 
		self.sldr = Slider( min=0, max=100 ) 
		self.sldg = Slider( min=0, max=100 ) 
		self.sldb = Slider( min=0, max=100 ) 

		self.originalColor = self._getDefaultColor( kargs )
		self.setRGB( self.originalColor )
		self._setOnDone( kargs )

		cont = BoxLayout( orientation="vertical" )
		cont.add_widget( self._getLabeledSlider( self.sldr, "R : " ) )
		cont.add_widget( self._getLabeledSlider( self.sldg, "G : " ) )
		cont.add_widget( self._getLabeledSlider( self.sldb, "B : " ) )
		cont.add_widget( self._getButtons() )

		Popup.__init__( self, \
						title = self._getLabel( kargs ), \
						content = cont, \
						size_hint = self._getSizeHint( kargs ) )

	def _getSizeHint( self, kargs ) :
		try :
			return kargs["size_hint"]
		except KeyError : 	
			return ( 0.9, 0.9 ) 

	def _setOnDone( self, kargs ) :
		try :
			self.onDone = kargs["onDone"]
		except KeyError : pass		
	
	def open( self, instance=None ) : 
		self.isShown = True
		Popup.open( self ) 

	def dismiss( self, instance=None ) : 
		self.isShown = False
		Popup.dismiss( self ) 

	def done( self, instance=None ) :	
		self.onDone( self )
		self.dismiss()

	def rgb( self ) : 
		return self.sldr.value_normalized, \
			   self.sldg.value_normalized, \
			   self.sldb.value_normalized

	def setRGB( self, color ) : 
		self.sldr.value_normalized = color[0]
		self.sldg.value_normalized = color[1]
		self.sldb.value_normalized = color[2]

	def _getButtons( self ) :
		btnDismiss = Button( text="Done" )
		btnDismiss.bind( on_press=self.done )
		btnCancel = Button( text="Cancel" )
		btnCancel.bind( on_press=self.cancel )
		buttons = BoxLayout()
		buttons.add_widget( btnDismiss )
		buttons.add_widget( btnCancel )
		return buttons

	def cancel( self, instance ) : 
		self.setRGB( self.originalColor )
		self.dismiss()		

	def _getLabeledSlider( self, slider, label ) :
		b = BoxLayout()
		l = Label( text=label )
		l.size_hint = 0.1, 1
		b.add_widget( l )
		b.add_widget( slider )
		return b
	
	def _getLabel( self, kargs ) :
		try :
			return kargs[ 'label' ]
		except KeyError : 
			return "Pick up a color"

	def _getDefaultColor( self, kargs ) :
		try :
			return kargs[ 'rgb' ]
		except KeyError : 
			return 0,0,0


class NumericUpDown( BoxLayout ) :
   
	vmin = NumericProperty( None )
	vmax = NumericProperty( None )
	vstep = NumericProperty( 1 )
	value = NumericProperty( 0 )
	txtvalue = ObjectProperty( None )
	btnUp = ObjectProperty( None )
	btnDown = ObjectProperty( None )

	def __init__( self, **kargs ) :
		super( NumericUpDown, self ).__init__( **kargs )
		try :
			self.vmin = kargs[ 'vmin' ]
		except KeyError : pass

		try :
			self.vmax = kargs[ 'vmax' ]
		except KeyError : pass

		try :
			self.vstep = kargs[ 'vstep' ]
		except KeyError : pass

		try :
			self.value = kargs[ 'value' ]
		except KeyError : 
			self.value = self.vmin + ( self.vmax-self.vmin )/2

		self.btnUp.bind( on_press=self._onBtnUpClick )
		self.btnDown.bind( on_press=self._onBtnDownClick )
		self.txtvalue.bind( text=self._onTxtEdit )

	def _onBtnUpClick( self, instance ) :
		if self.vmax is None or ( self.value <= self.vmax-self.vstep  ) :
			self.value += self.vstep

	def _onBtnDownClick( self, instance ) :
		if self.vmin is None or ( self.value >= self.vmin+self.vstep ) :
			self.value -= self.vstep

	def _onTxtEdit( self, instance, value ) :
		try : 
			newv = float( value )
			if ( ( self.vmin is None and self.vmax is None ) or 
				 ( self.vmin <= newv <= self.vmax ) or 
				 ( self.vmin is None and newv <= self.vmax) or 
				 ( self.vmax is None and newv >= self.vmin) ) :
				self.value = newv
		except ValueError : pass

from kivy.lang import Builder
from kivy.properties import ListProperty, NumericProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.widget import Widget

Builder.load_file( "kivyextras.kv" )

class ColorChooser( BoxLayout ) :
 
    sldr = ObjectProperty( None )
    sldg = ObjectProperty( None )
    sldb = ObjectProperty( None )
    label = StringProperty( "Pick up a color :" )

    """
    Arguments : 
        'label' : A simple text to display insted of the default one. Needed.
        'rgb'   : The default rgb value to display. Needed.
    """

    def __init__( self, **kargs ) : 
        super( ColorChooser, self ).__init__( **kargs )
        try :
            self.label = kargs[ 'label' ]
        except KeyError : pass
        try :
            rgb = kargs[ 'rgb' ]
            self.sldr.value_normalized = rgb[0]
            self.sldg.value_normalized = rgb[1]
            self.sldb.value_normalized = rgb[2]
        except KeyError : pass

    def rgb( self ) : 
        return self.sldr.value_normalized, \
               self.sldg.value_normalized, \
               self.sldb.value_normalized


class NumericUpDown( BoxLayout ) :
   
    vmin = NumericProperty( None )
    vmax = NumericProperty( None )
    vstep = NumericProperty( 1 )
    value = NumericProperty( 0 )
    txtvalue = ObjectProperty( None )
    btnUp = ObjectProperty( None )
    btnDown = ObjectProperty( None )

    """
    Arguments : 
        'vmin'  : The min value tha the user can insert. Default is None.
        'vmax'  : The max value tha the user can insert. Default is None.
        'vstep' : The step the click on the up or down button will use. Needed.
        'value' : The default value. Default : vmin + (vmax-vmin )/2
    """

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

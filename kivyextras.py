from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.slider import Slider

class ColorChooser( BoxLayout ) :
   
    def __init__( self, msg, rgba ) : 
        BoxLayout.__init__( self, orientation="vertical" )
        self.add_widget( Label( text = msg ) )
        self.r = Slider( min=0, max=100, value=rgba[0] )
        self.g = Slider( min=0, max=100, value=rgba[1] )
        self.b = Slider( min=0, max=100, value=rgba[2] )
        self.a = Slider( min=0, max=100, value=rgba[3] )

        r = BoxLayout( orientation="horizontal" )
        r.add_widget( Label( text="R : " ) )
        r.add_widget( self.r )
        g = BoxLayout( orientation="horizontal" )
        g.add_widget( Label( text="G : " ) )
        g.add_widget( self.g )
        b = BoxLayout( orientation="horizontal" )
        b.add_widget( Label( text="B : " ) )
        b.add_widget( self.b )
        a = BoxLayout( orientation="horizontal" )
        a.add_widget( Label( text="A: " ) )
        a.add_widget( self.a )

        self.add_widget( r )
        self.add_widget( g )
        self.add_widget( b )
        self.add_widget( a )

    def rgba( self ) : 
        r = self.r.value_normalized
        g = self.g.value_normalized
        b = self.b.value_normalized
        a = self.a.value_normalized
        return r, g, b, a

    def rgb( self ) :
        return self.rgba[:-1]


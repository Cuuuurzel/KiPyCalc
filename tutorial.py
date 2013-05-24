# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.config import Config
import kivy.graphics as kg
from kivy.lang import Builder
from kivy.properties import BooleanProperty, ListProperty, NumericProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget


class HelpPanel( Popup ) :
    
    errorsBefore = BooleanProperty( False )
    wrongExpression = BooleanProperty( False )

    def __init__( self ) :
        t = """[color=ff0000][size=24]Welcome to the help panel![/size][/color]

[size=16]First of all, I want to thank you for downloading my app, 
every single user is important for me, 
feel completely free to contact me for any question, 
issues, or suggestion![/size]

[size=20]Basic Usage[/size]
To be more pragmatic, let's start immediately.
The shift button allows you to change the meaning of the bottons.
All the calculations are made in symbolic mode, 
the evalf buttons give you a value : 
    a = 2 * pi        
    a              prints "2*pi"
    evalf( a )     prints "6.28..."
Declaring a function is also simple :
    f = x**3 * sin(x)
and then write 'f' to refer to the function, for example
    integrate( f, x )
or simply type 'f' and the press plot.

For now, I need time to fix some things, 
I will come with a good guide...
So, this is all, good look!
"""
        cont = BoxLayout( orientation="vertical" )
        cont.add_widget( Label( markup=True, text=t, halign="center" ) )

        Popup.__init__( self, title = 'Welcome to the help panel!', \
                              content = cont, 
                              size_hint = ( 0.95,0.95 ) )

    def open( self ) : 
        #display the popup        
        Popup.open( self )

    def dismiss( self ) :
        Popup.dismiss( self )
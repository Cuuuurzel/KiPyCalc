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
        cont = BoxLayout( orientation="vertical" )
        cont.add_widget( Label( markup=True, text="Welcome to the help panel!" ) )

        Popup.__init__( self, title = 'Plotting Options', \
                              content = cont, 
                              size_hint = ( 0.95,0.95 ) )

    def open( self ) : 
        #display the popup        
        Popup.open( self )

    def dismiss( self ) :
        Popup.dismiss( self )

# -*- coding: utf-8 -*-

from code import InteractiveConsole
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from sympy import *
from sympy.abc import *
from sympy.utilities.lambdify import lambdify
import sys

from keyboard import *

DEBUG = True
FONT_NAME = "res/font/tt/unispace rg.ttf"
FONT_SIZE = 16

class PyShell( BoxLayout ) :

    def __init__( self, plotFoo ) :
        self.console = InteractiveConsole()
        BoxLayout.__init__( self, orientation="vertical" )
        frm = BoxLayout( orientation="vertical" )
        self.listed = TextInput()
        self.listed.font_name = FONT_NAME
        self.listed.readonly = True
        self.listed.size_hint = 1, 0.2
        self.listed.font_size = FONT_SIZE
        frm.add_widget( self.listed )
        self.kb = KiPyKeyboard( self.onBtnExecPress, plotFoo )
        self.kb.size_hint = 1, 0.8
        frm.add_widget( self.kb )
        frm.size_hint = 1,1
        self.add_widget( frm )

    def start( self ) : 
        if not DEBUG :
            sys.stdout = self
            sys.stderr = self
        self.loadBuiltins()

    def loadBuiltins( self ) :
        self.console.push( "from math import *\n" )
        self.console.push( "from sympy import *\n" )
        self.console.push( "from sympy.abc import *\n" )

    def write( self, sometext ) :
        self.listed.text += sometext
   
    def inputOk( self, someInputString ) :
        print( "in: " + someInputString )
        if "integrate" in someInputString : 
            print( "This may take long... please wait." )
        return True

    def onBtnExecPress( self, instance ) :
        command = self.kb.current.text
        if self.inputOk( command ) :
            if self.console.push( command ) :
                print( "#More input required" )
            else : 
                self.kb.flush() 

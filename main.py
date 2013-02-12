# -*- coding: utf-8 -*-

from code import compile_command, InteractiveConsole
import sys
import kivy
from kivy.app import App
from kivy.config import Config
from kivy.lang import Builder
from kivy.properties import *
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

kivy.require( '1.1.2' )
Builder.load_file( "kipycalc.kv" )

class PyShell( BoxLayout ) :

    def __init__( self ) :
        self.console = InteractiveConsole()
        BoxLayout.__init__( self, orientation="vertical" )
        self.listed = TextInput()
        self.listed.font_name = "font/ubuntu-mono/UbuntuMono-R.ttf"
        self.listed.readonly = True
        self.listed.size_hint = 1, 0.2
        self.add_widget( self.listed )
        self.kb = CucuKeyboard( self.onBtnExecPress )
        self.kb.size_hint = 1, 0.8
        self.add_widget( self.kb )

    def start( self ) : 
        oldStdout = sys.stdout
        sys.stdout = self
        oldStderr = sys.stderr
        sys.stderr = self
        self.loadBuiltins()

    def loadBuiltins( self ) :
        self.feedInterpreter( "from math import *\n" )
        self.feedInterpreter( "from sympy import *\n" )
        self.feedInterpreter( "from sympy.abc import *\n" )
 
    def feedInterpreter( self, someinput ) :
        self.console.push( someinput )

    def write( self, sometext ) :
        self.listed.text += sometext

    def onBtnExecPress( self, instance ) :
        command = self.kb.current.text
        print( "in: " + command )
        if self.console.push( command ) :
            print( "#More input required" )
        else : 
            self.kb.flush() 


class CucuKeyboard( BoxLayout ) :
    
    def __init__( self, handlerfoo ) :
        BoxLayout.__init__( self, orientation="vertical" )
        self.padding = 1 
        inp = BoxLayout( orientation="horizontal" )
        inp.padding = 1
        self.current = TextInput()
        self.current.font_name = "font/ubuntu-mono/UbuntuMono-R.ttf"
        self.current.size_hint = 0.85, 1
        inp.add_widget( self.current )
        btnExec = Button( text="Exec()" )
        btnExec.bind( on_press=handlerfoo )
        btnExec.size_hint = 0.15, 1
        inp.add_widget( btnExec )
        inp.size_hint = 1, 0.25
        self.add_widget( inp )

        self.textnav = BoxLayout( orientation="vertical" )
        self.numpad = GridLayout( cols=4 )
        self.operators = GridLayout( cols=3 )
        self.symbols = GridLayout( cols=5 )
        self.functions = GridLayout( cols=5 )

        self.textnav.padding = 1
        self.numpad.padding = 1
        self.functions.padding = 1
        self.operators.padding = 1
        self.symbols.padding = 1

        rows = 10.0
        self.textnav.size_hint = 0.15, 1 
        self.numpad.size_hint = 1, 3/rows
        self.functions.size_hint = 1, 1/rows
        self.operators.size_hint = 1, 4/rows
        self.symbols.size_hint = 1, 2./rows

        self.keys = { "textnav" :   { 0 : "^ <- -> var def del \\n \\t".split( " " ),
                                      1 : "^ <- -> var def del \\n \\t".split( " " ),
                                      2 : "^ <- -> var def del \\n \\t".split( " " ) },

                      "numpad" :    { 0 : list( "1234567890.I" ),
                                      1 : list( "1234567890.I" ),
                                      2 : list( "1234567890.I" ) }, 

                      "symbols" :   { 0 : list( "xyztwTskE" ) + [ u"∏" ],
                                      1 : list( "abcdfghlov" ),
                                      2 : list( "ABpnumKMGP" ) }, 

                      "operators" : { 0 : "ANS , evalf + - * / **".split( " " ) + [ u"√" ] + "( ) =".split( " " ),
                                      1 : "ANS , evalf + - * / **".split( " " ) + [ u"√" ] + "( ) =".split( " " ),
                                      2 : "ANS , evalf + - * / **".split( " " ) + [ u"√" ] + "( ) =".split( " " ) },

                      "functions" : { 0 : "cos sin tan Log".split( " " ) + [ u"Δx/Δy" ],
                                      1 : "aCos aSin aTan aTan2".split( " " ) + [ u"∫" ],
                                      2 : [ "subs units of measure" ] }
                    }

        self.kb = BoxLayout( orientation="horizontal" )
        tkb = BoxLayout( orientation="vertical" )
        tkb.add_widget( self.operators )
        tkb.add_widget( self.numpad )
        tkb.add_widget( self.symbols )
        tkb.add_widget( self.functions )
        self.kb.add_widget( tkb )
        self.kb.add_widget( self.textnav )
        self.add_widget( self.kb )
        self.shiftCount = -1
        self.onShift()

    def onShift( self ) :
        self.shiftCount += 1
        if self.shiftCount == 3 : self.shiftCount = 0

        self.functions.clear_widgets()
        self.numpad.clear_widgets()
        self.symbols.clear_widgets()
        self.operators.clear_widgets()
        self.textnav.clear_widgets()

        for key in self.keys["numpad"][self.shiftCount] :
            btn = Button( text=key )
            btn.bind( on_press=self.onBtnPress ) 
            self.numpad.add_widget( btn )

        for key in self.keys["symbols"][self.shiftCount] :
            btn = Button( text=key )
            btn.bind( on_press=self.onBtnPress ) 
            self.symbols.add_widget( btn )

        for key in self.keys["operators"][self.shiftCount] :
            btn = Button( text=key )
            btn.bind( on_press=self.onBtnPress ) 
            self.operators.add_widget( btn )

        for key in self.keys["functions"][self.shiftCount] :
            btn = Button( text=key )
            btn.bind( on_press=self.onBtnPress ) 
            self.functions.add_widget( btn )

        for key in self.keys["textnav"][self.shiftCount] :
            btn = Button( text=key )
            btn.bind( on_press=self.onBtnPress ) 
            self.textnav.add_widget( btn )
 
    def onBtnPress( self, instance ) :
        command = instance.text

        if   command == u"√" : 
            self.current.text += "sqrt("
        elif command == u"∫" : 
            self.current.text += ".integrate( x )"
        elif command == u"Δx/Δy" : 
            self.current.text += ".diff( x )"
        elif command == "cos" : 
            self.current.text += "cos("
        elif command == "aCos" : 
            self.current.text += "acos("
        elif command == "sin" : 
            self.current.text += "sin("
        elif command == "aSin" : 
            self.current.text += "asin("
        elif command == "tan" : 
            self.current.text += "tan("
        elif command == "aTan" : 
            self.current.text += "atan("
        elif command == "aTan2" : 
            self.current.text += "atan2("
        elif command == "Log" : 
            self.current.text += "log( x, b )"
        elif command == "evalf" : 
            self.current.text += ".evalf()"
        elif command == u"∏" : 
            self.current.text += "pi"
        elif command == "e" : 
            self.current.text += "E"
        elif command == "^" : 
            self.onShift()
        elif   command == "\\n" : 
            self.current.text += "\n"
        elif command == "\\t" :
            self.current.text += "    "
        elif command == "del" :
            if len( self.current.text ) > 0 :
                self.current.text = self.current.text[:-1]
        elif command == "subs units of measure" :
            self.current.text += ".subs( { p:10**(-12), n:10**(-9), u:10**(-6), m:10**(-3), K:10**3, M:10**6, G:10**9, P:10**12 } )"
#!!!
        elif command == "<-" : 
            print( "Not yet implemented" )
        elif command == "->" : 
            print( "Not yet implemented" )
        elif command == "var" : 
            print( "Not yet implemented" )
        elif command == "def" : 
            print( "Not yet implemented" )
        elif command == "ANS" : 
            print( "Not yet implemented" )
#!!!
        #all the rest...
        else : 
            self.current.text += command

    def flush( self ) : 
        self.current.text = ""
    

class KiPyCalcApp( App ) : 

    def build( self ) :
        frm = BoxLayout( orientation="vertical" )
        shell = PyShell()
        shell.start()
        frm.add_widget( shell )
        return frm


if __name__ in [ "__android__", "__main__" ] :
    KiPyCalcApp().run()

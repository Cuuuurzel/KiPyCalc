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
Config.set( 'graphics', 'height', '800' )
Config.set( 'graphics', 'width', '480' )
Builder.load_file( "kipycalc.kv" )


class PyShell( BoxLayout ) :

    def __init__( self ) :
        self.console = InteractiveConsole()
        BoxLayout.__init__( self, orientation="vertical" )
        self.listed = TextInput()
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

        inp = BoxLayout( orientation="horizontal" )
        self.current = TextInput()
        self.current.size_hint = 0.85, 1
        inp.add_widget( self.current )
        btnExec = Button( text="Exec()" )
        btnExec.bind( on_press=handlerfoo )
        btnExec.size_hint = 0.15, 1
        inp.add_widget( btnExec )
        inp.size_hint = 1, 0.25
        self.add_widget( inp )

        self.textnav = BoxLayout( orientation="vertical" )
        self.textnav.size_hint = 0.15, 1

        self.numpad = GridLayout( cols=2 )
        self.numpad.size_hint = 0.3, 1

        self.operators = GridLayout( cols=3 )
        self.symbols = GridLayout( cols=4 )
        self.functions = GridLayout( cols=3 )

        self.textnav.padding = 1
        self.numpad.padding = 1
        self.symbols.padding = 1
        self.operators.padding = 1
        self.functions.padding = 1

        self.keys = { "textnav" :   { 0:[ "^", "<-", "->", "var", "def", "del", "\\n", "\\t"  ],
                                      1:[ "^", "<-", "->", "var", "def", "del", "\\n", "\\t"  ],
                                      2:[ "^", "<-", "->", "var", "def", "del", "\\n", "\\t"  ] },

                      "numpad" :    { 0:[ "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", ".", "I" ],
                                      1:[ "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", ".", "I" ],
                                      2:[ "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", ".", "I" ] }, 

                      "operators" : { 0:[ "+", "-", "*", "/", "**", u"√", "(", ")", "=" ],
                                      1:[ "+", "-", "*", "/", "**", u"√", "(", ")", "=" ],
                                      2:[ "+", "-", "*", "/", "**", u"√", "(", ")", "=" ] },

                      "symbols" :   { 0:[ "x", "y", "z", "t", "T", "w", "a", "oo", "k", "e", u"∏", "evalf" ],
                                      1:[ "f", "g", "h", "l", "m", "n", "o", "q", "r", "s", "a", "v" ],
                                      2:[ "u", "b", "A", "B", "C", "D", "S" ] }, 

                      "functions" : { 0:[ "cos", "aCos", "sin", "aSin", "tan", "aTan", "aTan2", u"∫", "Log" ], 
                                      1:[ "cos", "aCos", "sin", "aSin", "tan", "aTan", "aTan2", u"∫", "Log" ], 
                                      2:[ "cos", "aCos", "sin", "aSin", "tan", "aTan", "aTan2", u"∫", "Log" ] }
                    }

        self.kb = BoxLayout( orientation="horizontal" )
        tkb = BoxLayout( orientation="vertical" )
        tkb.add_widget( self.operators )
        tkb.add_widget( self.symbols )
        tkb.add_widget( self.functions )

        tkb.size_hint = 0.55, 1
        self.kb.add_widget( self.numpad )
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

        #"operators" block
        if   command == u"√" : 
            self.current.text += "sqrt("
        #"functions" block
        elif command == u"∫" : 
            self.current.text += "integrate("
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
        #"variables" block
        elif command == "evalf" : 
            self.current.text += ".evalf()"
        elif command == u"∏" : 
            self.current.text += "pi"
        elif command == "e" : 
            self.current.text += "E"
        #"textnav" block
#!!!
        elif command == "<-" : 
            pass
        elif command == "->" : 
            pass
        elif command == "var" : 
            pass
        elif command == "def" : 
            pass
#!!!
        elif command == "^" : 
            self.onShift()
        elif   command == "\\n" : 
            self.current.text += "\n"
        elif command == "\\t" :
            self.current.text += "    "
        elif command == "del" :
            if len( self.current.text ) > 0 :
                self.current.text = self.current.text[:-1]
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

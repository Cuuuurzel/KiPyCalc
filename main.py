# -*- coding: utf-8 -*-

from code import InteractiveConsole
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

Builder.load_file( "kipycalc.kv" )

class PyShell( BoxLayout ) :

    def __init__( self ) :
        self.console = InteractiveConsole()
        BoxLayout.__init__( self, orientation="vertical" )
        self.listed = TextInput()
        self.listed.font_name = "font/ubuntu-mono/UbuntuMono-R.ttf"
        self.listed.readonly = True
        self.listed.size_hint = 1, 0.2
        self.listed.font_size = 18
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
        self.current.font_size = 18
        self.current.size_hint = 0.85, 1
        inp.add_widget( self.current )
        btnExec = Button( text="Exec()" )
        btnExec.bind( on_press=handlerfoo )
        btnExec.size_hint = 0.15, 1
        btnExec.font_size = 18
        inp.add_widget( btnExec )
        inp.size_hint = 1, 0.25
        self.add_widget( inp )

        """
        self.textbar = GridLayout( cols=5 )
        self.parbar = GridLayout( cols=5 )
        self.numpad = GridLayout( cols=5 )
        self.operators = GridLayout( cols=5 )
        self.functions = GridLayout( cols=5 )

        self.textbar.padding = 1
        self.parbar.padding = 1
        self.numpad.padding = 1
        self.functions.padding = 1
        self.operators.padding = 1
        
        r = 9.0
        self.textbar.size_hint = 1, 1/r 
        self.parbar.size_hint = 1, 1/r 
        self.numpad.size_hint = 1, 2/r
        self.functions.size_hint = 1, 1/r
        self.operators.size_hint = 1, 2/r
        """

        self.keys = { "textnav" :   { "<-"  : [ "<-", "<-", "<-" ], \
                                      "->"  : [ "->", "->", "->" ] },

                      "textedit" :  { "del" : [ "del", "del", "del" ], \
                                      "_"   : [ "_", "_", "_" ], \
                                      "\\n" : [ "\\n", "\\n", "\\n" ], \
                                      "\\t" : [ "\\t", "\\t", "\\t" ] },

                      "parbar" :    { "(" : [ "(", "(", "(" ], \
                                      ")" : [ ")", ")", ")" ], \
                                      "[" : [ "[", "[", "[" ], \
                                      "]" : [ "]", "]", "]" ], \
                                      "{" : [ "{", "{", "{" ], \
                                      "}" : [ "}", "}", "}" ], \
                                      "," : [ ",", ",", "," ] },

                      "numpad" :    { "1"  : [ "1", "1", "1" ], \
                                      "2"  : [ "2", "2", "2" ], \
                                      "3"  : [ "3", "3", "3" ], \
                                      "4"  : [ "4", "4", "4" ], \
                                      "5"  : [ "5", "5", "5" ], \
                                      "6"  : [ "6", "6", "6" ], \
                                      "7"  : [ "7", "7", "7" ], \
                                      "8"  : [ "8", "8", "8" ], \
                                      "9"  : [ "9", "9", "9" ], \
                                      "0"  : [ "0", "0", "0" ], \
                                      "."  : [ ".", ".", "." ] },

                      "consts" :    { "I"  : [ "I", "I", "I" ], \
                                      "E"  : [ "E", "E", "E" ], \
                                      u"∏" : [ u"∏", u"∏", u"∏" ] },

                      "operators" : { "ANS"   : [ "ANS", "ANS", "ANS" ], \
                                      "evalf" : [ "evalf", "evalf", "evalf" ], \
                                      "="     : [ "=", "=", "=" ], \
                                      "+"     : [ "+", "+", "+" ], \
                                      "-"     : [ "-", "-", "-" ], \
                                      "*"     : [ "*", "*", "*" ], \
                                      "/"     : [ "/", "/", "/" ], \
                                      "**"    : [ "**", "**", "**" ], \
                                      u"√"    : [ u"√", u"√", u"√" ] },

                      "functions" : { "^"      : [ "^", "^", "^" ], \
                                      "subs"   : [ "subs", "subs", "subs" ], \
                                      "cos"    : [ "cos", "aCos", ""], \
                                      "sin"    : [ "sin", "aSin", "sinc" ], \
                                      "tan"    : [ "tan", "aTan", "aTan2" ], \
                                      "ln"     : [ "ln", "E**", "" ], \
                                      "log"    : [ "log", "10**", "" ], \
                                      u"Δx/Δy" : [ u"Δx/Δy", u"∫", "" ] }

                    }

        #self.kb = BoxLayout( orientation="vertical" )
        self.kb = GridLayout( cols=6 )
        self.kb.padding = 1
        self.add_widget( self.kb )
        self.shiftCount = -1
        self.onShift()

    def onShift( self ) :
        self.shiftCount += 1
        if self.shiftCount == 3 : self.shiftCount = 0

        for key in self.keys.keys() :
            keySet = self.keys[ key ]
            for keyName in keySet.keys() :
                caption = keySet[ keyName ][ self.shiftCount ]
                btn = Button( text=caption )
                btn.bind( on_press=self.onBtnPress ) 
                btn.font_size = 18
                self.kb.add_widget( btn )  
  
    def onBtnPress( self, instance ) :
        command = instance.text
        toInsert = ""

        if   command == u"√" :     toInsert = "sqrt("
        elif command == u"∫" :     toInsert = ".integrate( x )"
        elif command == u"Δx/Δy" : toInsert = ".diff( x )"
        elif command == "cos" :    toInsert = "cos("
        elif command == "aCos" :   toInsert = "acos("
        elif command == "sin" :    toInsert = "sin("
        elif command == "aSin" :   toInsert = "asin("
        elif command == "tan" :    toInsert = "tan("
        elif command == "aTan" :   toInsert = "atan("
        elif command == "aTan2" :  toInsert = "atan2("
        elif command == "Log" :    toInsert = "log( x, b )"
        elif command == "evalf" :  toInsert = ".evalf()"
        elif command == u"∏" :     toInsert = "pi"
        elif command == "E**" :    toInsert = "E**("
        elif command == "10**" :   toInsert = "10**("
        elif command == "_" :   toInsert = " "
        elif command == "^" :      self.onShift()
        elif command == "\\n" :    toInsert = "\n"
        elif command == "\\t" :    toInsert = "    "
        elif command == "<-" :     self.current.do_cursor_movement( 'cursor_left' )
        elif command == "->" :     self.current.do_cursor_movement( 'cursor_right' )
        elif command == "del" :    self.deleteChar()
        elif command == "subs" : toInsert = ".subs( { p:10**(-12), n:10**(-9), u:10**(-6), m:10**(-3), K:10**3, M:10**6, G:10**9, P:10**12 } )"
        #all the rest...
        else : 
            toInsert = command

        self.current.text += toInsert 


    def deleteChar( self ) : 
        print( "Not yet implemented" )

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

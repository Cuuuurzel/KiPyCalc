# -*- coding: utf-8 -*-

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

FONT_NAME = "res/font/tt/unispace rg.ttf"
FONT_SIZE = 20

def loadButtonsFromString( someWidget, names, onPress ) :
    for name in names : 
        btn = Button( text=name )
        btn.bind( on_press=onPress )
        btn.font_name = FONT_NAME
        btn.font_size = FONT_SIZE
        someWidget.add_widget( btn )


class KiPyKeyboard( BoxLayout ) :
    
    def __init__( self, handlerfoo, plotfoo ) :
        BoxLayout.__init__( self, orientation="vertical" )
        inp = BoxLayout( orientation="horizontal" )
        inp.padding = 1
        self.current = TextInput( text=u"" )
        self.current.font_name = FONT_NAME
        self.current.font_size = FONT_SIZE
        self.current.size_hint = 0.85, 1

        inp.add_widget( self.current )
        btnExec = Button( text="Exec()" )
        btnExec.font_name = FONT_NAME
        btnExec.font_size = FONT_SIZE
        btnExec.bind( on_press=handlerfoo )
        btnPlot = Button( text="Plot!" )
        btnPlot.font_name = FONT_NAME
        btnPlot.font_size = FONT_SIZE
        btnPlot.bind( on_press=plotfoo )
        b = BoxLayout( orientation="vertical" )
        b.add_widget( btnExec )
        b.add_widget( btnPlot )
        b.size_hint = 0.25, 1
        inp.add_widget( b )
        
        self.static_keys = BoxLayout( orientation="vertical" )
        self.loadStaticKeys()

        self.numpad = GridLayout( cols=4 )
        self.loadNumpad()
        self.numpad.size_hint = 0.6, 1

        self.symbols = GridLayout( cols=4 )
        self.loadSymbols()
        self.symbols.size_hint = 0.6, 1
         
        self.foo1 = GridLayout( cols=2 )
        self.loadFoo1()
        self.foo1.size_hint = 0.4, 1

        self.foo2 = GridLayout( cols=2 )
        self.loadFoo2()
        self.foo2.size_hint = 0.4, 1

        self.unitOfMeasure = GridLayout( cols=2 )
        self.loadUnitOfMeasure()
        self.unitOfMeasure.size_hint = 0.4, 1

        self.kb = BoxLayout( orientation="horizontal" )
        self.kb.size_hit = 1, 0.33
        self.static_keys.size_hit = 1, 0.33
        inp.size_hint = 1, 0.6
        self.add_widget( inp )
        self.add_widget( self.static_keys )
        self.add_widget( self.kb )
        self.shiftCount = -1
        self.onShift()

    def loadStaticKeys( self ) :
        k1 = "<- space tab \\n ->".split( " " )
        k2 = "{ [ ( , ) ] }".split( " " )
        k3 = "evalf print undo clear shift".split( " " )
        k4 = "+ - * / ** =".split( " " ) + [ u"√" ]
        default_keys = ( k1, k2, k3, k4 )

        for keySet in default_keys :
            k = BoxLayout( orientation="horizontal" )
            loadButtonsFromString( k, keySet, self.onBtnPress )
            self.static_keys.add_widget( k )

    def loadNumpad( self ) :
        keySet = "1 2 3 4 5 6 7 8 9 0 . I E".split( " " ) + [ u"π", "10**", "E**" ] 
        loadButtonsFromString( self.numpad, keySet, self.onBtnPress )

    def loadSymbols( self ) :
        keySet = "x y z t T w a b c d f g k . I E".split( " " ) 
        loadButtonsFromString( self.symbols, keySet, self.onBtnPress )

    def loadFoo1( self ) :
        keySet = "cos sin tan Ln Log diff".split( " " )
        loadButtonsFromString( self.foo1, keySet, self.onBtnPress )

    def loadFoo2( self ) :
        keySet = "aCos aSin aTan aTan2 Lim".split( " " ) + [ u"∫" ]
        loadButtonsFromString( self.foo2, keySet, self.onBtnPress )

    def loadUnitOfMeasure( self ) :
        keySet = "p n u m K M G P".split( " " )
        loadButtonsFromString( self.unitOfMeasure, keySet, self.onBtnPress )

    def onShift( self ) :
        self.shiftCount += 1
        if self.shiftCount == 3 : self.shiftCount = 0 
        self.kb.clear_widgets()

        if self.shiftCount == 0 : 
            self.kb.add_widget( self.foo1 )
            self.kb.add_widget( self.numpad )
        elif self.shiftCount == 1 : 
            self.kb.add_widget( self.foo2 )
            self.kb.add_widget( self.symbols )
        elif self.shiftCount == 2 : 
            self.kb.add_widget( self.unitOfMeasure )
            self.kb.add_widget( self.numpad )

    def onBtnPress( self, instance ) :
        command = instance.text
        toInsert = ""

        if   command == u"√" :    toInsert = "sqrt("
        elif command == u"∫" :    toInsert = "integrate( f, x )"
        elif command == "diff" :  toInsert = "diff( f, x )"
        elif command == "cos" :   toInsert = "cos("
        elif command == "aCos" :  toInsert = "acos("
        elif command == "sin" :   toInsert = "sin("
        elif command == "aSin" :  toInsert = "asin("
        elif command == "tan" :   toInsert = "tan("
        elif command == "aTan" :  toInsert = "atan("
        elif command == "aTan2" : toInsert = "atan2("
        elif command == "coTan" : toInsert = "cot("
        elif command == "Lim" : toInsert = "limit( f, x, xl )"
        elif command == "Log" :   toInsert = "log( x, 10 )"
        elif command == "Ln" :   toInsert = "ln( x, E )"
        elif command == "evalf" : toInsert = "evalf("
        elif command == u"π" :    toInsert = "pi"
        elif command == "clear" : self.current.text = u""
        elif command == "space" : toInsert = " "
        elif command == "ans" :   toInsert = "ANS"
        elif command == "shift" : self.onShift()
        elif command == "\\n" :   toInsert = "\n"
        elif command == "tab" :   toInsert = "    "
        elif command == "\\t" :   toInsert = "    "
        elif command == "print" : toInsert = "pprint( "
        elif command == "<-" :    self.current.do_cursor_movement( 'cursor_left' )
        elif command == "->" :    self.current.do_cursor_movement( 'cursor_right' )
        elif command == "undo" :  self.current.do_undo()
        elif command == "subs" :  toInsert = ".subs( { p:10**(-12), n:10**(-9), u:10**(-6), m:10**(-3), K:10**3, M:10**6, G:10**9, P:10**12 } )"
        #all the rest...
        else : 
            toInsert = command
        self.current.insert_text( toInsert )

    def flush( self ) : 
        self.current.text = ""

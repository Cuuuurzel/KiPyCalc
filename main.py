# -*- coding: utf-8 -*-

from code import InteractiveConsole
from kivy.app import App
from kivy.base import EventLoop
from kivy.clock import Clock
from kivy.graphics import *
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from sympy import *
from sympy.abc import *
from sympy.utilities.lambdify import lambdify
import sys


FONT_NAME = "res/font/ubuntu-mono/UbuntuMono-R.ttf"
FONT_SIZE = 24

Builder.load_file( "kipycalc.kv" )



class CucuKeyboard( BoxLayout ) :
    
    def __init__( self, handlerfoo, plotfoo ) :
        BoxLayout.__init__( self, orientation="vertical" )
        inp = BoxLayout( orientation="horizontal" )
        inp.padding = 1
        self.current = TextInput()
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
        k3 = "evalf print undo about shift".split( " " )
        k4 = "+ - * / ** =".split( " " ) + [ u"√" ]
        default_keys = ( k1, k2, k3, k4 )

        for keySet in default_keys :
            k = BoxLayout( orientation="horizontal" )
            loadButtonsFromString( k, keySet, self.onBtnPress )
            self.static_keys.add_widget( k )

    def loadNumpad( self ) :
        keySet = "1 2 3 4 5 6 7 8 9 0 . I E".split( " " ) + [ u"π", "10**", "E**" ] 
        loadButtonsFromString( self.numpad, keySet, self.onBtnPress )

    def loadFoo1( self ) :
        keySet = "cos sin tan ln log diff".split( " " )
        loadButtonsFromString( self.foo1, keySet, self.onBtnPress )

    def loadFoo2( self ) :
        keySet = "aCos aSin aTan aTan2 coTan".split( " " ) + [ u"∫" ]
        loadButtonsFromString( self.foo2, keySet, self.onBtnPress )

    def loadUnitOfMeasure( self ) :
        keySet = "p n u m K M G P".split( " " )
        loadButtonsFromString( self.unitOfMeasure, keySet, self.onBtnPress )

    def onShift( self ) :
        self.shiftCount += 1
        if self.shiftCount == 3 : self.shiftCount = 0 
        self.kb.clear_widgets()
        self.kb.add_widget( self.numpad )
        if  self.shiftCount == 0 : 
            self.kb.add_widget( self.foo1 )
        elif self.shiftCount == 1 : 
            self.kb.add_widget( self.foo2 )
        elif self.shiftCount == 2 : 
            self.kb.add_widget( self.unitOfMeasure )

    def onBtnPress( self, instance ) :
        command = instance.text
        toInsert = ""

        if   command == u"√" :    toInsert = "sqrt("
        elif command == u"∫" :    toInsert = ".integrate( x )"
        elif command == "diff" :  toInsert = ".diff( x )"
        elif command == "cos" :   toInsert = "cos("
        elif command == "aCos" :  toInsert = "acos("
        elif command == "sin" :   toInsert = "sin("
        elif command == "aSin" :  toInsert = "asin("
        elif command == "tan" :   toInsert = "tan("
        elif command == "aTan" :  toInsert = "atan("
        elif command == "aTan2" : toInsert = "atan2("
        elif command == "coTan" : toInsert = "cot("
        elif command == "Log" :   toInsert = "log( x, b )"
        elif command == "evalf" : toInsert = ".evalf()"
        elif command == u"π" :    toInsert = "pi"
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
        

class Plotter( Widget ) :
    points = ListProperty()

    def __init__( self, foo, center, xRange, scale ) : 
        Widget.__init__( self )
        self.foo = lambdify( x, foo ) 
        self.xRange = xRange
        self.scale = scale
        self.center = center
        self.step = self.goodStep()
        self.points = self.evalPoints()

    def goodStep( self ) :
        dx = abs( self.xRange[0] - self.xRange[1] )
        w = Config.get( 'graphics', 'width' )
        return 1 

    def evalPoints( self ) :
        points = []
        x = self.xRange[0]
        while x < self.xRange[1] : 
            y = self.foo( x )
            points.append( x*self.scale[0] + self.center[0] )
            points.append( y*self.scale[1] + self.center[1] )
            x += self.step
        return points


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
        self.kb = CucuKeyboard( self.onBtnExecPress, plotFoo )
        self.kb.size_hint = 1, 0.8
        frm.add_widget( self.kb )
        frm.size_hint = 1,1
        self.add_widget( frm )

    def start( self ) : 
        oldStdout = sys.stdout
        sys.stdout = self
        oldStderr = sys.stderr
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
        if someInputString.find( "integrate" ) != -1 : 
            print( "This may take long... please wait" )
        return True

    def onBtnExecPress( self, instance ) :
        command = self.kb.current.text
        if self.inputOk( command ) :
            if self.console.push( command ) :
                print( "#More input required" )
            else : 
                self.kb.flush() 


def loadButtonsFromString( someWidget, names, onPress ) :
    for name in names : 
        btn = Button( text=name )
        btn.bind( on_press=onPress )
        btn.font_name = FONT_NAME
        btn.font_size = FONT_SIZE
        someWidget.add_widget( btn )


class KiPyCalc( PyShell ) :

    def __init__( self, **kwargs ) :
        PyShell.__init__( self, self.onBtnPlotPress )
        self.plotterMode = False
        with self.canvas:
            Callback( self.draw )
        Clock.schedule_interval( self.ask_update, 1/60. )

    def draw( self, t ) :
        if self.plotterMode : 
            #draw as Plotter
            pass                   

    def ask_update( self, *args ) :
        self.canvas.ask_update()

    def onBtnPlotPress( self, instance ) : 
        self.plotterMode = True
        print( "Plot Mode On..." )

    def onReturnKey( self ) :
        if self.plotterMode :
            self.plotterMode = False
            print( "Plot Mode Off..." )


class KiPyCalcApp( App ) : 

    icon = 'res/icon.png'
    title = 'KiPyCalc'
    
    def build( self ) :
        self.kpc = KiPyCalc()
        self.kpc.start()
        EventLoop.window.bind( on_keyboard=self.hook_keyboard )
        return self.kpc

    def hook_keyboard( self, window, key, *largs ):
        if key == 27 :
            self.kpc.onReturnKey() 
            return True 

if __name__ in [ "__android__", "__main__" ] :
    KiPyCalcApp().run()

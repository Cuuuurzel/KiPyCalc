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

FONT_NAME = "res/ubuntu-font-family-0.80/UbuntuMono-R.ttf"
FONT_SIZE = 18

class PyShell( BoxLayout ) :

	def __init__( self, plotFoo ) :
		self._lastOutput = []
		self.console = InteractiveConsole()

		BoxLayout.__init__( self, orientation="vertical" )
		frm = BoxLayout( orientation="vertical" )
		self.listed = TextInput()
		self.listed.font_name = FONT_NAME
		self.listed.readonly = True
		self.listed.size_hint = 1, 0.3
		self.listed.font_size = FONT_SIZE

		frm.add_widget( self.listed )
		self.kb = KiPyKeyboard( self.onBtnExecPress, plotFoo )
		self.kb.size_hint = 1, 0.7
		frm.add_widget( self.kb )
		frm.size_hint = 1,1
		self.add_widget( frm )

	def start( self ) :
		sys.stdout = self
		sys.stderr = self
		self.shellInit()

	def shellInit( self ) :
		initCode = open( "res/SHELL_INIT" ).read()
		for line in initCode.split("\n") :
			self.console.push( line )

	def write( self, sometext ) :
		self._lastOutput.append( sometext )
		self.listed.text += sometext

	def correctInput( self, stat ) :
		if stat == "\n" : stat = "ans\n"
		print( "in : " + stat[:-1] )

		if stat.upper() in ( "ANS\n", "ANS" ) :
			return "print( ans )", False
		
		keys = [ "DEF", "FOR", "WHILE", "IMPORT", "EXEC" ]
		for key in keys : 
			if key in stat.upper() : 
				return stat, False
		return "ans = " + stat, True
			

	def onBtnExecPress( self, instance ) :
		stat = self.kb.current.text + "\n"
		stat, printANS = self.correctInput( stat )

		#Save current ANS.
		if printANS : self.console.push( "last_ANS = ans\n" )
		#Execute statement.
		moreInputNeeded = self.console.push( stat )
		#Check for multiline instructions.
		if moreInputNeeded :
			print( "#Multiline instructions must be entered in one fell swoop!" )
			self.console.push( "\n" )
		#The input was ok.
		else :
			#If ANS is None, restore last_ANS.
			self.console.push( "if ans is None : ans = last_ANS\n" ) 
			#Print ANS, flush input buffer.			
			if printANS : self.console.push( "print( ans )\n" )
			self.kb.flush() 















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

DEBUG = False
FONT_NAME = "res/ubuntu-font-family-0.80/Ubuntu-L.ttf"
FONT_SIZE = 16

class WrappedString() :
	def __init__( self, s="", **kargs ) :
		self.s = s

	def write( self, someText ) :
		self.s += someText

	def contains( self, someText ) :
		return someText in self.s

	def __str__( self ) :
		return self.s

class PyShell( BoxLayout ) :

	def __init__( self, plotFoo ) :
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
		if not DEBUG :
			sys.stdout = self
			sys.stderr = self
		self.shellInit()

	def shellInit( self ) :
		initCode = """
from math import *
from sympy import *
from sympy.abc import *
from __future__ import division
ans = 0
print( "#Type 'ans' to refer to the last result." )
print( "#Keep in mind that numeric values differs a lot from symbolic one." )
def evalf() : 
	try :
		return ans.evalf()
	except AttributeError : 
		return ans
"""

		for line in initCode.split("\n") :
			self.console.push( line )

	def write( self, sometext ) :
		self.listed.text += sometext

	"""
	Add input check here!
	"""
	def inputCheck( self, stat ) :
		print( "in: " + stat )
		return stat

	def onBtnExecPress( self, instance ) :
		stat = self.inputCheck( self.kb.current.text ) #missing \n?
		if self.console.push( "ans = " + stat ) :
			print( "#Multiline instructions must be entered in one fell swoop" )
		self.console.push( "ans" )
		self.kb.flush() 















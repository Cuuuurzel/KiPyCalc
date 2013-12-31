class History() : 

	def __init__( self ) :
		self.inputs = []
		self.inputs_strings = []
		self.outputs = []
		self.outputs_strings = []

	def putInput( self, newInput, strInput ) :
		inputs.append( newInput )
		inputs_strings.append( strInput )

	def putOutput( self, newOutput, strOutput) :
		outputs.append( newOutput )
		outputs_strings.append( strOutput )
		pass

	def getHtml( self ) :
		s = "<html>\n\t<body>"
		div = '<div class="kipyInput">'
		for i in range( 0, len( self.inputs_strings ) ) :
			s += div + self.inputs_strings[i] + "<div>\n"
			s += div + self.outputs_strings[i] + "<div>"

	def getInput( self, i=-1 ) :
		return self.inputs[ i ]

	def getInputStr( self, i=-1 ) :
		return self.inputs_strings[ i ]

	def getOutput( self, i=-1 ) :
		return self.outputs[ i ]

	def getOutputStr( self, i=-1 ) :
		return self.outputs_strings[ i ]



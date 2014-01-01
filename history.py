class History() : 

	INPUT = 0
	OUTPUT = 1
	KIPY_MSG = 2
	PLOT_PATH = 3

	def __init__( self ) :
		self.h = []

	def put( self, kind, newInput ) :
		self.h.append( [ kind, str( newInput ) ] )

	def getHtml( self ) :
		s = """<html>
	<style media="screen" type="text/css">
		.kipyINPUT  { text-align:left   } 
		.kipyOUTPUT { text-align:center  } 
		.kipyMSG    { text-align:center } 
		.kipyPLOT   { text-align:center } 
	</style>

	<body>
"""
		for i in range( 0, len( self.h ) ) :
			if   self.h[i][0] == History.INPUT : s += '<p class="kipyINPUT">'
			elif self.h[i][0] == History.OUTPUT : s += '<p class="kipyOUTPUT">'
			elif self.h[i][0] == History.KIPY_MSG : s += '<p class="kipyMSG">'
			elif self.h[i][0] == History.PLOT_PATH : s += '<p class="kipyPLOT">'
			s += self.h[i][1] + "</p>\n"

		s += """
	</body>
</html>
"""
		return s

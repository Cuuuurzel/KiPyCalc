from time import asctime

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
		* { text-align:center; background-color:#202020; color:#FFFFFF; font-family: "Courier New", Courier, monospace; }
		div { border:1px solid #505050; border-radius:12px; padding:15px; margin:12px; }
		.history    { max-width:800px; margin:0 auto; padding:2px; }
		.kipyINPUT  { background-color:#2D2D50; color:#FFFFFF; text-align:left;   } 
		.kipyOUTPUT { background-color:#2D502D; color:#FFFFFF; text-align:right;  } 
		.kipyMSG    { background-color:#2D2D2D; color:#FFFFFF; } 
		.kipyPLOT   { background-color:#2D2D2D; color:#FFFFFF; } 
		.kipyTITLE  { color:#FFFFFF; padding:30px; }
	</style>

	<body>
		
		<h3 class="kipyTITLE"> Session saved on """ + asctime() + """  </h3>

		<div class="history">
"""
		for i in range( 0, len( self.h ) ) :
			if   self.h[i][0] == History.INPUT : s += '<div class="kipyINPUT"> -&gt; &nbsp;'
			elif self.h[i][0] == History.OUTPUT : s += '<div class="kipyOUTPUT">'
			elif self.h[i][0] == History.KIPY_MSG : s += '<div class="kipyMSG">'
			elif self.h[i][0] == History.PLOT_PATH : s += '<div class="kipyPLOT">'

			s += self.h[i][1]
			if self.h[i][0] == History.OUTPUT : s+= "&nbsp; &lt;-"
			s += "</div>\n"

		s += """
		</div>
	
		<h4 class="kipyTITLE"> Powered by <a href="https://play.google.com/store/apps/details?id=org.cuuuurzel.KiPyCalc"> Kipycalc </a> </h4>

	</body>
</html>
"""
		return s

kml_writer.py

A Simple KML Writer module written in Python for creating KML files for Google Earth.


#Usage example:
import kml_writer as kml

# Create document
kmldoc = kml.KMLDocument("My KML document")

# Create elements and add them to the document
folder = kml.Folder("Points", description="Folder with points")
kmldoc.addElement(folder)

trackStyle = kml.Style("trackStyle", line={'color': 'ff00ff00', 'width': '12'}, poly={'color': 'f0f0f0f0'})
pointStyle = kml.Style("pointStyle", icon={'icon': 'http://google.com/kml/example/icon.png'})
trackDescription = "<b>A basic html description</b>"
track = kml.Path(latitudes, longitudes, altsArray=altitudes, extrude=1, tessellate=1, name="A Track", description=trackDescription, style="trackStyle")
kmldoc.addElements(trackStyle, pointStyle, track)

for latitude, longitude, date in data:
    dt = kml.parseDate(date)
    point = kml.Point(latitude, longitude, datetime=dt, style="pointStyle")
    kmldoc.addElementToFolder(point, "Points")
    
# Write document to a file
kml.writeKML(kmldoc.document, "example.kml")

#############################################################
See Google's KML documentation for more information.

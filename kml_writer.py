#!/usr/bin/env python

'''
kml_writer.py

Created on 3 Nov 2011

@author: Jan Holownia <jan.holownia@gmail.com>
@summary: A module for creating KML files.

###########################################################
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

'''

import csv
import xml.dom.minidom as xdm
import dateutil.parser as dtparser


class Element(xdm.Element):
    """ A class to make KML output compatible with Google Earth """
    
    def writexml(self, writer, indent="", addindent="", newl=""):
        """ Write XML to the writer object """
        # indent = current indentation
        # addindent = indetation to add to higher levels
        # newl = newline string
        writer.write(indent + "<" + self.tagName)
        
        attrs = self._get_attributes()
        a_names = attrs.keys()
        a_names.sort()
        
        for a_name in a_names:
            writer.write(" %s=\"" %a_name)
            xdm._write_data(writer, attrs[a_name].value)
            writer.write("\"")
        
        if self.childNodes:
            newl2 = newl
            if len(self.childNodes) == 1 and self.childNodes[0].nodeType == xdm.Node.TEXT_NODE:
                indent, addindent, newl = "", "", ""            
            writer.write(">%s" %(newl))
            
            for node in self.childNodes:
                node.writexml(writer, indent+addindent, addindent, newl)                            
            writer.write("%s</%s>%s" %(indent, self.tagName, newl2))            
        else:
            writer.write("/>%s" %(newl))

xdm.Element = Element


def parseDate(dateString, dayFirst=True):
    """ Attempt to parse a date time string and return a string formatted for google earth as 'yyyy-mm-ddThh:mm:ssZ'. 
    
    Arguments:
    dateString - A date and time in an any format as string
    dayFirst - specifies if in case of ambiguous dates first number should be day or month. 
    
    Returns 0 on failure.
    
    """
    try:
        dt = dtparser.parse(dateString, dayfirst=dayFirst)
        return dt.isoformat() + "Z"
    except:        
        return 0


# Doesn't belong here but added for convenience
def readCSVFile(filename, delim=',', dialect=None):
    """ Read a CSV file. Return an array of data rows as dictionaries in {field_name: value} format. 
    
    Arguments:
    filename - a path to the file to read
    delim - CSV file delimiter
    dialect - csv.Dialect object to use for parsing the file
    
    """
            
    with open(filename, "r") as f:
        if dialect:
            reader = csv.DictReader(f, dialect=dialect)
        else:
            reader = csv.DictReader(f, delimiter=delim)
        records = []
        for row in reader:        
            records.append(row)
        
    return records

def writeKML(doc, filename):
    """ Write a KML document to a file 
        
    Arguments:
    doc - KMLDocument.document object to write
    filename - kml output filename 
       
    """
    fileOut = open(filename, "w")
    fileOut.write(doc.toprettyxml(indent="   ", encoding='UTF-8'))
    fileOut.close()
    
def printKML(doc):
    """ Print a KML document to the teminal """
    print doc.toprettyxml(indent="   ", encoding='UTF-8')
    
def getText(nodelist):
    """ Get string from text nodes """
    txt = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            txt.append(node.data)
    return "".join(txt)
    

class KMLDocument:
    """ KML document class """
    
    def __init__(self, title, description=""):
        """ Init KMLDocument """       
        self.title = title
        self.description = description
        self.document = self.kml()
        self.folders = []                
        
    def kml(self):
        """ Creates KML document and returns DOM document """
        doc = xdm.Document()
        
        # <kml>
        kml = doc.createElement('kml')
        kml.setAttribute('xmlns', 'http://www.opengis.net/kml/2.2')
        doc.appendChild(kml)
        
        # <document>
        document = doc.createElement('Document')
        kml.appendChild(document)
        
        # <name>
        docName = doc.createElement('name')
        document.appendChild(docName)    
        docNameText = doc.createTextNode(self.title)
        docName.appendChild(docNameText)
        
        # <description>
        docDesc = doc.createElement('description')    
        document.appendChild(docDesc)    
        docDescText = doc.createTextNode(self.description)
        docDesc.appendChild(docDescText)
        
        return doc
    
    def addElement(self, element):
        """ Add an element to the document 
        
        Arguments:
        element - xml.dom.minidom.Document object to be added
        
        """
        self.document.documentElement.getElementsByTagName('Document')[0].appendChild(element.kml().documentElement)
        
    def addElements(self, *elements):
        """ Convenience method for adding multiple elements """
        for element in elements:
            self.addElement(element)
        
    def addFolder(self, folder):
        """ Add folder to the document """
        self.addElement(folder)
        folderName = getText(folder.kml().getElementsByTagName("name")[0].childNodes)        
        self.folders.append(folderName)
        
    def addElementToFolder(self, element, folderName):
        """ Add element to the folder 
        
        The folder needs to be created earlier and added to the KMLDocument.
       
        """        
        def getFolderByName(name):
            folders = self.document.documentElement.getElementsByTagName('Folder')
            for folder in folders:
                if getText(folder.getElementsByTagName("name")[0].childNodes) == name:
                    return folder
                
        if folderName in self.folders:
            f = getFolderByName(folderName)
            f.appendChild(element.kml().documentElement)                       
        else:
            print "No folder named %s. Please create it first." % folderName


class Style:
    """ Style class. 
    
    Represents a Style element in Google Earth KML file.
    
    A Style defines the look of placemarks such as points, paths and polygons.  
    
    """    
    def __init__(self, id, icon=None, line=None, poly=None):
        """ Init Style
        
        Arguments:
        id - style id
        icon - defines IconStyle element
        line - defines LineStyle element
        poly - defines PolyStyle element
        
        These arguments should be dictionaries with key - value pairs for the elements they define. A single style
        can be used for more than one type of element. Styles should be added to the document before they are used.
        
        Example:
        # A green polygon with thick green lines.
        linestyle = {'color': '7f00ffff', 'width': '8'}
        polystyle = {'color': '7f00ff00}
        
        yellowPolyStyle = Style('yellowPoly', line=linestyle, poly=polystyle)
        
        # A white pushpin
        pointstyle = {'icon': 'http://maps.google.com/mapfiles/kml/paddle/wht-blank.png'}
        
        whitePointStyle = Style('whitePoint', icon=pointstyle)
        
        """
        self.id = id
        self.icon = icon
        self.line = line
        self.poly = poly
        
    def kml(self):
        """ Create Style node. Return xml.dom.minidom.Document """
        doc = xdm.Document()
        
        # <Style>
        style = doc.createElement('Style')        
        doc.appendChild(style)
        style.setAttribute("id", self.id)
        
        # <IconStyle>
        if self.icon:
            iconstyle = doc.createElement('IconStyle')
            for k, v in self.icon.items():
                if k.lower() == "icon":
                    iconNode = doc.createElement('Icon')
                    iconstyle.appendChild(iconNode)
                    href = doc.createElement('href')
                    iconNode.appendChild(href)
                    hrefText = doc.createTextNode(v)
                    href.appendChild(hrefText)
                else:
                    kNode = doc.createElement(k)
                    iconstyle.appendChild(kNode)
                    kValue = doc.createTextNode(v)
                    kNode.appendChild(kValue)
                    
        # <LineStyle>
        if self.line:
            linestyle = doc.createElement('LineStyle')
            style.appendChild(linestyle)            
            for k, v in self.line.items():
                kNode = doc.createElement(k)
                linestyle.appendChild(kNode)
                kValue = doc.createTextNode(v)
                kNode.appendChild(kValue)
                
        # <PolyStyle>                
        if self.poly:
            polystyle = doc.createElement('PolyStyle')
            style.appendChild(polystyle)
            for k, v in self.poly.items():
                kNode = doc.createElement(k)
                polystyle.appendChild(kNode)
                kValue = doc.createTextNode(v)
                kNode.appendChild(kValue)
        
        return doc
    
    
class StyleMap:
    """ StyleMap class. 
    
    Represents a Google Earth StyleMap which maps element state to a style.
    """
    
    def __init__(self, id, styles):
        """ Init StyleMap
        
        Arguments:
        id - StyleMap id
        styles - a dictionary of state - styleUrl pairs
        
        Example:
        # A point that changes when hovered over.
        myPointStyle = StyleMap('normal': 'whitePoint', 'highlight': 'redPoint')        
        
        """
        self.id = id
        self.styles = styles
        
    def kml(self):
        """ Create StyleMap node. Return xml.dom.minidom.Document """
        doc = xdm.Document()
        
        # <Style>
        stylemap = doc.createElement('StyleMap')        
        doc.appendChild(stylemap)
        stylemap.setAttribute("id", self.id)
        
        # <Pair> (key + styleUrl)
        for k, v in self.styles.items():
            pair = doc.createElement('Pair')
            stylemap.appendChild(pair)
            key = doc.createElement('key')
            pair.appendChild(key)
            keyValue = doc.createTextNode(k)
            key.appendChild(keyValue)
            styleUrl = doc.createElement('styleUrl')
            pair.appendChild(styleUrl)
            url = doc.createTextNode(str(v))
            styleUrl.appendChild(url)
            
        return doc                
       

class Folder:
    """ Folder class """
    
    def __init__(self, name):
        """ Init Folder class 
        
        Arguments:
        name - Folder name
        
        """
        self.name = name
        
    def kml(self):
        """ Creates Folder element in KML. Returns xml.dom.minidom.Document """
        doc = xdm.Document()
        
        # <Fodler>
        folder = doc.createElement('Folder')
        doc.appendChild(folder)
        
        # <name>
        nameNode = doc.createElement('name')
        folder.appendChild(nameNode)
        nameText = doc.createTextNode(self.name)
        nameNode.appendChild(nameText)
        
        return doc

    
class Placemark:
    """ Placemark class. 
    
    A placemark element in Google Earth without any graphical representation (doesn't show on the map). 
    
    """
    def __init__(self, name="", description=""):                
        self.name = name
        self.description = description
        
    def kml(self):
        """ Creates placemark element in KML """
        doc = xdm.Document()
        
        # <Placemark>
        pm = doc.createElement('Placemark')
        self.doc.appendChild(pm)
        
        # <name>
        if self.name != '':
            nameNode = doc.createElement('name')
            pm.appendChild(nameNode)
            nameText = doc.createTextNode(self.name)
            nameNode.appendChild(nameText)
            
        # <description>
        desc = doc.createElement('description')
        pm.appendChild(desc)
        descText = doc.createTextNode(self.description)
        desc.appendChild(descText)
        
        return doc    
        
        
class Point(Placemark):
    """ Point class. 
    
    Represents a single point or a push pin in Google Earth.
    
    """
    
    def __init__(self, latitude, longitude, name="", description="", datetime="", startDate="", endDate="", style=None):
        """ Init Point.
        
        Arguments:
        latitude - geographical latitude of the point
        longitude - geographical longitude of the point
        name - point's name
        description - point's description. This is the "baloon" that pops up when the point is clicked. It can contain
                        html with images and links etc.
        datetime - used for TimeStamp element. A point with a TimeStamp will only display for a short period of time. Tightly sampled
                    TimeStamps can be used to create an animation
        startDate - a date when the point appears
        endDate - a date when the point dissapears
        style - a style to use for the point
        
        Note that time arguments are optional and are generally only used for animations. Either datetime or start and end dates should be used, not both.
        
        """
        Placemark.__init__(self, name, description)
        self.lat = latitude
        self.lon = longitude
        self.dt = datetime
        self.sdt = startDate
        self.edt = endDate
        self.style = style
        
    def kml(self):
        """ Create point node. Return xml.dom.minidom.Document. """
        doc = xdm.Document()
    
        # <Placemark>
        pm = doc.createElement('Placemark')
        doc.appendChild(pm)
        
        # <name>
        if self.name != '':
            nameNode = doc.createElement('name')
            pm.appendChild(nameNode)
            nameText = doc.createTextNode(self.name)
            nameNode.appendChild(nameText)
            
        # <styleUrl>
        if self.style:
            styleUrl = doc.createElement('styleUrl')
            pm.appendChild(styleUrl)
            url = doc.createTextNode("#" + self.style)
            styleUrl.appendChild(url)        
        
        # <description>
        if self.description != "":
            desc = doc.createElement('description')
            pm.appendChild(desc)
            descText = doc.createTextNode(self.description)
            desc.appendChild(descText)
        
        # <point>
        pt = doc.createElement('Point')
        pm.appendChild(pt)
        
        # <coordinates>
        coords = doc.createElement('coordinates')
        pt.appendChild(coords)
        coordsText = doc.createTextNode('%s, %s, 0' %(self.lon, self.lat))
        coords.appendChild(coordsText)
        
        # <TimeStamp>
        if self.dt != "":
            timestamp = doc.createElement('TimeStamp')
            pm.appendChild(timestamp)
            # <when>
            when = doc.createElement('when')
            timestamp.appendChild(when)
            whenText = doc.createTextNode(self.dt)
            when.appendChild(whenText)
        else:        
            # <TimeSpan>
            if self.sdt != '':        
                timespan = doc.createElement('TimeSpan')
                pm.appendChild(timespan)
                
                # <begin>
                begin = doc.createElement('begin')
                timespan.appendChild(begin)
                beginText = doc.createTextNode(self.sdt)
                begin.appendChild(beginText)       
                
                # <end>
                if self.edt != '':            
                    end = doc.createElement('end')
                    timespan.appendChild(end)
                    endText = doc.createTextNode(self.edt)
                    end.appendChild(endText)       
        
        return doc


class Path(Placemark):
    """ Path class.
    
    Represents a path (track) in Google Earth.
    
    """
    
    def __init__(self, latsArray, lonsArray, altsArray=None, extrude=0, tessellate=0, altitudeMode="absolute", startDate="", endDate="", name="", description="", style=None):
        """ Init Path.
        
        Arguments:
        latsArray - an array of geographical latitudes for the path
        lonsArray - an array of geographical longitudes for the path
        altsArray - an array of altitudes for the path
        extrude - whether the path should be extruded down to the ground
        tessellated - whether the path should be tessellated
        altitudeMode - specifies the way Google Earth reads altitude values (absolute|relativeToGround|relativeToSeaFloor|clampToGround|clampToSeaFloor)
        startDate - a start date for TimeSpan element
        endDate - an endDate for TimeSpan element        
        name - track name
        description - track description, can use html
        style - a style to be used by the track
        
        Note that date arguments are optional and not needed for a track that displays permanently. Altitudes are also not
        necessary for a flat track.        
        
        """
        Placemark.__init__(self, name, description)
        self.lats = latsArray
        self.lons = lonsArray
        self.alts = altsArray
        self.extrude = extrude
        self.tess = tessellate
        self.altMode = altitudeMode
        self.sdt = startDate
        self.edt = endDate        
        self.style = style
       
                
    def kml(self):
        """ Create Path node. Return xml.dom.minidom.Document """
        doc = xdm.Document()
    
        # <Placemark>
        pm = doc.createElement('Placemark')
        doc.appendChild(pm)
        
        # <name>
        if self.name != '':
            nameNode = doc.createElement('name')
            pm.appendChild(nameNode)
            nameText = doc.createTextNode(self.name)
            nameNode.appendChild(nameText)
            
        # <styleUrl>
        if self.style:
            styleUrl = doc.createElement('styleUrl')
            pm.appendChild(styleUrl)
            url = doc.createTextNode("#" + self.style)
            styleUrl.appendChild(url)
            
        # <description>
        if self.description != "":
            desc = doc.createElement('description')
            pm.appendChild(desc)
            descText = doc.createTextNode(self.description)
            desc.appendChild(descText)
            
        # <TimeSpan>
        if self.sdt != '':        
            timespan = doc.createElement('TimeSpan')
            pm.appendChild(timespan)
            
            # <begin>
            begin = doc.createElement('begin')
            timespan.appendChild(begin)
            beginText = doc.createTextNode(self.sdt)
            begin.appendChild(beginText)       
            
            # <end>
            if self.edt !='':
                end = doc.createElement('end')
                timespan.appendChild(end)
                endText = doc.createTextNode(self.edt)
                end.appendChild(endText)
        
        # <LineString>
        ls = doc.createElement('LineString')
        pm.appendChild(ls)        
        # <extrude>
        extr = doc.createElement('extrude')
        ls.appendChild(extr)
        extrText = doc.createTextNode(str(self.extrude))
        extr.appendChild(extrText)
        # <tessellate>
        tess = doc.createElement('tessellate')
        ls.appendChild(tess)
        tessText = doc.createTextNode(str(self.tess))
        tess.appendChild(tessText)
        # <altitudeMode>
        altmode = doc.createElement('altitudeMode')
        ls.appendChild(altmode)
        altmodeText = doc.createTextNode(self.altMode)
        altmode.appendChild(altmodeText)                    
        # <coordinates>
        coords = doc.createElement('coordinates')
        ls.appendChild(coords)        
        if not self.alts:
            for lat, lon in zip(self.lats, self.lons):
                coordsText = doc.createTextNode('%s, %s, 0' %(lon, lat))
                coords.appendChild(coordsText)
        else:
            for lat, lon, alt in zip(self.lats, self.lons, self.alts):
                coordsText = doc.createTextNode('%s, %s, %s' %(lon, lat, alt))
                coords.appendChild(coordsText)             
        
        return doc
    
    
class GroundOverlay:
    """GroundOverlay class.
    
    Represents Google Earth GroundOverlay, an image that is displayed on the ground.
    
    """
    
    def __init__(self, name, description, icon, north, south, east, west, rotation=0):
        """ Init GroundOverlay.
        
        Arguments:
        name - overlay name
        description - overlay description
        icon - an url to the image to be used as an overlay
        north - latitude of northmost point of the image
        south - latitude of southmost point of the image
        east - longitude of eastmost point of the image
        west - longitude of westmost point of the image
        rotation - rotation of y-axis of the image in degrees, clockwise
        
        """
        self.name = name
        self.desc = description
        self.icon = icon
        self.north = north
        self.south = south
        self.east = east
        self.west = west
        self.rotation = rotation
        
    def kml(self):
        """ Create GoundOverlay node. Return xml.dom.minidom.Document """
        doc = xdm.Document()
        
        # <GroundOverlay>
        overlay = doc.createElement('GroundOverlay')
        doc.appendChild(overlay)
        
        # <name>
        if self.name != '':
            nameNode = doc.createElement('name')
            overlay.appendChild(nameNode)
            nameText = doc.createTextNode(self.name)
            nameNode.appendChild(nameText)

        # <description>    
        if self.desc != '':
            descNode = doc.createElement('description')
            overlay.appendChild(descNode)
            descText = doc.createTextNode(self.desc)
            descNode.appendChild(descText)
            
        # <Icon>
        iconNode = doc.createElement('Icon')
        overlay.appendChild(iconNode)
        # <href>
        href = doc.createElement('href')
        iconNode.appendChild(href)
        hrefText = doc.createTextNode(self.icon)
        href.appendChild(hrefText)
        
        # <LatLonBox>
        latlonbox = doc.createElement('LatLonBox')
        overlay.appendChild(latlonbox)
        # <north>
        north = doc.createElement('north')
        latlonbox.appendChild(north)
        northText = doc.createTextNode(str(self.north))
        north.appendChild(northText)
        # <south>
        south = doc.createElement('south')
        latlonbox.appendChild(south)
        southText = doc.createTextNode(str(self.south))
        south.appendChild(southText)        
        # <east>
        east = doc.createElement('east')
        latlonbox.appendChild(east)
        eastText = doc.createTextNode(str(self.east))
        east.appendChild(eastText)        
        # <west>
        west = doc.createElement('west')
        latlonbox.appendChild(west)
        westText = doc.createTextNode(str(self.west))
        west.appendChild(westText)
        # <rotation>
        rotation = doc.createElement('rotation')
        latlonbox.appendChild(rotation)
        rotationText = doc.createTextNode(str(self.rotation))
        rotation.appendChild(rotationText)
        
        return doc
    
    
class Polygon(Placemark):
    """ Polygon class.
    
    Represents Google Earth Polygon - a 2 or 3-dimensional shape, on or above the ground.
     
    """
    def __init__(self, name, description, coordinates, style=None, extrude=1, altitudeMode="relativeToGround"):
        """ Init Polygon
        
        Arguments:
        name - Polygon name
        description - Polygon description, can contain html
        coordinates - new line separated list of geographical coordinates in format of: longitude, latitude, altitude\n
        style - kml style to use for the polygon
        extrude - whether the polygon should be extruded down to the ground
        
        """        
        Placemark.__init__(self, name, description)
        self.coordinates = coordinates
        self.extrude = extrude
        self.altitudeMode = altitudeMode
        self.style = style
        
    def kml(self):
        """ Create Polygon node. Return xml.dom.minidom.Document """
        doc = xdm.Document()
        
        # <Placemark>
        pm = doc.createElement('Placemark')
        doc.appendChild(pm)
        
        # <name>
        if self.name != '':
            nameNode = doc.createElement('name')
            pm.appendChild(nameNode)
            nameText = doc.createTextNode(self.name)
            nameNode.appendChild(nameText)
            
        # <styleUrl>
        if self.style:
            styleUrl = doc.createElement('styleUrl')
            pm.appendChild(styleUrl)
            url = doc.createTextNode("#" + self.style)
            styleUrl.appendChild(url)                    
        
        # <description>
        if self.description != "":
            desc = doc.createElement('description')
            pm.appendChild(desc)
            descText = doc.createTextNode(self.description)
            desc.appendChild(descText)
        
        # <Polygon>
        poly = doc.createElement('Polygon')
        pm.appendChild(poly)
        # <extrude>
        extr = doc.createElement('extrude')
        poly.appendChild(extr)
        extrText = doc.createTextNode(str(self.extrude))
        extr.appendChild(extrText)
        # <altitudeMode>
        am = doc.createElement('altitudeMode')
        poly.appendChild(am)
        amText = doc.createTextNode(self.altitudeMode)
        am.appendChild(amText)
        
        # <outerBoundaryIs>
        obi = doc.createElement('outerBoundaryIs')
        poly.appendChild(obi)
        # <LinearRing>
        lr = doc.createElement('LinearRing')
        obi.appendChild(lr)
        # <coordinates>
        coords = doc.createElement('coordinates')
        lr.appendChild(coords)
        for c in self.coordinates.split("\n"):
            coordsText = doc.createTextNode(c)
            coords.appendChild(coordsText)
        
        return doc
 
    
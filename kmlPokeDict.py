from xml.etree import ElementTree
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import xml.etree.ElementTree as ET

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, method='html', encoding='utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="   ")

def getKMLStops():
    tree = ET.parse('output (1).kml')
    root = tree.getroot()
    root = root[0]
    pokeDict = {}
    for child in root:
        #print(child.tag)
        #print(prettify(child))
        if "Placemark" in child.tag:
            name = None
            loc = None
            for kid in child:
                if "name" in kid.tag:
                    name = kid.text
                if "Point" in kid.tag:
                    loc = kid[0].text

            #     name = child[1].text
            #     loc = child[2][0].text
            # print(child[2].tag)
            #print(child[1].tag)
            if name != None and loc != None:
                pokeDict[name] = loc
            else:
                raise Exception("Location/Name data are not in this file")
    #print(root.findtext("ns0:Placemark"))
    #placemark = root.getSubElement()
    newRoot = prettify(root)
    #print(newRoot)
    #print(stop)
    #print(pokeDict)
    #print(len('</ns0:coordinates>'))
    numEntries = 0
    #rint(test)

    for elem in pokeDict.keys():
        numEntries += 1
        #print(elem, end = ": \n")
        #print(pokeDict[elem], end = '\n\n')
        string = pokeDict[elem].split(',')
        pokeDict[elem] = (float(string[0]), float(string[1]), 0.0)

    #print(pokeDict['Sombrero Duck'])
    #print(numEntries)
    return(pokeDict)
    #print(tag)

def pokeDictFromFile(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    root = root[0]
    pokeDict = {}
    for child in root:

        if "Placemark" in child.tag:
            name = None
            loc = None
            for kid in child:
                if "name" in kid.tag:
                    name = kid.text
                if "Point" in kid.tag:
                    loc = kid[0].text

            #     name = child[1].text
            #     loc = child[2][0].text
            # print(child[2].tag)
            #print(child[1].tag)
            if name != None and loc != None:
                pokeDict[name] = loc
            else:
                raise Exception("Location/Name data are not in this file")

    newRoot = prettify(root)
    print(pokeDict)
    numEntries = 0


    for elem in pokeDict.keys():
        numEntries += 1

        string = pokeDict[elem].split(',')
        pokeDict[elem] = (float(string[0]), float(string[1]), 0.0)

    return(pokeDict)
 
def writeKMLFile(filename, pokestops):
    f = open(filename, 'w')
    root = Element("kml", xmlns='http://www.opengic.net/kml/2.2')
    document = SubElement(root, 'Document')
    name = SubElement(document, 'Name')
    file = filename.split('.')
    name.text = file[0]
    for stop in pokestops:
        placemark = SubElement(document, 'Placemark')
        name = SubElement(placemark, 'name')
        styleURL = SubElement(placemark, 'styleUrl')
        point = SubElement(placemark, 'Point')
        coord = SubElement(point, 'coordinates')

        name.text = stop.name
        styleURL.text = '#icon-959-4186F0-nodesc'
        coord.text = str(stop.loc[0]) + ',' + str(stop.loc[1]) + ',0.0'
    
    style = SubElement(document,'Style', id ="icon-959-4186F0-nodesc-normal")
    IconStyle = SubElement(style, 'IconStyle')
    color = SubElement(IconStyle, 'color')
    color.text = 'ffF08641'
    scale = SubElement(IconStyle, 'scale')
    scale.text = '1.1'
    icon = SubElement(IconStyle, 'Icon')
    href = SubElement(icon, 'href')
    href.text = 'http://www.gstatic.com/mapspro/images/stock/959-wht-circle-blank.png'
    labelstyle = SubElement(style, 'LabelStyle')
    scale = SubElement(labelstyle, 'scale')
    scale.text='0.0'
    balloonStyle = SubElement(style, 'BalloonStyle')
    text = SubElement(balloonStyle, 'text')
    text.text = '<![CDATA[<h3>$[name]</h3>]]>'

    style = SubElement(document, 'Style', id = "icon-959-4186F0-nodesc-highlight")
    IconStyle = SubElement(style, 'IconStyle')
    color = SubElement(IconStyle, 'color')
    color.text = 'ffF08641'
    scale = SubElement(IconStyle, 'scale')
    scale.text = '1.1'
    icon = SubElement(IconStyle, 'Icon')
    href = SubElement(icon, 'href')
    href.text = 'http://www.gstatic.com/mapspro/images/stock/959-wht-circle-blank.png'
    labelstyle = SubElement(style, 'LabelStyle')
    scale= SubElement(labelstyle, 'scale')
    scale.text = '1.1'
    balloonStyle = SubElement(style, 'BalloonStyle')
    text = SubElement(balloonStyle, 'text')
    text.text = '''<![CDATA[<h3>$[name]</h3>]]>'''

    StyleMap = SubElement(document, 'StyleMap', id ="icon-959-4186F0-nodesc")
    pair = SubElement(StyleMap, 'Pair')
    key = SubElement(pair, 'key')
    key.text= 'normal'
    styleUrl = SubElement(pair, 'styleUrl')
    styleUrl.text = '#icon-959-4186F0-nodesc-normal'

    pair = SubElement(StyleMap, 'Pair')
    key = SubElement(pair, 'key')
    key.text= 'highlight'
    styleUrl = SubElement(pair, 'styleUrl')
    styleUrl.text = '#icon-959-4186F0-nodesc-highlight'


    prettyRoot = prettify(root)
    htmlPretty = ''
    ind = 0
    while(ind < len(prettyRoot)):
        if ind < len(prettyRoot) - 4 and prettyRoot[ind:ind+4] == '&lt;':
            htmlPretty += '<'
            ind+=4
        elif ind < len(prettyRoot) - 4 and prettyRoot[ind:ind+4] == '&gt;':
            htmlPretty += '>'
            ind+=4
        else:
            htmlPretty+=prettyRoot[ind]
            ind+=1
    f.write(htmlPretty)
    f.close()

getKMLStops()
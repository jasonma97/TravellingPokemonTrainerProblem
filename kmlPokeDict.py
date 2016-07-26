from xml.etree import ElementTree
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import xml.etree.ElementTree as ET

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
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
 

getKMLStops()
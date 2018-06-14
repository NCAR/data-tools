#
# Utilities for inserting values into ISO 19139 documents
#

import numbers
from lxml import etree as ElementTree       # ISO XML parser
from copy import deepcopy                   # Allows deep copy of ISO elements

# Debug
import logging
import pprint
log = logging.getLogger(__name__)


# We need XML namespace mappings in order to search the ISO element tree
XML_NAMESPACE_MAP = {'gmd': 'http://www.isotc211.org/2005/gmd',
                     'xlink': 'http://www.w3.org/1999/xlink', 
                     'gco': 'http://www.isotc211.org/2005/gco', 
                     'gml': 'http://www.opengis.net/gml'}

#
# Tree-wide operations
#
def getXMLTree(templateFilePath):
    tree = ElementTree.parse(templateFilePath)
    root = tree.getroot()
    return root


def toString(xml_tree):
    outputString = ElementTree.tostring(xml_tree, pretty_print=True)
    return outputString

#
# XML Element Query operations
#
def getFirst(someList):
    ''' Return first item in a list if list is nonempty (returns None otherwise). '''
    if someList:
        return someList[0]
    return None

def getLast(someList): 
    ''' Return last item in a list if list is nonempty (returns None otherwise). '''
    if someList:
        return someList[-1]
    return None

def getElement(baseElement, elementPath):
    ''' Search XML element tree and return the first matching element '''
    elements = baseElement.xpath(elementPath, namespaces=XML_NAMESPACE_MAP)
    element = getFirst(elements)
    assert element != None
    return element

def getLastElement(baseElement, elementPath):
    ''' Search XML element tree and return the first matching element '''
    elements = baseElement.xpath(elementPath, namespaces=XML_NAMESPACE_MAP)
    element = getLast(elements)
    assert element != None
    return element


def cutElement(baseElement, elementPath, returnIndex = False):
    ''' Search XML element tree and cut the first matching element. '''
    elements = baseElement.xpath(elementPath, namespaces=XML_NAMESPACE_MAP)
    element = getFirst(elements)

    parent = element.getparent()
    elementIndex = parent.index(element)
    parent.remove(element)
    # Sometimes the element's index is needed for correct insert placement.
    if returnIndex:
        return element, parent, elementIndex
    else:
        return element, parent

def copyElement(element):
    ''' Create a deep copy of some XML element. '''
    elementCopy = deepcopy(element)
    return elementCopy

#
# XML Element Modify operations
#

def setTextOrMarkMissing(element, fillText, setCodeListValue = False):
    if isinstance(fillText, numbers.Real):
        fillText = str(fillText)
    elif fillText is None:
        fillText = ""
    element.text = fillText

    # Set or remove "gco:nilReason = missing" attribute from parent element
    missingAttribute = '{http://www.isotc211.org/2005/gco}nilReason'
    hasParent = element.getparent() is not None
    hasParentWithMissing = hasParent and element.getparent().attrib.has_key(missingAttribute)
    if len(fillText) > 0 and hasParentWithMissing:
        element.getparent().attrib.pop(missingAttribute)
    elif len(fillText) == 0 and hasParent:
        element.getparent().attrib[missingAttribute] = "missing"

    # Also set code list value if specified
    if setCodeListValue:
        element.attrib['codeListValue'] = fillText


def setElementValue(xmlTreeRoot, xPath, value, setCodeListValue = False):
    """ Set the text value, and optionally the code list value, of an element in an XML tree. """
    element = getElement(xmlTreeRoot, xPath)
    setTextOrMarkMissing(element, value, setCodeListValue)


#
# XML Element Insert operations
#

def addChildList(xml_root, elementXPath, childXPath, valueList, setCodeListValue = False):
    element = getElement(xml_root, elementXPath)
    emptyChild, parent = cutElement(element, childXPath)
    for value in valueList:
        childCopy = copyElement(emptyChild)
        setTextOrMarkMissing(childCopy, value, setCodeListValue)
        parent.append(childCopy)




#
#  To run these unit tests: type "./run_tests.sh" at a command prompt.
#

import unittest
import json
from lxml.etree import Element
from lxml import etree as ElementTree


import api.util.xml as xml

#
# Unit test Setup/Helper functions
#

def addXPathToXML(xml_tree, XPath, childText):
    ''' This helper method adds to the XML tree a nested set of elements corresponding to a given XPath.
        The given childText is placed in the rightmost element of the XPath.
    '''
    # Construct XPath XML elements right-to-left (bottom up).
    elementNames = XPath.split('/')
    child = Element(elementNames.pop(-1))
    child.text = childText

    topElement = child
    while elementNames:
        newTop = Element(elementNames.pop(-1))
        newTop.append(topElement)
        topElement = newTop

    xml_tree.append(topElement)
    return xml_tree



#
# Unit tests
#
class XML_Test(unittest.TestCase):

   def setUp(self):
      self.simpleTree = Element('Root')

   def testGetElement_ReturnsFirstMatch(self):
      ''' If more than one matching element exists, the first element should be returned.
      '''
      xml_tree = self.simpleTree
      xml_tree = addXPathToXML(xml_tree, "Child", '1')
      xml_tree = addXPathToXML(xml_tree, "Child", '2')

      foundElement = xml.getFirstElement(xml_tree, 'Child')
      self.assertEqual(foundElement.text, '1')



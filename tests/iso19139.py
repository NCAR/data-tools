#
#  To run these unit tests: type "./run_tests.sh" at a command prompt.
#

import unittest
import json
from lxml.etree import Element
from lxml import etree as ElementTree

import api.util.iso19139 as iso
import api.util.xml as xml


#
# Unit test Setup/Helper functions
#


def getEmptyTemporalExtentXMLTree():
    ''' Create a simplified XML Tree with a temporal extent whose values are all missing. '''
    root = ElementTree.fromstring('''
    <root xmlns:gco="http://www.isotc211.org/2005/gco" 
          xmlns:gmd="http://www.isotc211.org/2005/gmd" 
          xmlns:gml="http://www.opengis.net/gml" 
          xmlns:xlink="http://www.w3.org/1999/xlink">
      <gml:TimePeriod gml:id="timePeriodDate">
        <gml:beginPosition></gml:beginPosition>
        <gml:endPosition></gml:endPosition>
      </gml:TimePeriod>
    </root>
    ''')
    return root


#
# Unit tests
#
class ISO19139_Test(unittest.TestCase):

   def setUp(self):
      self.simpleTree = Element('Root')

   def testModifyTemporalExtent_SetsIndeterminateAttributes(self):
      ''' If special time values are used for temporal extent, the "indeterminatePosition" attribute should be set.
      '''
      xml_tree = getEmptyTemporalExtentXMLTree()
      extentRecord = {"start": "unknown", "end": "now"}
      iso.modifyTemporalExtent(xml_tree, '.', extentRecord)

      # Debug any XML changes this way:
      #print(ElementTree.tostring(xml_tree, pretty_print=True))

      element = xml.getFirstElement(xml_tree, iso.childXPaths['extentBegin'])
      self.assertEqual(element.attrib['indeterminatePosition'], extentRecord['start'])

      element = xml.getFirstElement(xml_tree, iso.childXPaths['extentEnd'])
      self.assertEqual(element.attrib['indeterminatePosition'], extentRecord['end'])



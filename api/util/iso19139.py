#
#  Code for modifying DSET Concepts ISO 19139 XML file.
#

import api.util.xml as xml

# # Debug
# import logging
# import pprint
# log = logging.getLogger(__name__)


childXPaths =  {
     'individual'  : './/gmd:individualName/gco:CharacterString',
     'position'    : './/gmd:positionName/gco:CharacterString',
     'organization': './/gmd:organisationName/gco:CharacterString',
     'email'       : './/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:electronicMailAddress/gco:CharacterString',
     'roleCode'    : './/gmd:role/gmd:CI_RoleCode',
     'keyword'     : 'gmd:keyword/gco:CharacterString',
     'repTypeCode' : 'gmd:MD_SpatialRepresentationTypeCode',
     'distance'    : './/gco:Distance',
     'real'        : 'gco:Real',
     'string'      : 'gco:CharacterString',
     'stringURL'   : 'gco:CharacterString[starts-with(.,"http://") or starts-with(.,"https://")]',
     'linkage'     : 'gmd:linkage/gmd:URL',
     'name'        : 'gmd:name/gco:CharacterString',
     'description' : 'gmd:description/gco:CharacterString',
     'extentBegin' : 'gml:TimePeriod/gml:beginPosition',
     'extentEnd'   : 'gml:TimePeriod/gml:endPosition',
     'westLong'    : './/gmd:westBoundLongitude/gco:Decimal',
     'eastLong'    : './/gmd:eastBoundLongitude/gco:Decimal',
     'northLat'    : './/gmd:northBoundLatitude/gco:Decimal',
     'southLat'    : './/gmd:southBoundLatitude/gco:Decimal',
     'relatedLink' : 'gmd:MD_MetadataExtensionInformation/gmd:extensionOnLineResource/gmd:CI_OnlineResource',
   } 

#
#  ISO Element Modification functions
#

def modifyOnlineResource(resourceElement, url, name='', description=''):
    """ Modify contents of an "onLineResource" ISO element """
    elementURL = xml.getFirstElement(resourceElement, childXPaths['linkage'])
    xml.setTextOrMarkMissing(elementURL, url)

    elementName = xml.getFirstElement(resourceElement, childXPaths['name'])
    xml.setTextOrMarkMissing(elementName, name)

    elementDescription = xml.getFirstElement(resourceElement, childXPaths['description'])
    xml.setTextOrMarkMissing(elementDescription, description)


def modifyBoundingBox(xml_root, bboxXPath, bboxRecord):
    """ Modify contents of a "geographic bounding box" ISO element """
    bboxElement = xml.getFirstElement(xml_root, bboxXPath)

    elementWest = xml.getFirstElement(bboxElement, childXPaths['westLong'])
    xml.setTextOrMarkMissing(elementWest, bboxRecord['west'])

    elementEast = xml.getFirstElement(bboxElement, childXPaths['eastLong'])
    xml.setTextOrMarkMissing(elementEast, bboxRecord['east'])

    elementNorth = xml.getFirstElement(bboxElement, childXPaths['northLat'])
    xml.setTextOrMarkMissing(elementNorth, bboxRecord['north'])

    elementSouth = xml.getFirstElement(bboxElement, childXPaths['southLat'])
    xml.setTextOrMarkMissing(elementSouth, bboxRecord['south'])


def modifyTemporalExtent(xml_root, extentXPath, extentRecord):
    """ Modify contents of a "temporal extent" ISO element."""
    indeterminatePositions = {'before', 'after', 'now', 'unknown'}

    extentElement = xml.getFirstElement(xml_root, extentXPath)
    elementBegin = xml.getFirstElement(extentElement, childXPaths['extentBegin'])
    xml.setTextOrMarkMissing(elementBegin, extentRecord['start'])
    if extentRecord['start'] in indeterminatePositions:
        elementBegin.attrib['indeterminatePosition'] = extentRecord['start']

    elementEnd = xml.getFirstElement(extentElement, childXPaths['extentEnd'])
    xml.setTextOrMarkMissing(elementEnd, extentRecord['end'])
    if extentRecord['end'] in indeterminatePositions:
        elementEnd.attrib['indeterminatePosition'] = extentRecord['end']


def modifyContactData(contactElement, contactData, impliedRoleValue = None):
    """ Modify contents of a "contact" ISO element, a.k.a ResponsibleParty element.
        Modify all values, substituting empty text where values are not given. """

    #  For some contact elements, a specific role value is implied.  Set this value if given.
    if impliedRoleValue:
        contactData['role'] = impliedRoleValue

    nameValue = contactData.get('name', "")
    element = xml.getFirstElement(contactElement, childXPaths['individual'])
    xml.setTextOrMarkMissing(element, nameValue)

    positionValue = contactData.get('position', "")
    element = xml.getFirstElement(contactElement, childXPaths['position'])
    xml.setTextOrMarkMissing(element, positionValue)

    organizationValue = contactData.get('organization', "")
    element = xml.getFirstElement(contactElement, childXPaths['organization'])
    xml.setTextOrMarkMissing(element, organizationValue)

    emailValue = contactData.get('email', "")
    element = xml.getFirstElement(contactElement, childXPaths['email'])
    xml.setTextOrMarkMissing(element, emailValue)

    roleValue = contactData.get('role', "")
    element = xml.getFirstElement(contactElement, childXPaths['roleCode'])
    xml.setTextOrMarkMissing(element, roleValue)
    element.attrib['codeListValue'] = roleValue


def modifyContactDataSelectively(contactElement, contactData):
    """ Modify contents of a "contact" XML element, a.k.a ResponsibleParty element.
        Only override XML values if fill values are given, so XML template values are unchanged. """
    nameValue = contactData.get('name', None)
    if nameValue:
        element = xml.getFirstElement(contactElement, childXPaths['individual'])
        xml.setTextOrMarkMissing(element, nameValue)

    positionValue = contactData.get('position', None)
    if positionValue:
        element = xml.getFirstElement(contactElement, childXPaths['position'])
        xml.setTextOrMarkMissing(element, positionValue)

    organizationValue = contactData.get('organization', None)
    if organizationValue:
        element = xml.getFirstElement(contactElement, childXPaths['organization'])
        xml.setTextOrMarkMissing(element, organizationValue)

    emailValue = contactData.get('email', None)
    if emailValue:
        element = xml.getFirstElement(contactElement, childXPaths['email'])
        xml.setTextOrMarkMissing(element, emailValue)

    roleValue = contactData.get('role', None)
    if roleValue:
        element = xml.getFirstElement(contactElement, childXPaths['roleCode'])
        xml.setTextOrMarkMissing(element, roleValue)
        element.attrib['codeListValue'] = roleValue


# 
# Methods for inserting a collection of related ISO elements.
#

def addSpatialResolutionDistances(xml_root, resolutionXPath, resolutionList):
    """ Append a number of Spatial Resolution "distance" ISO elements. """
    insertCounter = 0
    resolutionElement, resolutionParent, elementIndex = xml.cutElement(xml_root, resolutionXPath, True)
    for resolution in resolutionList:
        elementCopy = xml.copyElement(resolutionElement)
        distanceElement = xml.getFirstElement(elementCopy, childXPaths['distance'])
        xml.setTextOrMarkMissing(distanceElement, resolution['distance'])
        distanceElement.attrib['uom'] = resolution['units']
        # Insert element copies back into parent, in order of creation.
        resolutionParent.insert(elementIndex + insertCounter, elementCopy)
        insertCounter += 1


def appendContactData(xml_root, contactXPath, contactData, impliedRoleValue = None):
    """ Append a new contact element to a collection of ResponsibleParty elements """
    contactElement = xml.getLastElement(xml_root, contactXPath)
    contactParent = contactElement.getparent()
    contactIndex = contactParent.index(contactElement)
    elementCopy = xml.copyElement(contactElement)
    modifyContactData(elementCopy, contactData, impliedRoleValue)
    contactParent.insert(contactIndex + 1, elementCopy)


def fixKeywordChars(keyword):
    """DataCite sometimes inserts '&gt;' instead of '>' for GCMD, so we fix this here."""
    fixedKeyword = keyword.replace('&gt;', '>')
    return fixedKeyword


def addKeywords(xml_root, keywordXPath, keywordList):
    """ Add GCMD Keyword elements, one element per list item, to the keyword section of the XML document. """
    keywordElement, keywordParent, originalIndex = xml.cutElement(xml_root, keywordXPath, True)
    if not keywordList:
        keywordSection = keywordParent.getparent()
        keywordSectionParent = keywordSection.getparent()
        keywordSectionParent.remove(keywordSection)
        return
    insertCounter = 0
    for keyword in keywordList:
        fixedKeyword = fixKeywordChars(keyword)
        elementCopy = xml.copyElement(keywordElement)
        xml.setElementValue(elementCopy, childXPaths['string'], fixedKeyword)
        keywordParent.insert(originalIndex + insertCounter, elementCopy)
        insertCounter += 1


def addRelatedLinks(xml_root, relatedLinkXPath, relatedLinks):
    """ Add related link XML elements using a list of related link records. """
    emptyLinkElement, parent, originalIndex = xml.cutElement(xml_root, relatedLinkXPath, True)
    insertCounter = 0
    for link in relatedLinks:
        elementCopy = xml.copyElement(emptyLinkElement)
        onlineResourceChild = xml.getFirstElement(elementCopy, childXPaths['relatedLink'])
        modifyOnlineResource(onlineResourceChild, link['linkage'], link['name'], link['description'])
        parent.insert(originalIndex + insertCounter, elementCopy)
        insertCounter += 1


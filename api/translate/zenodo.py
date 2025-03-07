import datetime

from api.util.xml import getElements, getFirstElement

Person_ISO_to_Zenodo = {
    'individualName': 'name',
    'organisationName' : 'affiliation',
    'roleCode': 'type'
}

RoleCode_ISO_to_Zenodo = {
    'resourceProvider': 'Distributor',
    'custodian': 'DataManager',
    'owner': 'RightsHolder',
    'user': 'Other',
    'distributor': 'Distributor',
    'originator': 'DataCollector',
    'pointOfContact': 'ContactPerson',
    'principalInvestigator': 'ProjectLeader',
    'processor': 'Other',
    'publisher': 'Producer',
}


parentXPaths = {
    'fileIdentifier'   : '/gmd:MD_Metadata/gmd:fileIdentifier/gco:CharacterString',
    'assetType'        : '/gmd:MD_Metadata/gmd:hierarchyLevel/gmd:MD_ScopeCode',
    'metadataContact'  : '/gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty',
    'landingPage'      : '/gmd:MD_Metadata/gmd:dataSetURI/gco:CharacterString',
    'title'            : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString',
    'publicationDate'  : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:date/gco:Date',
    'citedContact'     : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:citedResponsibleParty/gmd:CI_ResponsibleParty',
    'abstract'         : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:abstract/gco:CharacterString',
    'supportContact'   : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:pointOfContact',
    'legalConstraints' : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:useLimitation/gco:CharacterString',
    'accessConstraints': '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:otherConstraints/gco:CharacterString',
    'geographicExtent' : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox',
    'temporalExtent':    '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent',
}

childXPaths = {
    'individualName':      'gmd:individualName/gco:CharacterString',
    'organisationName':    'gmd:organisationName/gco:CharacterString',
    'position':        'gmd:positionName/gco:CharacterString',
    'email':           'gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:electronicMailAddress/gco:CharacterString',
    'keyword':         'gmd:keyword/gco:CharacterString',
    'roleCode':        'gmd:role/gmd:CI_RoleCode',
    'repTypeCode':     'gmd:MD_SpatialRepresentationTypeCode',
    'distance':        'gco:Distance',
    'real':            'gco:Real',
    'point':           'gml:pos',
    'string':          'gco:CharacterString',
    'stringURL':       'gco:CharacterString[starts-with(.,"http://") or starts-with(.,"https://")]',
    'linkage':         'gmd:linkage/gmd:URL',
    'name':            'gmd:name/gco:CharacterString',
    'description':     'gmd:description/gco:CharacterString',
    'extentBegin':     'gml:TimePeriod/gml:beginPosition',
    'extentEnd':       'gml:TimePeriod/gml:endPosition',
    'westLon':         'gmd:westBoundLongitude/gco:Decimal',
    'eastLon':         'gmd:eastBoundLongitude/gco:Decimal',
    'southLat':        'gmd:southBoundLatitude/gco:Decimal',
    'northLat':        'gmd:northBoundLatitude/gco:Decimal',
}

ISO_NAMESPACES = {'gmd': 'http://www.isotc211.org/2005/gmd',
                  'xlink': 'http://www.w3.org/1999/xlink',
                  'gco': 'http://www.isotc211.org/2005/gco',
                  'gml': 'http://www.opengis.net/gml'}

def get_spatial_locations(xml_tree):
    """
    Zenodo only supports a list of points for their spatial extent metadata.
    In contrast, Bounding box is the only spatial representation type supported by GDEX.
    Grab and return in a dictionary format supported by Zenodo.
    """
    locations = []
    geoExtents = getElements(xml_tree, parentXPaths['geographicExtent'])
    for geoExtent in geoExtents:
        westLon = getFirstElement(geoExtent, childXPaths['westLon']).text
        eastLon = getFirstElement(geoExtent, childXPaths['eastLon']).text
        southLat = getFirstElement(geoExtent, childXPaths['southLat']).text
        northLat = getFirstElement(geoExtent, childXPaths['northLat']).text
        if westLon == eastLon and southLat == northLat:
            location = {'lat': float(southLat), 'lon': float(westLon), 'place': 'Missing Name'}
            locations.append(location)
        else:
            print('    (skipping non-point geographic extent...)')

    return locations

def truncate_iso_date(dateString):
    """ Return an ISO date string without hours, minutes, seconds.
    """
    if 'T' in dateString:
        dateString = dateString.split('T')[0]
    return dateString

def get_temporal_extents(xml_tree):
    """
    Zenodo supports only ISO date strings, so replace any occurrence of "now" with today's date.
    """
    dates = []
    dateRanges = getElements(xml_tree, parentXPaths['temporalExtent'])
    for dateRange in dateRanges:
        rangeBegin = getFirstElement(dateRange, childXPaths['extentBegin']).text
        rangeEnd = getFirstElement(dateRange, childXPaths['extentEnd']).text
        if rangeBegin and rangeEnd:
            if rangeEnd.lower() == 'now':
                rangeEnd = datetime.datetime.now().isoformat()
            rangeBegin = truncate_iso_date(rangeBegin)
            rangeEnd = truncate_iso_date(rangeEnd)
            date = {'start': rangeBegin, 'end': rangeEnd, 'type': 'Valid'}
            dates.append(date)
    return dates


def getElementsMatchingRole(roleString, contactXPath, roleCodeXPath, xml_tree):
    """ Get all XML contact elements matching a specific role for the given contact XPath.
    """
    matchingContactElements = []
    contactElements = xml_tree.xpath(contactXPath, namespaces=ISO_NAMESPACES)

    for contactElement in contactElements:
        roleCodeElements = contactElement.xpath(roleCodeXPath, namespaces=ISO_NAMESPACES)

        if roleCodeElements and roleCodeElements[0].get('codeListValue') == roleString:
            matchingContactElements.append(contactElement)

    return matchingContactElements



def getRoleMatchesAsJson(roleString, contactXPath, roleCodeXPath, xml_tree):
    """
    Return a dictionary of creators/contributors matching a specific role found at the given contact XPath.
    """
    foundPeople = []

    matchingContactElements = getElementsMatchingRole(roleString, contactXPath, roleCodeXPath, xml_tree)

    # Map 'individualName' to 'name', 'organizationName to
    for contactElement in matchingContactElements:

        zenodo_person = {}
        for (iso_name, zen_name) in Person_ISO_to_Zenodo.items():

            # Zenodo creators have no role/type, so skip this case
            if roleString == 'author' and zen_name == 'type':
                continue
            childXPath = childXPaths[iso_name]
            foundText = contactElement.findtext(childXPath, namespaces=ISO_NAMESPACES)

            # For individual names, try transforming to "LastName, FirstName" format
            if zen_name == 'name' and get_lastname_firstname(foundText):
                foundText = get_lastname_firstname(foundText)
            zenodo_person[zen_name] = foundText
        foundPeople.append(zenodo_person)

    return foundPeople



def get_lastname_firstname(name_string):
    """
    This function takes a person's full name, and if it has one whitespace separating two words and no commas,
    e.g. "John Doe", it returns a modified version of name_string, of the form "Doe, John".

    If the name string does not have the form "word1 word2", the function returns None.
    """
    return_value = None
    words = name_string.split()
    no_comma = ',' not in name_string
    if len(words) == 2 and no_comma:
        return_value = "%s, %s" % (words[1], words[0])
    return return_value


def get_creators_as_json(xml_tree):
    """
    Searches an ISO XML element tree for authors and returns a JSON description of them according to Zenodo's
    'creator' metadata concept.
    """
    authorJson = getRoleMatchesAsJson('author', parentXPaths['citedContact'], childXPaths['roleCode'], xml_tree)
    return authorJson


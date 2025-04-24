import datetime

from api.util.xml import getElements, getFirstElement, getXMLTree, getElementText, ISO_NAMESPACES


Person_ISO_to_Zenodo = {
    'individualName': 'name',
    'individualAnchor': 'name',
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
    'keywords'         : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords',
    'title'            : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString',
    'publicationDate'  : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:date/gco:Date',
    'citedContact'     : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:citedResponsibleParty/gmd:CI_ResponsibleParty',
    'abstract'         : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:abstract/gco:CharacterString',
    'supportContact'   : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:pointOfContact/gmd:CI_ResponsibleParty',
    'legalConstraints' : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:useLimitation/gco:CharacterString',
    'accessConstraints': '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:otherConstraints/gco:CharacterString',
    'geographicExtent' : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox',
    'temporalExtent':    '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent',
    'spatialResolution': '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:spatialResolution/gmd:MD_Resolution/gmd:distance/gco:Distance',
}

childXPaths = {
    'individualName':      'gmd:individualName/gco:CharacterString',
    'individualAnchor':    'gmd:individualName/gmx:Anchor',
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

#
#  ISO File Metadata Mappings for Zenodo
#

METADATA_PATHS = {
    'title'            : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString',
    'description'      : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:abstract/gco:CharacterString',
}

def extract_metadata(iso_file):
    """ Parse ISO XML file and pull metadata for Zenodo upload.
    """
    metadata = {}
    xml_root = getXMLTree(iso_file)
    for (key, xpath) in METADATA_PATHS.items():
        value = getElementText(xpath, xml_root)
        metadata[key] = value

    # Add fields required by Zenodo
    authors_json = get_creators_as_json(xml_root)
    metadata['creators'] = authors_json
    metadata['upload_type'] = 'dataset'
    metadata['license'] = 'cc-by-4.0'

    # Add DOI if it exists already
    doi_string = get_DOI(xml_root)
    if doi_string:
        metadata['doi'] = doi_string

    # Add publication date
    date_string = get_publication_date(xml_root)
    if date_string:
        metadata['publication_date'] = date_string

    # Add dataset contributors
    contributors_json = get_contributors_as_json(xml_root)
    metadata['contributors'] = contributors_json

    # Add optional metadata if it exists
    (point_locations, location_notes) = get_spatial_info(xml_root)

    # If True, only the first point location is uploaded to Zenodo
    TRUNCATE_POINTS = True
    if point_locations and TRUNCATE_POINTS:
        point_locations = [point_locations[0]]
    if point_locations:
        metadata['locations'] = point_locations

    (date_ranges, temporal_notes) = get_temporal_info(xml_root)
    if date_ranges:
        metadata['dates'] = date_ranges

    resolution_notes = get_spatial_resolutions(xml_root)
    notes = location_notes + temporal_notes + resolution_notes
    if notes:
        metadata['notes'] = notes

    keywords = get_keywords(xml_root)
    if keywords:
        metadata['keywords'] = keywords

    return metadata


def get_keywords(xml_tree):
    """
    Extract and return a list of keywords from an ISO XML file.
    Make sure 'Dataset' is not in the list, as this is a special "resource type" keyword.
    """
    keywords = []
    elements = getElements(xml_tree, parentXPaths['keywords'])
    for element in elements:
        keyword = getElementText(childXPaths['keyword'], element)
        keywords.append(keyword)

    filtered_keywords = [keyword for keyword in keywords if keyword.lower() != 'dataset']
    return filtered_keywords




def get_spatial_info(xml_tree):
    """
    Zenodo only supports a list of points and descriptions for their spatial extent metadata.
    In contrast, Bounding box is the only spatial representation type supported by GDEX.
    Grab and return in a dictionary format supported by Zenodo.
    """
    locations = []
    notes = ''
    geoExtents = getElements(xml_tree, parentXPaths['geographicExtent'])
    for geoExtent in geoExtents:
        westLon = getFirstElement(geoExtent, childXPaths['westLon']).text
        eastLon = getFirstElement(geoExtent, childXPaths['eastLon']).text
        southLat = getFirstElement(geoExtent, childXPaths['southLat']).text
        northLat = getFirstElement(geoExtent, childXPaths['northLat']).text
        if westLon == eastLon and southLat == northLat:
            location = {'lat': float(southLat), 'lon': float(westLon), 'place': 'Missing Name'}
            locations.append(location)
        notes = notes + (f' Longitude West Boundary: {westLon}<br> Longitude East Boundary: {eastLon}<br>' +
                         f' Latitude South Boundary: {southLat}<br> Latitude North Boundary: {northLat}<br><br>')
    return locations, notes


def get_spatial_resolutions(xml_tree):
    """ Return a description of spatial resolutions in the XML tree """
    resolutions = ''
    resolution_elements = getElements(xml_tree, parentXPaths['spatialResolution'])
    for element in resolution_elements:
        resolution_value = element.text
        resolution_units = element.get('uom')
        resolutions = resolutions + f' Spatial Resolution: {resolution_value} {resolution_units}<br>'
    if resolutions:
        resolutions = resolutions + '<br>'
    return resolutions


def truncate_iso_date(dateString):
    """ Return an ISO date string without hours, minutes, seconds.
    """
    if 'T' in dateString:
        dateString = dateString.split('T')[0]
    return dateString

def get_temporal_info(xml_tree):
    """ Zenodo supports only ISO date strings, so replace any occurrence of "now" with today's date.
    """
    dates = []
    notes = ''
    dateRanges = getElements(xml_tree, parentXPaths['temporalExtent'])
    for dateRange in dateRanges:
        rangeBegin = getFirstElement(dateRange, childXPaths['extentBegin']).text
        rangeEnd = getFirstElement(dateRange, childXPaths['extentEnd']).text
        if rangeBegin and rangeEnd:
            notes = notes + (f' Temporal Range Start: {rangeBegin}<br>' +
                             f' Temporal Range End: {rangeEnd}<br><br>')
            if rangeEnd.lower() == 'now':
                rangeEnd = datetime.datetime.now().isoformat()
            rangeBegin = truncate_iso_date(rangeBegin)
            rangeEnd = truncate_iso_date(rangeEnd)
            date = {'start': rangeBegin, 'end': rangeEnd, 'type': 'Valid'}
            dates.append(date)
    return dates, notes


def getElementsMatchingRole(roleString, contactXPath, xml_tree):
    """ Get all XML contact elements matching a specific role for the given contact XPath.
    """
    matchingContactElements = []
    contactElements = xml_tree.xpath(contactXPath, namespaces=ISO_NAMESPACES)

    for contactElement in contactElements:
        roleCodeElements = contactElement.xpath(childXPaths['roleCode'], namespaces=ISO_NAMESPACES)

        if roleCodeElements and roleCodeElements[0].get('codeListValue') == roleString:
            matchingContactElements.append(contactElement)

    return matchingContactElements


def getRoleMatchesAsJson(roleString, contactXPath, xml_tree):
    """ Return a dictionary of creators/contributors matching a specific role found at the given contact XPath.
    """
    foundPeople = []
    matchingContactElements = getElementsMatchingRole(roleString, contactXPath, xml_tree)
    for contactElement in matchingContactElements:
        zenodo_person = {}
        for (iso_name, zen_name) in Person_ISO_to_Zenodo.items():

            # Zenodo creators have no role/type, so skip this case
            if roleString == 'author' and zen_name == 'type':
                continue
            childXPath = childXPaths[iso_name]
            foundText = contactElement.findtext(childXPath, namespaces=ISO_NAMESPACES)

            # Grab the ORCID value if it exists
            if iso_name == 'individualAnchor' and foundText:
                orcid_id = extract_orcid(contactElement)
                zenodo_person['orcid'] = orcid_id

            # For individual names, try transforming to "LastName, FirstName" format
            if zen_name == 'name' and foundText and get_lastname_firstname(foundText):
                foundText = get_lastname_firstname(foundText)
            if foundText:
                zenodo_person[zen_name] = foundText
        foundPeople.append(zenodo_person)

    return foundPeople


def extract_orcid(contactElement):
    """ Extract and return the ORCID identifier from a CitedContact element. """
    anchorElement = contactElement.xpath(childXPaths['individualAnchor'], namespaces=ISO_NAMESPACES)
    orcid_url = anchorElement[0].get('{http://www.w3.org/1999/xlink}href')
    orcid_id = orcid_url.split('/')[-1]
    return orcid_id


def get_lastname_firstname(name_string):
    """
    This function takes a person's full name, and if it has one whitespace separating two words and no commas,
    e.g. "John Doe", it returns a modified version of name_string, of the form "Doe, John".  If the full name
    has three words, no commas, and the middle word is in the form of a middle initial, e.g. "Jane L. Plain",
    then return "Plain, Jane L.".

    If the word string has a comma or otherwise does not match the above formats, the function returns None.
    """
    return_value = None
    words = name_string.split()
    no_comma = ',' not in name_string
    if no_comma and len(words) == 2 :
        return_value = f"{words[1]}, {words[0]}"
    elif no_comma and len(words) == 3 and is_middle_initial(words[1]):
        return_value = f"{words[2]}, {words[0]} {words[1]}"
    return return_value


def is_middle_initial(word_string):
    is_mi = len(word_string) == 2 and word_string[-1] == '.'
    return is_mi


def get_creators_as_json(xml_tree):
    """
    Searches an ISO XML element tree for authors and returns a JSON description of them according to Zenodo's
    'creator' metadata concept.
    """
    authorJson = getRoleMatchesAsJson('author', parentXPaths['citedContact'], xml_tree)
    return authorJson

def get_contributors_as_json(xml_tree):
    """
    Searches an ISO XML element tree for Resource Support Contact and Metadata Contact, and returns the first
    instances of each.
    """
    support_contact_json = getRoleMatchesAsJson('pointOfContact', parentXPaths['supportContact'], xml_tree)
    support_contact_json = support_contact_json[0]
    support_contact_json['type'] = 'ContactPerson'
    metadata_contact_json = getRoleMatchesAsJson('pointOfContact', parentXPaths['metadataContact'], xml_tree)
    metadata_contact_json = metadata_contact_json[0]
    metadata_contact_json['type'] = 'RelatedPerson'
    return [support_contact_json, metadata_contact_json]


def is_DOI(urlString):
    """  Returns True if urlString appears to be a DOI.  Otherwise, it returns False.
    """
    is_doi = False
    if urlString:
       if urlString.startswith('http://doi.org/') or urlString.startswith('https://doi.org/'):
          is_doi = True
    return is_doi

def get_DOI(xml_tree):
    """
    If required landing page is a DOI, return it as a string.  Otherwise, return None.
    """
    doi_string = None
    xpath = parentXPaths['landingPage']
    landing_page = getElementText(xpath, xml_tree)
    if is_DOI(landing_page):
        doi_string = landing_page
    return doi_string

def get_publication_date(xml_tree):
    """
    Extract ISO 8601 date and make sure timestamp is removed.
    """
    date_string = getElementText(parentXPaths['publicationDate'], xml_tree)
    if 'T' in date_string:
        date_string = date_string.split('T')[0]
    return date_string
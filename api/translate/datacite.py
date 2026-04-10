#import sys
from datetime import datetime

import api.util.xml as xml
import api.util.iso19139 as iso

roleMappingDataCiteToISO = {
    "Creator": "author",
    "Publisher": "publisher",
    "ContactPerson": "pointOfContact",  ## Any ContactPerson should be considered a Resource Support Contact
    "DataCollector": "contributor",
    "DataCurator": "custodian",
    "DataManager": "custodian",
    "Distributor": "distributor",
    "Editor": "editor",
    "Funder": "funder",
    "HostingInstitution": "resourceProvider",
    "Producer": "mediator",
    "ProjectLeader": "principalInvestigator",
    "ProjectManager": "collaborator",
    "ProjectMember": "contributor",
    "RegistrationAgency": "",
    "RegistrationAuthority": "",
    "RelatedPerson": "pointOfContact",  ##  Any RelatedPerson should be considered a Metadata Contact
    "Researcher": "contributor",
    "ResearchGroup": "collaborator",
    "RightsHolder": "rightsHolder",
    "Sponsor": "sponsor",
    "Supervisor": "",
    "WorkPackageLeader": "",
    "Other": "contributor",
}

parentXPaths = {
    'fileIdentifier': '/gmd:MD_Metadata/gmd:fileIdentifier/gco:CharacterString',
    'assetType': '/gmd:MD_Metadata/gmd:hierarchyLevel/gmd:MD_ScopeCode',
    'metadataContact': '/gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty',
    'metadataDate': '/gmd:MD_Metadata/gmd:dateStamp/gco:DateTime',
    'landingPage': '/gmd:MD_Metadata/gmd:dataSetURI/gco:CharacterString',
    'title': '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString',
    'publicationDate': '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:date/gco:Date',
    'citedContact': '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:citedResponsibleParty',
    'abstract': '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:abstract',
    'supportContact': '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:pointOfContact',
    'resourceType': '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:thesaurusName/gmd:CI_Citation/gmd:title/gco:CharacterString[contains(., "Resource Type")]/../../../../gmd:keyword/gco:CharacterString',
    'resourceFormat': '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceFormat',
    'keyword': '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:thesaurusName/gmd:CI_Citation/gmd:title/gco:CharacterString[contains(., "GCMD")]/../../../../gmd:keyword',
    'keywordCutElement': '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:thesaurusName/gmd:CI_Citation/gmd:title/gco:CharacterString[contains(., "GCMD")]/../../../../../../gmd:descriptiveKeywords',
    'relatedLink': '/gmd:MD_Metadata/gmd:metadataExtensionInfo',
    'legalConstraints': '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:useLimitation/gco:CharacterString',
    'accessConstraints': '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:otherConstraints/gco:CharacterString',
    'geoExtent': '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox',
    'geoExtentCutElement': '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:geographicElement',
    'temporalExtent': '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent',
    'temporalExtentCutElement': '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:temporalElement',
}


# def translateDataCiteRecords():
#     """ batch translate DataCite Records and save to output directory. """
#
#     # Get records
#     records = getDataCiteRecords()
#
#     print("##", file=sys.stderr)
#     print(("## Translating " + str(len(records)) + " Records..."), file=sys.stderr)
#     print("##", file=sys.stderr)
#
#     # Loop over DataCite Records
#     for record in records:
#         xmlOutput = translateDataCiteRecord(record)
#
#         # Isolate the second part of a DOI identifier for the output file name
#         uniqueID = recordID.split('/')[1]
#
#         outputFilePath = 'defaultOutputRecords/' + uniqueID + '.xml'
#         f = open(outputFilePath, 'w')
#         f.write(xmlOutput)
#         f.close()
#
#     print('...Finished Translating Records.', file=sys.stderr)


def translateDataCiteRecord(record, templateFile):
    """ Return ISO 19139 translation for a single DataCite record. """
    recordISO, recordID = transformDataCiteToISO(record, templateFile, roleMappingDataCiteToISO)

    headerXML = '<?xml version="1.0" encoding="UTF-8"?>\n'
    outputXML = headerXML + recordISO
    return outputXML


def transformDataCiteToISO(record, templateFileISO, roleMapping):
    # Load the ISO template file as an XML element tree
    root = xml.getXMLTree(templateFileISO)

    # Put DOI in fileIdentifier
    assert 'doi' in record
    xml.setElementValue(root, parentXPaths['fileIdentifier'], record['doi'])

    # Put current time in dateStamp
    currentTime = datetime.now().isoformat()
    xml.setElementValue(root, parentXPaths['metadataDate'], currentTime)

    # Put resourceTypeGeneral in hierarchyLevelName
    assert 'resourceTypeGeneral' in record['types']
    xml.setElementValue(root, parentXPaths['resourceType'], record['types']['resourceTypeGeneral'])

    # Put title in title
    assert 'title' in record['titles'][0]
    titleValue = record['titles'][0]['title']
    xml.setElementValue(root, parentXPaths['title'], titleValue)

    # Put description in abstract
    if 'description' in record['descriptions'][0]:
        fullXPath = parentXPaths['abstract'] + '/gco:CharacterString'
        descriptionValue = record['descriptions'][0]['description']
        xml.setElementValue(root, fullXPath, descriptionValue)
    else:
        xml.cutElement(parentXPaths['abstract'])

    # Put rights in legalConstraints
    if 'rightsList' in record and len(record['rightsList']) > 0:
        legalRightsText, accessRightsText = getRightsText(record['rightsList'])
        xml.setElementValue(root, parentXPaths['legalConstraints'], legalRightsText)
        xml.setElementValue(root, parentXPaths['accessConstraints'], accessRightsText)

    # Put publicationYear in CI_Citation/date
    xml.setElementValue(root, parentXPaths['publicationDate'], record["publicationYear"])

    # Make DOI URL the Landing Page
    url = "https://doi.org/" + record["doi"]
    xml.setElementValue(root, parentXPaths['landingPage'], url)

    # Add relatedIdentifier as online resource if it is a URL
    relatedIdentifierList = record.get("relatedIdentifiers", [])
    relatedURLs = [id['relatedIdentifier'] for id in relatedIdentifierList if id['relatedIdentifierType'] == 'URL']
    relatedLinks = []
    for url in relatedURLs:
        relatedLinks.append({"name": "Unknown URL title", "linkage": url, "description": "Unknown URL description"})
    iso.addRelatedLinks(root, parentXPaths['relatedLink'], relatedLinks)

    # Add "subject" keywords.  Fill existing element first, then create copies.   If no keywords are present, cut XML element.
    keywords = []
    if 'subjects' in record:
        keywords = [s['subject'] for s in record['subjects']]

    # Call this even if keywords are empty, so any unpopulated keyword XML elements are removed. 
    iso.addKeywords(root, parentXPaths['keyword'], keywords)

    formats = []
    if 'formats' in record:
        formats = record['formats']

    # Call this even if no formats exist, so the template XML element for resourceFormat is removed.
    createResourceFormats(formats, root)

    # Create list of cited contacts from three keys: "creators", "publisher", and "contributors".
    # Also obtain a list of support contacts from "contributors".
    citedContacts = getAuthors(record)

    if 'publisher' in record:
        publisherRecord = {"organization": record["publisher"], "role": "publisher"}
        citedContacts.append(publisherRecord)

    if ('contributors' in record):
        otherContacts, supportContacts, metadataContacts = splitContributors(record["contributors"], roleMapping)
        citedContacts.extend(otherContacts)
    else:
        supportContacts = []
        metadataContacts = []

    # Fill in cited contacts.
    createResponsibleParties(root, parentXPaths['citedContact'], citedContacts)

    # Fill in Resource Support contacts.
    createResponsibleParties(root, parentXPaths['supportContact'], supportContacts)

    # Fill in Metadata contacts.
    createResponsibleParties(root, parentXPaths['metadataContact'], metadataContacts)

    # Fill in geographical bounding box if provided. Otherwise, delete the empty XML element to keep the XML valid.
    if ('geoLocations' in record) and (len(record['geoLocations']) > 0) and (
            'geoLocationBox' in record['geoLocations'][0]):
        bbox = record['geoLocations'][0]['geoLocationBox']
        bbox_new = {'west': bbox['westBoundLongitude'],
                    'east': bbox['eastBoundLongitude'],
                    'north': bbox['northBoundLatitude'],
                    'south': bbox['southBoundLatitude']
                    }
        iso.modifyBoundingBox(root, parentXPaths['geoExtent'], bbox_new)
    else:
        xml.cutElement(root, parentXPaths['geoExtentCutElement'])

    # Fill in temporal extent if provided.  Otherwise, delete the empty XML element to keep the XML valid.
    temporalExtentExists = False
    if ('dates' in record) and (len(record['dates']) > 0):
        beginDate, endDate = getTemporalExtent(record['dates'])
        if beginDate or endDate:
            temporalExtentExists = True
            extentRecord = {'start': beginDate, 'end': endDate}
            iso.modifyTemporalExtent(root, parentXPaths['temporalExtent'], extentRecord)

    if not temporalExtentExists:
        xml.cutElement(root, parentXPaths['temporalExtentCutElement'])

    # Return ISO record and record identifier
    recordAsISO = xml.toString(root)
    return recordAsISO, record["doi"]


def getTemporalExtent(dates):
    """ Return the first set of dates marked as 'Collected', which means
        the dates represent a bounding temporal extent for some dataset. """
    beginDate = None
    endDate = None
    for dateDict in dates:
        if 'dateType' in dateDict and dateDict['dateType'] == 'Collected':
            beginDate = 'unknown'
            endDate = 'now'
            dateString = dateDict['date']
            extractedDates = dateString.split('/')
            if extractedDates[0]:
                beginDate = extractedDates[0]
            if extractedDates[1]:
                endDate = extractedDates[1]
            break
    return beginDate, endDate

def getRelatedIdentifierParts(relatedIdentifier):
    """ Return the parts of a DataCite relatedIdentifier object. """
    relatedIdentifierParts = relatedIdentifier.split(":")
    namePart = "Related Resource: " + relatedIdentifierParts[0]
    typePart = relatedIdentifierParts[1]
    urlPart = ':'.join(relatedIdentifierParts[2:])
    return namePart, typePart, urlPart


def getAuthors(record):
    """ Convert the list of creators into a list of author records. """
    creatorList = record["creators"]
    authorList = []
    for creator in creatorList:
        author = {"name": creator["name"], "role": 'author', "orcid_url": None}
        if creator['nameIdentifiers']:
            for identifier in creator['nameIdentifiers']:
                if identifier['nameIdentifier'] and 'orcid' in identifier['nameIdentifier']:
                    author['orcid_url'] = identifier['nameIdentifier']
        authorList.append(author)
    # sys.stderr.write('authorList : %s\n' % authorList)
    return authorList


def extractEmailFromDataciteName(name):
    """Detect if the contributor has an email address as part of the name.
       * If so, split the name into separate parts.
       * If not, return the original name and an empty string for the email.
    """
    nameSplitOnComma = name.split(',')
    hasOneComma = len(nameSplitOnComma) == 2
    hasAtSign = hasOneComma and len(nameSplitOnComma[1].split('@')) == 2
    if hasAtSign:
        name = nameSplitOnComma[0].strip()
        email = nameSplitOnComma[1].strip()
    else:
        email = ''
    return name, email


def splitContributors(contributorList, roleMapping):
    """ Split the contributors by type, since they are added to different parts of the XML tree. """
    # Remove contributors that do not have a contributorType.
    contributorsWithType = [contributor for contributor in contributorList if 'contributorType' in contributor]
    citedContacts = []
    supportContacts = []
    metadataContacts = []
    for contributor in contributorsWithType:
        # name = contributor['name']
        name, email = extractEmailFromDataciteName(contributor['name'])
        roleDatacite = contributor['contributorType']
        roleISO = roleMapping[roleDatacite]
        contactRecord = {"name": name, "role": roleISO, "email": email}
        if roleDatacite == 'RelatedPerson':
            metadataContacts.append(contactRecord)
        elif roleDatacite == 'ContactPerson':
            supportContacts.append(contactRecord)
        else:
            citedContacts.append(contactRecord)
    return citedContacts, supportContacts, metadataContacts


def getRightsText(rightsList):
    """Apply the following rules to determine whether a given rights element belongs in Access Constraints or Legal Constraints:
    
    1. First look for RightsURI. If it is there, it is a "Legal Constraints" concept.
    
    2. If (1) fails, look for "Legal Constraints" or "Access Constraints" in the description text to disambiguate.
    
    3. If (2) fails, process them in order, with "Legal Constraints" mapping to the first one found.
    """
    legalRightsText = ""
    accessRightsText = ""

    for rightsElement in rightsList:
        rightsText = rightsElement.get('rights', '')

        if 'rightsUri' in rightsElement and rightsElement['rightsUri']:
            legalRightsText += rightsText + ' (See also ' + rightsElement['rightsUri'] + ' )'
        elif 'Legal Constraints' in rightsText:
            legalRightsText += rightsText
        elif 'Access Constraints' in rightsText:
            accessRightsText += rightsText
        elif not legalRightsText:
            legalRightsText += rightsText
        else:
            accessRightsText += rightsText

    return legalRightsText, accessRightsText


def createResponsibleParties(root, contactXPath, contactList):
    """ Insert XML elements for a list of contact records. """
    contactTemplate, contactParent, contactIndex = xml.cutElement(root, contactXPath, True)
    insertCounter = 0
    for contactRecord in contactList:
        contactElement = xml.copyElement(contactTemplate)
        iso.modifyContactDataSelectively(contactElement, contactRecord)
        contactParent.insert(contactIndex + insertCounter, contactElement)
        insertCounter += 1


def createResourceFormats(formats, root):
    """
    Given a list of format strings and an XML tree, insert a ResourceFormat element for each format string.
    """
    emptyElement, parent, originalIndex = xml.cutElement(root, parentXPaths['resourceFormat'], True)
    indexCounter = 0
    for format in formats:
        elementCopy = xml.copyElement(emptyElement)
        xml.setElementValue(elementCopy, 'gmd:MD_Format/gmd:name/gco:CharacterString', format)
        # "version" entry is optional
        parent.insert(originalIndex + indexCounter, elementCopy)
        indexCounter += 1


import api.util.iso19139 as iso
import api.util.xml as xml

parentXPaths = {
     'relatedLink'         : '/gmd:MD_Metadata/gmd:metadataExtensionInfo',
     'alternateTitle'      : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:alternateTitle',
     'resourceVersion'     : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:edition',
     'progressCode'        : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:status/gmd:MD_ProgressCode',
     'resourceFormat'      : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceFormat',
     'softwareLanguage'    : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:environmentDescription/gco:CharacterString',
     'additionalInfo'      : '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:supplementalInformation',
     'distributor'         : '/gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributor',
     'distributionFormat'  : '/gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributionFormat',
     'assetSize'           : '/gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:transferOptions',
}


def transformOptionalFields(root, record):

    # //OPTIONAL FIELDS
    # - Related Link: repeatable
    if 'related_link' in record:
        emptyLinkElement, parent, originalIndex = xml.cutElement(root, parentXPaths['relatedLink'], True)
        indexCounter = 0
        for link in record['related_link']:
            elementCopy = xml.copyElement(emptyLinkElement)
            onlineResourceChild = xml.getElement(elementCopy, 'gmd:MD_MetadataExtensionInformation/gmd:extensionOnLineResource/gmd:CI_OnlineResource')
            name = link['name']
            url = link['linkage']
            description = link['description']
            iso.modifyOnlineResource(onlineResourceChild, url, name, description)
            parent.insert(originalIndex + indexCounter, elementCopy)
            indexCounter += 1
    else:
        xml.cutElement(root, parentXPaths['relatedLink'])

    # - Alternate Identifier: repeatable
    if 'alternate_identifier' in record:
        emptyElement, parent, originalIndex = xml.cutElement(root, parentXPaths['alternateTitle'], True)
        indexCounter = 0
        for title in record['alternate_identifier']:
            elementCopy = xml.copyElement(emptyElement)
            xml.setElementValue(elementCopy, 'gco:CharacterString', title)
            parent.insert(originalIndex + indexCounter, elementCopy)
            indexCounter += 1
    else:
        xml.cutElement(root, parentXPaths['alternateTitle'])

    # - Resource Version: not repeatable
    if 'resource_version' in record:
        versionElement = xml.getElement(root, parentXPaths['resourceVersion'])
        xml.setElementValue(versionElement, 'gco:CharacterString', record['resource_version'])
    else:
        xml.cutElement(root, parentXPaths['resourceVersion'])

    # - Progress: not repeatable
    if 'progress' in record:
        setProgressCode = True
        progressElement = xml.getElement(root, parentXPaths['progressCode'])
        xml.setTextOrMarkMissing(progressElement, record['progress'], setProgressCode)
    else:
        xml.cutElement(root, parentXPaths['resourceVersion'])

    # - Resource Format: repeatable
    if 'resource_format' in record:
        emptyElement, parent, originalIndex = xml.cutElement(root, parentXPaths['resourceFormat'], True)
        indexCounter = 0
        for format in record['resource_format']:
            elementCopy = xml.copyElement(emptyElement)
            xml.setElementValue(elementCopy, 'gmd:MD_Format/gmd:name/gco:CharacterString', format['name'])
            # "version" entry is optional
            xml.setElementValue(elementCopy, 'gmd:MD_Format/gmd:version/gco:CharacterString', format.get('version', []))
            parent.insert(originalIndex + indexCounter, elementCopy)
            indexCounter += 1
    else:
        xml.cutElement(root, parentXPaths['resourceFormat'])

    # - Software Implementation Language: not repeatable
    if 'software_implementation_language' in record:
        languageElement = xml.getElement(root, parentXPaths['softwareLanguage'])
        xml.setTextOrMarkMissing(languageElement, record['software_implementation_language'])
    else:
        xml.cutElement(root, parentXPaths['softwareLanguage'])

    # - Additional Information: not repeatable
    if 'additional_information' in record:
        informationElement = xml.getElement(root, parentXPaths['additionalInfo'])
        xml.setElementValue(informationElement, 'gco:CharacterString', record['additional_information'])
    else:
        xml.cutElement(root, parentXPaths['additionalInfo'])

    # - Distributor: not repeatable
    if 'distributor' in record:
        distributorElement = xml.getElement(root, parentXPaths['distributor'])
        contactElement = xml.getElement(distributorElement, 'gmd:MD_Distributor/gmd:distributorContact/gmd:CI_ResponsibleParty')
        iso.modifyContactData(contactElement, record['distributor'], 'distributor')
    else:
        xml.cutElement(root, parentXPaths['distributor'])

    # - Distribution Format: repeatable
    if 'distribution_format' in record:
        emptyElement, parent, originalIndex = xml.cutElement(root, parentXPaths['distributionFormat'], True)
        indexCounter = 0
        for format in record['distribution_format']:
            elementCopy = xml.copyElement(emptyElement)
            xml.setElementValue(elementCopy, 'gmd:MD_Format/gmd:name/gco:CharacterString', format)
            parent.insert(originalIndex + indexCounter, elementCopy)
            indexCounter += 1
    else:
        xml.cutElement(root, parentXPaths['distributionFormat'])

    # - Asset Size: not repeatable
    if 'asset_size_MB' in record:
        sizeElement = xml.getElement(root, parentXPaths['assetSize'])
        xml.setElementValue(sizeElement, 'gmd:MD_DigitalTransferOptions/gmd:transferSize/gco:Real', record['asset_size_MB'])
    else:
        xml.cutElement(root, parentXPaths['assetSize'])

    # - Author Identifier: currently not well defined for "old ISO".

    return root



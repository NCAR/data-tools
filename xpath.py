import argparse
import sys
import csv
from lxml import etree as ElementTree  # ISO XML parser

from utils.harvest_mappings import getStandardResourceFormat
from utils.name_parse import split_name_string

import os.path
from pathlib import Path

__version_info__ = ('2026', '04', '10')
__version__ = '-'.join(__version_info__)

PROGRAM_DESCRIPTION = '''
    A utility for reporting existence of xml elements, or extracting element values, from a file or directory of files.
    
    
Example usage:

       python xpath.py --type publisher   

Required arguments:
  
       --type  <type>               Type of XML element to examine.  Must be one of:
                                    ['publisher', 'author', 'resourceFormat', 'standardResourceFormat', 
                                     'geoExtent', 'timeExtent']

Optional arguments:

       --inputDir  <path_to_dir>    Path to directory with ISO XML files; full directory hierarchy will be examined.
       --file      <path_to_file>   Path to ISO XML file to examine
       --datasetsOnly               Only examine ISO XML files with Resource Type: Dataset
       --version                    Print this program version and exit 

 '''

x_paths = {"resourceType": ('/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:descriptiveKeywords' +
                            '/gmd:MD_Keywords/gmd:thesaurusName/gmd:CI_Citation/gmd:title/gco:CharacterString'),
           "geoExtent":    ('/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent' +
                            '/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox'),
           "timeExtent":   ('/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent' +
                            '/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent'),
           "resourceFormat": '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceFormat',
           "citedContact": ('/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation' +
                            '/gmd:CI_Citation/gmd:citedResponsibleParty/gmd:CI_ResponsibleParty')
           }

child_x_paths = {
    'individual': './/gmd:individualName',
    'individual_char': './/gmd:individualName/gco:CharacterString',
    'individual_anchor': './/gmd:individualName/gmx:Anchor',
    'organisation_char': 'gmd:organisationName/gco:CharacterString',
    'organisation_anchor': 'gmd:organisationName/gmx:Anchor',
    'roleCode': 'gmd:role/gmd:CI_RoleCode',
    'keyword': 'gmd:keyword/gco:CharacterString',
    'formatName': 'gmd:MD_Format/gmd:name/gco:CharacterString'
}

# We need XML namespace mappings in order to search the ISO element tree
ISO_NAMESPACES = {'gmd': 'http://www.isotc211.org/2005/gmd',
                  'xlink': 'http://www.w3.org/1999/xlink',
                  'gco': 'http://www.isotc211.org/2005/gco',
                  'gml': 'http://www.opengis.net/gml',
                  'gmx': 'http://www.isotc211.org/2005/gmx'}


def check_directory_existence(directory_path, directory_description):
    """ generate an error if directory does not exist. """
    if not os.path.isdir(directory_path):
        message = directory_description + ' does not exist: %s\n' % directory_path
        parser.error(message)


class PrintHelpOnErrorParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


#
# Tree-wide operations
#
def get_xml_tree(source):
    try:
        etree = ElementTree.parse(source)
        root = etree.getroot()
    except Exception:
        print(f"Unable to parse {source}")
        root = None
    return root


def get_elements_matching_role(roleString, contactXPath, roleCodeXPath, xml_tree):
    """ Get all XML contact elements matching a specific role for the given contact XPath.
    """
    matching_contact_elements = []
    contact_elements = xml_tree.xpath(contactXPath, namespaces=ISO_NAMESPACES)

    for contactElement in contact_elements:
        role_code_elements = contactElement.xpath(roleCodeXPath, namespaces=ISO_NAMESPACES)

        if role_code_elements and role_code_elements[0].get('codeListValue') == roleString:
            matching_contact_elements.append(contactElement)

    return matching_contact_elements


def get_first_child_text_for_role(role_string, contact_x_path, child_x_path, role_code_x_path, xml_tree):
    """ Get child string from the first matching role found at the given contact XPath.
    """
    found_text_value = ''

    matching_contact_elements = get_elements_matching_role(role_string, contact_x_path, role_code_x_path, xml_tree)

    if matching_contact_elements:
        found_text = matching_contact_elements[0].findtext(child_x_path, namespaces=ISO_NAMESPACES)

        if found_text:
            found_text_value = found_text

    return found_text_value


def print_author(file, csv_writer, check_non_datasets=True):
    cited_contact = x_paths['citedContact']
    elements_to_search = [child_x_paths['individual_char'], child_x_paths['individual_anchor'],
                          child_x_paths['organisation_char'], child_x_paths['organisation_anchor']]
    tree = get_xml_tree(file)

    # Return early if this file is not parsed, or it is not a dataset and checkNonDatasets is False.
    not_parsed = tree is None
    skip_non_dataset = (not check_non_datasets) and (not is_dataset_record(tree))
    if not_parsed or skip_non_dataset:
        return

    author_elements = get_elements_matching_role('author', cited_contact, child_x_paths['roleCode'], tree)
    for author_element in author_elements:
        found_text = None
        for element in elements_to_search:
            name_element = author_element.xpath(element, namespaces=ISO_NAMESPACES)
            if name_element and name_element[0].text:
                found_text = name_element[0].text
                word_length = len(found_text.split())
                first_name, last_name = split_name_string(found_text)
                if first_name and ((len(first_name) == 1) or ('.' in first_name)):
                    middle_initial = True
                else:
                    middle_initial = False
                # Flag certain cases for Impacts
                flag = middle_initial and ('Anchor' not in element)
                data = {'name': found_text, 'element': element, 'word length': word_length,
                        'middle initial': middle_initial, 'flag': flag}
                csv_writer.writerow(data)
                break
        if not found_text:
            print(f"Warning: author string not found in contact element in {file}")


def print_publisher(file, check_non_datasets=True):
    cited_contact = x_paths['citedContact']
    elements_to_search = [child_x_paths['individual_char'], child_x_paths['individual_anchor'],
                          child_x_paths['organisation_char'], child_x_paths['organisation_anchor']]
    publisher_text = []

    tree = get_xml_tree(file)

    # Return early if this file is not parsed, or it is not a dataset and checkNonDatasets is False.
    not_parsed = tree is None
    skip_non_dataset = (not check_non_datasets) and (not is_dataset_record(tree))
    if not_parsed or skip_non_dataset:
        return

    for element in elements_to_search:
        publisher_text = get_first_child_text_for_role('publisher', cited_contact, element, child_x_paths['roleCode'], tree)
        if publisher_text:
            print(str(publisher_text), file=sys.stdout)
            break
    if len(publisher_text) == 0:
        print(f"Warning: publisher string not found for {file}")


def get_child_text_list(parent_x_path, child_x_path, xml_tree):
    """ Loop over children of a parent XPath and return the text associated with all child elements.
        If no children are found or no child element has text, return the empty list.
    """
    child_text_list = []
    parent_elements = xml_tree.xpath(parent_x_path, namespaces=ISO_NAMESPACES)

    for parentElement in parent_elements:
        child_elements = parentElement.xpath(child_x_path, namespaces=ISO_NAMESPACES)

        for childElement in child_elements:
            if childElement.text:
                child_text_list.append(childElement.text)

    return child_text_list


def print_resource_formats(file_path, check_non_datasets, use_format_mapping):
    tree = get_xml_tree(file_path)

    # Return early if this file is not XML, or we are ignoring non-dataset records and this is a non-dataset record.
    is_iso_file = tree is not None
    skip_file = not is_iso_file or not (check_non_datasets or is_dataset_record(tree))
    if not skip_file:
        formats = get_child_text_list(x_paths["resourceFormat"], child_x_paths["formatName"], tree)
        for fmt in formats:
            if use_format_mapping:
                standard_format_name = getStandardResourceFormat(fmt)
                print(f"{standard_format_name} | {fmt}", file=sys.stdout)
            else:
                print(fmt, file=sys.stdout)
        # Indicate that the file is missing format information
        if not formats:
            print(f"UNDEFINED FORMAT in {file_path}", file=sys.stdout)



def get_datacite_resource_type(thesaurus_x_path, keyword_x_path, xml_tree):
    """ Get the first resource type keyword by searching thesaurus titles containing "Resource Type".
        Strip whitespace and return lowercase version of string.
    """
    resource_type = ''
    for thesaurus in xml_tree.xpath(thesaurus_x_path, namespaces=ISO_NAMESPACES):
        if "Resource Type" in thesaurus.text:
            keywordElement = thesaurus.getparent().getparent().getparent().getparent()

            for keyword in keywordElement.xpath(keyword_x_path, namespaces=ISO_NAMESPACES):
                if keyword.text:
                    resource_type = keyword.text.strip().lower()
                    # Substitute ambiguous keywords with more understandable versions.
                    if resource_type == 'text':
                        resource_type = 'publication'

                    # Return the first match found.
                    return resource_type

    return resource_type


def is_dataset_record(tree):
    resource_type = get_datacite_resource_type(x_paths["resourceType"], child_x_paths["keyword"], tree)
    return resource_type.lower() == 'dataset'


def print_xpath_exists(file, xpath_list, check_non_datasets=True):
    tree = get_xml_tree(file)
    is_iso_record = tree is not None
    is_dataset = is_iso_record and is_dataset_record(tree)

    if not is_iso_record:
        message = "not_a_iso_record"
    elif not (is_dataset or check_non_datasets):
        message = "not_a_dataset_record"
    elif is_dataset or check_non_datasets:
        exists = True
        for xpath in xpath_list:
            xml_element = tree.xpath(xpath, namespaces=ISO_NAMESPACES)
            if not xml_element:
                exists = False
        if exists:
            message = "xpath_exists"
        else:
            message = "xpath_missing"
    else:
        # If this statement is reached, there is a logic error.
        assert False

    # print out the XML file name as a something that could be stripped off later.
    print(f'{message}  {file}', file=sys.stdout)


#
#  Parse and validate command line options.
#
program_help = PROGRAM_DESCRIPTION + __version__
parser = PrintHelpOnErrorParser(description=program_help, formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('--inputDir', nargs=1, help="base dir for XML files")
parser.add_argument('--file', nargs=1, help="XML file to search")
parser.add_argument('--datasetsOnly', action='store_true', help="Limit output to records with resource type 'Dataset'")
parser.add_argument('--version', action='version', version="%(prog)s (" + __version__ + ")")

requiredArgs = parser.add_argument_group('required arguments')
typeChoices = ['author', 'publisher', 'resourceFormat', 'standardResourceFormat', 'geoExtent', 'timeExtent']
requiredArgs.add_argument('--type', nargs=1, required=True, choices=typeChoices, help=f"Type of XML element")

args = parser.parse_args()


###
### START OF MAIN PROGRAM
###

def perform_operation(file, csv_writer):
    """ Chooses which action to perform based on command-line options.
    """
    # Decide whether to limit output to dataset records only
    check_non_datasets = not args.datasetsOnly

    if args.type[0] == 'publisher':
        print_publisher(file, check_non_datasets)
    elif args.type[0] == 'author':
        print_author(file, csv_writer, check_non_datasets)
    elif args.type[0] == 'resourceFormat':
        print_resource_formats(file, check_non_datasets, use_format_mapping=False)
    elif args.type[0] == 'standardResourceFormat':
        print_resource_formats(file, check_non_datasets, use_format_mapping=True)
    elif args.type[0] == 'geoExtent':
        print_xpath_exists(file, [x_paths['geoExtent']], check_non_datasets)         # check geographical extent existence
    elif args.type[0] == 'timeExtent':
        print_xpath_exists(file, [x_paths['timeExtent']], check_non_datasets)      # check temporal extent existence

    # printXPathExists(file, [xpaths['resourceFormat']], checkNonDatasets)  # check resource format existence
    # check spatio-temporal extent existence
    #printXPathExists(file, [xpaths['timeExtent'], xpaths['geoExtent']], checkNonDatasets)


# readSTDIN = (args.inputDir == None)
# if readSTDIN:
#     tree = getXMLTree(sys.stdin)


csvfile=None
csv_writer = None
if args.type[0] == 'author':
    filename = 'author.csv'
    if args.file is not None:
        filename = args.file[0].split('/')[-1]
    elif args.inputDir[0] is not None:
        filename = args.inputDir[0].split('/')[-1]
    fields = ['name', 'element', 'word length', 'middle initial', 'flag']
    csvfile = open(filename + '.csv', 'w', newline='')
    csv_writer = csv.DictWriter(csvfile, fieldnames=fields)
    csv_writer.writeheader()

readFile = (args.file is not None)
if readFile:
    perform_operation(args.file[0], csv_writer)
else:
    check_directory_existence(args.inputDir[0], 'Input directory')
    for path in Path(args.inputDir[0]).rglob('*.xml'):
        perform_operation(path.as_posix(), csv_writer)

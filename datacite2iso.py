#
# Python program for translating DataCite metadata to ISO 19139.
#

import argparse
import sys
import os.path

import api.inputjson as input_json
import api.translate.datacite as translate

__version_info__ = ('2026', '04', '10')
__version__ = '-'.join(__version_info__)

PROGRAM_DESCRIPTION = '''

A program for translating DataCite JSON metadata into ISO 19139 metadata.

DataCite metadata is obtained from the DataCite website, so an internet connection is required.

Example usage:

       python datacite2iso.py --doi 10.5065/D6WD3XH5   > test_datacite.xml

Required arguments:
  
       --doi            DOI code to translate

Optional arguments:

       --template       Custom ISO template to use from the 'templates' folder.  Default: datacite.xml 

Program Version: '''


class PrintHelpOnErrorParser(argparse.ArgumentParser):
    def error(self, error_message):
        sys.stderr.write('error: %s\n' % error_message)
        self.print_help()
        sys.exit(2)


#
#  Parse the command line options.
#
programHelp = PROGRAM_DESCRIPTION + __version__
parser = PrintHelpOnErrorParser(description=programHelp, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("--template", nargs=1, help="custom ISO template to use from the 'templates' folder.  Default: datacite.xml")
parser.add_argument('--version', action='version', version="%(prog)s (" + __version__ + ")")

requiredArgs = parser.add_argument_group('required arguments')
requiredArgs.add_argument("--doi", nargs=1, required=True, help="Digital Object Identifier (DOI)")

args = parser.parse_args()

# Check for ISO 19139 template existence.
DEFAULT_OUTPUT_TEMPLATE = 'datacite.xml'

templateFilePath = input_json.getTemplateFilePath(args.template, DEFAULT_OUTPUT_TEMPLATE)
if not os.path.isfile(templateFilePath):
    message = 'Template file does not exist: %s\n' % templateFilePath
    parser.error(message)

# Query the specified DOI's metadata JSON record.
doi = args.doi[0]
record = input_json.getDataCiteRecords(doi)

#
#  Perform the translation.
#
if len(record) > 0:
    output = translate.translateDataCiteRecord(record, templateFilePath)
    print(output, file=sys.stdout)
else:
    print(("DOI " + doi + " was not found.\n"), file=sys.stderr)

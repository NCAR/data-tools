import sys

import requests
import argparse
import os
import json

from api.translate.zenodo import extract_metadata


PROGRAM_DESCRIPTION = '''

A program for uploading files to Zenodo.  

An API token for Zenodo is required.  Before running the program, set the API token value as follows:

 export ZENODO_TOKEN='<my_token>'
 
Also required is a path to a folder with files to upload.  All files in the folder and its sub-folders 
will be uploaded.  If the upload folder contains spaces, then surround the path in single quotes.

Example usage:

       python zenodo_create.py --folder <local_folder_with_files>

Optional arguments:

       --iso_file <iso_file_path>    Extract and upload metadata from ISO XML file. 
       --resume <resume_file_path>   Resume uploading to a recently created dataset using an automatically generated 
                                     resume file; default location is /tmp/resume_upload_<dataset_id>.json .
       --publish                     After upload, publish the dataset.
       --test                        Upload to Zenodo's sandbox server instead; requires a sandbox API token.
       --version                     Print the program version and exit.
       --help                        Print the program description and exit.

Tested with python 3.8.

Program Version: '''

__version_info__ = ('2025', '03', '20')
__version__ = '-'.join(__version_info__)


#
#  Parse the command line options.
#

programHelp = PROGRAM_DESCRIPTION + __version__
parser = argparse.ArgumentParser(description=programHelp)
parser.add_argument("--test", help="Upload to Zenodo Sandbox server", action='store_const', const=True)
parser.add_argument("--publish", help="Publish dataset after upload", action='store_const', const=True)
parser.add_argument("--resume_file", nargs=1, help="Resume uploading using dataset resume file", default=['None'])
parser.add_argument("--iso_file", nargs=1, help="Path to ISO XML Metadata file", default=['None'])
parser.add_argument('--version', action='version', version="%(prog)s (" + __version__ + ")")

requiredArgs = parser.add_argument_group('required arguments')
requiredArgs.add_argument("--folder", nargs=1, required=True, help="File Upload Folder")

args = parser.parse_args()

upload_folder = args.folder[0]
iso_file = args.iso_file[0]
resume_file = args.resume_file[0]
TEST_UPLOAD = args.test
PUBLISH = args.publish

# Check validity of upload folder path, resume file path, iso_file path
assert(os.path.isdir(upload_folder))

if resume_file != 'None':
    assert (os.path.isfile(resume_file))

metadata = {}
if iso_file != 'None':
    assert(os.path.isfile(iso_file))
    metadata = extract_metadata(iso_file)
    # Provide verbose feedback on the command line
    metadata_pretty = json.dumps(metadata, indent=4)
    print(f'metadata = {metadata_pretty}')


if TEST_UPLOAD:
    upload_url = 'https://sandbox.zenodo.org/api/deposit/depositions'
else:
    upload_url = 'https://zenodo.org/api/deposit/depositions'

#
# Get the environment variable 'ZENODO_TOKEN'
#

api_token = os.environ.get('ZENODO_TOKEN')
params = {'access_token': api_token}
headers = {"Content-Type": "application/json"}

print(f'upload_url == {upload_url}')
print(f'TEST_UPLOAD == {TEST_UPLOAD}')
print(f'resume_file == {resume_file}')
print(f'api_token == "{api_token}"')
print(f'upload_folder == "{upload_folder}"\n\n')

#
#  Get the file paths for upload.
#

upload_folder = os.path.abspath(upload_folder)
file_info = []
print(f'Files to upload in {upload_folder}:')

for root, subdirs, files in os.walk(upload_folder):
    for file_name in files:
        # Ignore hidden files always
        if file_name.startswith('.'):
            print(f'    (skipping hidden file {file_name} ...)')
            continue
        print(f'    {file_name}')
        file_path = os.path.join(root, file_name)
        file_info.append((file_name, file_path))

# Verify that all filenames are unique
file_names = [file_name for (file_name, file_path) in file_info]
if len(file_names) != len(set(file_names)):
    print('\n  ERROR: file names are not unique.  Aborting...', file=sys.stderr)
    exit(2)


#
#  Create a new dataset on Zenodo if no resume file is provided.
#
if resume_file == 'None':
    r = requests.post(upload_url, params=params, json={}, headers=headers)

    # Exit if status code is not success.
    if r.status_code != 201:
        print(r.json())
        exit(r.status_code)

    dataset_id = r.json()["id"]
    bucket_url = r.json()["links"]["bucket"]
    resume_upload_data = {'dataset_id': dataset_id, 'bucket_url': bucket_url}

    # Save upload ids to a 'resume file'
    resume_file_folder = '/tmp'
    resume_file_name = f'resume_upload_{dataset_id}.json'
    resume_file = f'{resume_file_folder}/{resume_file_name}'
    with open(resume_file, "w") as f:
        json.dump(resume_upload_data, f, indent=4)
else:
    # Grab upload parameters from a previous upload attempt
    with open(resume_file, 'r') as openfile:
        resume_data = json.load(openfile)
        dataset_id = resume_data['dataset_id']
        bucket_url = resume_data['bucket_url']


print(f'\n\n  "UPLOAD RESUME" CONFIGURATION FILE = {resume_file}\n\n')

#
#  Upload files.
#
for (file_name, file_path) in file_info:
    with open(file_path, "rb") as fp:
        r = requests.put(
            "%s/%s" % (bucket_url, file_name),
            data=fp,
            params=params,
        )
        try:
            checksum = r.json()['checksum']
            size =  r.json()['size']
            print(f'{file_name}: checksum= {checksum}, size= {size}')
        except KeyError:
            print(r.json())
            exit(r.status_code)

#
# Upload metadata if there is any.
#
if metadata:
    print('\n Uploading metadata...\n')
    upload_metadata = {'metadata': metadata}
    r = requests.put('%s/%s' % (upload_url, dataset_id),
                     params=params, data=json.dumps(upload_metadata),
                     headers=headers)
    if r.status_code != 200:
        print(r.json())
        exit(r.status_code)


if PUBLISH:
    r = requests.post(upload_url + '/%s/actions/publish' % dataset_id, params=params)
    print(f'\nPublish status code: {r.status_code}')



print(f'\n...DONE\n')

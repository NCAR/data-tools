# data-tools:  Installation Instructions


## Prerequisites 

You must be on a machine with python installed, where the "virtualenv" or "conda" command is available.  One of these commands is needed to create a python environment where you can install several python library dependencies.  If either of the following commands returns a path, then you are set:

     which conda
     which python3


### Linux

#### Using conda 

If conda is already available, you can skip to the "Download and Install" section.

#### Using pip

If the "conda" command is not available on your Linux system, then creating python environments can be accomplished through the python command, version 3, provided the correct system packages are installed: 

     sudo yum list | grep python3-virtualenv
     
If no packages match, then the system package install command

     sudo yum install python3-virtualenv.noarch

should provide the ability to create a python virtual environment.

You may also need to install the system packages 'libxml2-devel' and 'libxslt-devel' if they are not already installed:

     sudo dnf install libxml2-devel libxslt-devel

Then you can test the ability to create and manage a python development environment with these commands:

     python3 -venv <my_python_envs_directory>/pythondev     # Create
     source ~/pythondev/bin/activate                        # Activate
     deactivate                                             # Deactivate
     \rm -rf <my_python_envs_directory>/pythondev           # Remove
     
   

### Mac OSX

For Mac OSX, the ability to create python virtual environments is not available by default.   If you wish to run on Mac OSX, you have two main courses of action: 

*  Install XCode, and the "homebrew" package manager (somewhat painful to install and manage) 

OR

*  Install Anaconda (much less painful to install and manage).  

Anaconda can be downloaded here:   

https://www.anaconda.com/download/#macos

You should choose to download Python 3 DMG installer.

Once Anaconda is installed, you can continue with the instructions for downloading and installing the software.
     

## Download and Install Software in your User Space

* Navigate in your browser to https://github.com/NCAR/dset-JSON-to-ISO19139 and click the green "Code" button.   Clone the repository or download the zip file.   The zip file may be named "dset-JSON-to-ISO19139-main.zip" or something similar.
* Decide where you want the software to reside in your user space.  You should not need administrative privileges to install.   You only need read/write privileges in the folder where you want the software to reside.  We will call the target directory `<install_directory>`.
* Activate the conda or pip-based environment:

If you are using conda, type:

    INSTALL_CMD='conda env create -f ./environment.yml'

If you are using pip, type:

    INSTALL_CMD='pip install -r ./requirements.txt'
    
    # Create the python virtual environment
    python3 -m venv <my_python_envs_directory>/pythondev
    
    # You may want to alias the next command for activating your virtual environment:
    source <my_python_envs_directory>/pythondev/bin/activate

* Install the software in your python environment:
  
If you cloned the repo, type these commands:

     mv <cloned-repo> <install_directory>
     cd <install_directory>
     cd data-tools
     $INSTALL_CMD

If you downloaded the zip file, type these commands:

     mv <zip_file> <install_directory>
     cd <install_directory>
     unzip <zip_file>
     cd data-tools-main
     $INSTALL_CMD

If the final install command completes without errors, the scripts should be ready to use.   To test that your installation works correctly, the following command should run without producing errors: 

     python dset2iso.py  < defaultInputRecords/test_dset_full.txt  > test_dset_full.xml

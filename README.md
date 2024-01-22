# EIC_extraction-integration-plotting_LCMS_data
This code allows you to extract ion chromatograms from HRMS data, integrate peaks and plot the data by sample type and by timestamp.
Written by Chris Pook, drchrispook@gmail.com

This code is written in Python to be compiled using PyInstaller to create an executable file for use by those with no mass spec experience.
The code is designed to be run on a folder of Thermo .raw LC-MS datafiles. It requires an xlsx to be present in the same folder with a specific name. That is the name of the folder with "_TARGETS.xlsx" appended. The xlsx needs to contain columns called name, mz, mins, width, distance and prominence. The script will automatically load this file and use the data in each row to extract an EIC from.

Each Thermo .raw file will first be converted to an /mzML file using the msconvert command line tool from ProteoWizard. You will need this tool installed on your PC in order for this code to run. You can download and install the OpenMS package, which includes the msconvert tool, from https://openms.readthedocs.io/en/latest/openms-applications-and-tools/installation.html

Dependencies
In order to compile this script to a Windows exceutable .exe. file you will need to install several Python libraries upon which it depends:
pyinstaller
pandas
pyopenms
peakutils
plotly

As well as several functions of the more common 'core' libraries:
scipy.signal
numpy.arange
etc.




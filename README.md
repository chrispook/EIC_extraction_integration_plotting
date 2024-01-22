# EIC_extraction-integration-plotting_LCMS_data
This code allows you to extract ion chromatograms from HRMS data, integrate peaks and plot the data by sample type and by timestamp.
Written by Chris Pook, drchrispook@gmail.com
This code is released under a GNU3 license - https://www.gnu.org/licenses/gpl-3.0.en.html#license-text

This code is written in Python and designed to be compiled using PyInstaller to create an executable file for use by those with no mass spec experience.
The executable needs to be copied to a folder of Thermo .raw LC-MS datafiles. It requires an xlsx to be present in the same folder with a specific name. That is the name of the folder with "_TARGETS.xlsx" appended. The xlsx needs to contain columns called name, mz, mins, window, width, distance and prominence. The script will automatically load this file and use the data in each row to extract an EIC from. The first four values are specific to your analysis, 'window' being the RT delta within which EIC data will be extracted. The last three are parameters for the scipy.signal.find_peaks() function - https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html#scipy.signal.find_peaks
Values for these three are analysis-specific but suggested starting values are width = 12, distance = 50 and prominence = 60,000. 

Each Thermo .raw file will first be converted to an /mzML file using the msconvert command line tool from ProteoWizard. You will need this tool installed on your PC in order for this code to run. You can download ProteoWizard here - https://proteowizard.sourceforge.io/download.html
Alternatively, you can download and install the OpenMS package, which includes the msconvert tool - https://openms.readthedocs.io/en/latest/openms-applications-and-tools/installation.html

Dependencies
In order to compile this script to a Windows exceutable .exe file you will need to install a recent version of Python and several libraries upon which it depends:
pyinstaller
pandas
pyopenms
peakutils
plotly

As well as several functions of the more common 'core' libraries:
scipy.signal
numpy.arange
etc.

I built the version I'm currently using with Python 3.9. PyInstaller is rather particular and I had to install it in its own Python 3.9 environment using Anaconda and then add all the dependencies manually before PyInstaller would produce a bug-free executable.

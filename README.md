# EIC_extraction-integration-plotting_LCMS_data
This code allows you to extract ion chromatograms from HRMS data, integrate peaks and plot the data by sample type and by timestamp.
Written by Chris Pook, drchrispook@gmail.com
This code is released under a GNU3 license - [https://www.gnu.org/licenses/gpl-3.0.en.html#license-text](https://github.com/chrispook/EIC_extraction-integration-plotting_LCMS_data/blob/main/LICENSE)

This code is written in Python and designed to be compiled using PyInstaller to create an executable file for use by those with no mass spec experience.
The executable needs to be copied to a folder of Thermo .raw LC-MS datafiles. It requires an xlsx to be present in the same folder with a specific name. That is the name of the folder with "_TARGETS.xlsx" appended. The xlsx needs to contain columns called name, mz, mins, window, ppm, width, distance and prominence. The script will automatically load this file and use the data in each row to extract an EIC from. The first six values are specific to your analysis, 'window' being the RT delta from the retention time given in 'mins' and 'ppm' being the ppm delta from the given m/z within which EIC data will be extracted. The value for 'smoothing' is the width of the moving average window. The last three are parameters for the scipy.signal.find_peaks() function - https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html#scipy.signal.find_peaks
Values for the _TARGETS.xlsx file are analysis-specific but suggested starting values used for the Q-Exactive are: 
window:	0.4, ppm:	6, smoothing:	11, , width:	12, distance:	50, prominence:	50000

Each Thermo .raw file will first be converted to an /mzML file using the msconvert command line tool from ProteoWizard. You will need this tool installed on your PC in order for this code to run. You can download ProteoWizard here - https://proteowizard.sourceforge.io/download.html
Alternatively, you can download and install the OpenMS package, which includes the msconvert tool - https://openms.readthedocs.io/en/latest/openms-applications-and-tools/installation.html
One caveat necessary to make this code compile and run is that you may have to set the path to the OpenMS shared resources folder in the Python code in line 11, which currently reads: 
os.environ["OPENMS_DATA_PATH"] = r'C:\Program Files\OpenMS-2.6.0\share\OpenMS'
This is hopefully the only variable that is likely to need customisation from the user.

Once EIC data has been extracted and the file creation timestamp scraped from the Windows file metadata, the peaks in each EIC will be identified using a combination of peak_utils.indexes(), scipy.signal.find_peaks_cwt() and scipy.signal.find_peaks() and integrated. Files will be assigned to one of several classes based on my own file naming conventions: a file name containing the string '_BL' will be considered a blank, '_QC' is a QC, any file name containing the string 'prime' will be set to that class and any file name containing the string 'sst' in any combination of upper or lower case will be considered a System Suitability Test (SSTs are part of our daily/batchwise quality assurance procedure). All other files will be considered samples. The EICs, the peak areas by class, and time series plots of the peak areas and RTs will be visualised using plotly and exported to interactive .html files in a new folder created in the main analysis folder. The peak areas and other metrics for each feature will be tabulated and exported to an xlsx in the new folder using pandas and xlsxwriter. 

Dependencies
In order to compile this script to a Windows exceutable .exe file you will need to install a recent version of Python and several libraries upon which it depends:
pyinstaller
pyopenms
peakutils
plotly
xlsxwriter
tqdm
pytz


As well as several functions of the more common 'core' libraries:
pandas
scipy.signal
numpy.arange
datetime
glob
math
time

I built the version I'm currently using with Python 3.9. PyInstaller is rather particular and I had to install it in its own Python 3.9 environment using Anaconda and then add all the dependencies manually to that environment before PyInstaller would produce a bug-free executable.

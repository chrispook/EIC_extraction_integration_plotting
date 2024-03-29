# EIC_extraction-integration-plotting [EEIP]
This code allows you to extract ion chromatograms from HRMS data, integrate peaks and plot the data by sample type and by timestamp.
Written by Chris Pook, drchrispook@gmail.com
This code is released under a GNU3 license - [https://www.gnu.org/licenses/gpl-3.0.en.html#license-text](https://github.com/chrispook/EIC_extraction-integration-plotting_LCMS_data/blob/main/LICENSE)

This code is written in Python and designed to be compiled using PyInstaller to create an executable file for use by those with no mass spec experience.
The executable needs to be copied to a folder of Thermo .raw LC-MS datafiles. It requires an xlsx to be present in the same folder with a specific name. That is the name of the folder with "_TARGETS.xlsx" appended. An example file - example_TARGETS.xlsx - is available in the repository. The xlsx needs to contain columns called name, mz, mins, window, ppm, width, distance and prominence. The script will automatically load this file and use the data in each row to extract an EIC from. The first six values are specific to your analysis, 'window' being the RT delta from the retention time given in 'mins' and 'ppm' being the ppm delta from the given m/z within which EIC data will be extracted. The value for 'smoothing' is the width of the moving average window. The last three are parameters for the scipy.signal.find_peaks() function - https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html#scipy.signal.find_peaks

Values for the _TARGETS.xlsx file are analysis-specific but suggested starting values used for the Q-Exactive are: 
window:	0.4, ppm:	6, smoothing:	11, , width:	12, distance:	50, prominence:	50000

Each Thermo .raw file will first be converted to an .mzML file using the msconvert command line tool from ProteoWizard. You will need this tool installed on your PC in order for this code to run. You can download ProteoWizard here - https://proteowizard.sourceforge.io/download.html

Alternatively, you can download and install the OpenMS package, which includes the msconvert tool - https://openms.readthedocs.io/en/latest/openms-applications-and-tools/installation.html

One caveat necessary to make this code compile and run is that you may have to set the path to the OpenMS shared resources folder in the Python code in line 11, which currently reads: 
os.environ["OPENMS_DATA_PATH"] = r'C:\Program Files\OpenMS-2.6.0\share\OpenMS'
This is hopefully the only variable that is likely to need customisation from the user.

Once EIC data has been extracted and the file creation timestamp scraped from the Windows file metadata, the peaks in each EIC will be identified using a combination of peak_utils.indexes(), scipy.signal.find_peaks_cwt() and scipy.signal.find_peaks() and integrated. Files will be assigned to one of several classes based on basic analytical file naming conventions: a file name containing the case-sensitive string '_BL' will be considered a blank. Likewise, '_QC' is a QC, any file name containing the string 'prime' in upper or lower case will be set to that class. Any file name containing the string 'SST' in any combination of upper or lower case will be considered a System Suitability Test (SSTs are part of our daily/batchwise quality assurance procedure). All other files will be considered samples. 

The EICs, the peak areas by class, and time series plots of the peak areas and RTs will be visualised using plotly and exported to interactive .html files in a new folder created in the main analysis folder. The peak areas and other metrics for each feature will be tabulated and exported to an xlsx in the new folder using pandas and xlsxwriter. 

Here's a screenshot of the plot output for phenylalanine in a series of primes, SSTs, blanks and QCs from a batch of polar metabolomics analysis. Hovering over dots in the time series plots reveals contextual information. You can click and drag to zoom in any plot. Clicking on the coloured traces in the legend hides and shows the trace. Double clicking on one hides all but that one. Double click anywhere in any plot to reset or just reload the page. I have had some issues with axis labels in plotly so they aren't yet included. 
![freindly](https://github.com/chrispook/EIC_extraction-integration-plotting_LCMS_data/assets/51006923/218a8a63-d5c9-4b98-ba8a-9d9076a77189)

Here's a screenshot of the xlsx output. I've autosized the columns. 
![excel](https://github.com/chrispook/EIC_extraction-integration-plotting_LCMS_data/assets/51006923/6042d14c-98ac-4993-8555-05e1607c5956)


# Python Dependencies

In order to compile this script to a Windows exceutable .exe file you will need to install a recent version of Python and several libraries upon which it depends:
pyinstaller
pyopenms
peakutils
plotly
xlsxwriter
tqdm
pytz


You will also need working versions of the more common 'core' libraries:
pandas
scipy
numpy
datetime
glob
math
time

I built the version I'm currently using with Python 3.9. PyInstaller is rather particular and I had to install it in its own Python 3.9 environment using Anaconda and then add all the dependencies manually to that environment before PyInstaller would produce a bug-free executable. The first time you run an executable that you've just built you should run it from the command line, otherwise you won't be able to see debugging output. 


# TTD

Future developments include:
- labelling axes
- making the code vendor-agnostic
- improving integration
- making prebuilt executables available

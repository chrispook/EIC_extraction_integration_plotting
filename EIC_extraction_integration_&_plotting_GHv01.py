''' EIC_extraction-integration-plotting [EEIP]
This code allows you to extract ion chromatograms from HRMS data, integrate peaks and plot the data by sample type and by timestamp.
Written by Chris Pook, drchrispook@gmail.com
This code is released under a GNU3 license - https://www.gnu.org/licenses/gpl-3.0.en.html#license-text

https://github.com/chrispook/EIC_extraction-integration-plotting_LCMS_data
'''

from pyopenms import MSExperiment,MzMLFile
import os,glob,pytz
os.environ["OPENMS_DATA_PATH"] = r'C:\Program Files\OpenMS-2.6.0\share\OpenMS'
import pandas as pd
from time import sleep
import plotly.graph_objects as go
import pandas as pd
import plotly.offline as offline
from scipy import signal
import peakutils
from datetime import datetime
from plotly.subplots import make_subplots
from numpy import arange

folder = os.getcwd() # folder path 
print('folder: ', folder)
analysis_name = os.path.split(folder)[1]
print('analysis_name: ', analysis_name)
ef = analysis_name + '_TARGETS.xlsx' # path to xlsx describing features to quant. Must have columns for name, quant m/z, mins, window, ppm, width, distance
plot_folder = folder + r'\EEIP_output'
outfile = plot_folder + r'\\' + analysis_name + '_EEIP_results.xlsx' # xlsx output file name
print('ef: ', ef)

raw_files = glob.glob('*.raw') # get files
files = [x.replace('.raw', '') for x in raw_files]

classes = {} # dict of file names and their class
for ii in files:
    if 'prime' in ii.lower(): classes[ii] = 'prime'
    elif '_BL' in ii: classes[ii] = 'blank'
    elif '_QC' in ii: classes[ii] = 'QC'
    elif 'sst' in ii.lower(): classes[ii] = 'SST'
    else: classes[ii] = 'sample'
    
timestamp = {} # dict of timestamps for each file
    
efdf = pd.read_excel(ef, index_col = 'name', sheet_name = 'targets') # get features xlsx
names = efdf.index.values
EICs = [] # list of dfs to hold data for each EIC

for ff in files:  # iterate through mzML files
    if not os.path.exists(ff + '.mzML'): # if the mzml doesn't exist convert it
        print('converting ', ff, ' to .mzML')
        command = 'msconvert ' + folder + r'\\' + ff + '.raw ' + folder + r'\\' + ff + '.mzML'
        print(command)
        os.system(command)
    
    # scrape Xcalibur timestamps
    tz = pytz.timezone('NZ')
    unix = os.path.getmtime(ff + '.raw')
    timestamp[ff] = datetime.fromtimestamp(unix, tz).isoformat() # add to the dictionary
    
    dic_list = []
    inp = MSExperiment()
    MzMLFile().load(ff + '.mzML', inp)
    for tt,rr in efdf.iterrows():
        mzz = rr['mz']
        RTT = rr['mins']
        ppm = rr['ppm']
        RT_start = (RTT - rr['window']) *60 # these number need to be in seconds
        RT_end = (RTT + rr['window']) *60
        mz_start = -1
        mz_end = -1
        if mzz <150:  # low m/z can't be windowed using ppm !!!
            mz_start = mzz - 0.01
            mz_end = mzz + 0.01
        else:
            mz_start = (1- (ppm /1000000)) *mzz
            mz_end = (1+ (ppm /1000000)) *mzz
        # print(mzz, RTT, RT_start, RT_end, mz_start, mz_end)
        for s in inp: # strip out the EIC data
            if s.getMSLevel() == 1 and s.getRT() >RT_start and s.getRT() <RT_end:  # ignore MS2 data and scans outside the RT window
                filtered_mz = []
                filtered_int = []
                for mz, intensity in zip(*s.get_peaks()):
                    if mz_start < mz < mz_end:
                        filtered_mz.append(mz)
                        filtered_int.append(intensity)
                dic_list.append({'file':ff, 'name':tt, 'secs':s.getRT(), 'mins':s.getRT() /60, 'RT':RTT, 'mz':mzz, 'ppm':ppm, 'intensity':sum(filtered_int)})
    EIC = pd.DataFrame(dic_list)
    EICs.append(EIC)
eicdf = pd.concat(EICs)

classes = {}
for ii in files:
    if 'prime' in ii.lower(): classes[ii] = 'prime'
    elif '_BL' in ii: classes[ii] = 'blank'
    elif '_QC' in ii: classes[ii] = 'QC'
    elif '_SST' in ii: classes[ii] = 'SST'
    else: classes[ii] = 'sample'

    # plot each target & integrate
plot_folder = folder + r'\EEIP_output'
if not os.path.exists(plot_folder): os.makedirs(plot_folder)

peak_tups = [] # list of integration results as tuple of peak_df and name

for tt,rr in efdf.iterrows():
    fig = make_subplots(rows=2, cols=2) # four traces
    peak_list = []
    tsub = eicdf[eicdf['name'] == tt]

    for nn,aa in enumerate(files):
        # filter by the file and the RT window
        sub = tsub[tsub['file'] == aa]

        smooth = list(sub['intensity'].rolling(rr['smoothing'], min_periods=3, center=True).mean()) # rolling average smoothing
        smooth = [x - min(smooth) for x in smooth] # zero adjust

        # add the chromatogram traces
        fig.add_trace(go.Scatter(x= sub['mins'], y = smooth, mode='lines', name = aa), row=1, col=1) #top right trace

        # integrate the peaks and add peak markers and annotations
        peaks, props = signal.find_peaks(smooth, width= rr['width'], prominence = rr['prominence'], distance= rr['distance'])
        widths = signal.peak_widths(smooth, peaks, rel_height=1.0)
        cwt = signal.find_peaks_cwt(smooth, widths= arange(1,50)) # note difference between width and widths
        peak_indices = peakutils.indexes(smooth, thres= 0.1)
        
        real_peaks = [] # filter peaks by peak_indices to exclude peaks that weren't captured by both algorithms
        for ppp in peaks:
            keep = 0
            for pi in peak_indices:
                if ppp in [pi +x for x in arange(-4,4)]: keep = keep +1
            for wave in cwt:
                if ppp in [wave +x for x in arange(-13,13)]: keep = keep +1
            if keep >1: real_peaks.append(ppp)           
        print(peaks, cwt, peak_indices)
        
        if len(real_peaks) >0:    # integration
            for uu,pp in enumerate(peaks):
                if pp not in real_peaks: continue # skip peaks that peak_utils didn't find 
                area = 0
                for ii in range(props['left_bases'][uu], props['right_bases'][uu]): area += smooth[ii]
                area = int(area)
                peak_list.append({'file':aa, 'class':classes[aa], 'timestamp': timestamp[aa], 'name':tt, 'n':uu+1, 'RT':list(sub['mins'])[peaks[uu]], 'intensity':smooth[peaks[uu]], 'area':area, 
                                  'left base':list(sub['mins'])[props['left_bases'][uu]], 'right base':list(sub['mins'])[props['right_bases'][uu]], 'width':widths[0][uu], 'peak':(uu, pp)})

                fig.add_trace(go.Scatter(x= [list(sub['mins'])[peaks[uu]]], 
                                     y = [smooth[peaks[uu]]],
                                     mode='markers', 
                                     text = aa + ' - peak ' + str(uu+1) + ', RT: ' + str(list(sub['mins'])[peaks[uu]]) + ', area: ' + str(area),
                                         showlegend=False),
                             row=1, col=1) # added to multiplot
                             
    peak_list = pd.DataFrame(peak_list)
    if len(peak_list) == 0: 
        print('no peaks found for ', tt, ' in any file!')
        continue

    fig.add_trace(go.Box(y=peak_list['area'], x = peak_list['class'], name= tt, boxpoints='all', marker_color = '#3D9970', text = peak_list['file'],
                                hovertemplate = "file: %{text} <br>timestamp: %{x} </br> peak area: %{y}"), row=1, col=2) #top left trace
    fig.add_trace(go.Scatter(y=peak_list['area'], x = peak_list['timestamp'], mode = 'markers', marker = dict(color = 'blue'), text = peak_list['file'],
                                hovertemplate = "file: %{text} <br>timestamp: %{x} </br> peak area: %{y}",
                            ), row=2, col=1) #bottom left trace
    fig.add_trace(go.Scatter(y=peak_list['RT'], x = peak_list['timestamp'], mode = 'markers', marker = dict(color = 'black'), text = peak_list['file'],
                                hovertemplate = "file: %{text} <br>timestamp: %{x} </br> retention time (mins): %{y}",
                            ), row=2, col=2) #bottom right trace

    fig.update_layout(autosize= True, showlegend=True, title= tt + ' - m/z: ' + str(round(rr['mz'],4)) + ', RT: ' + str(round(rr['mins'],2)) + ' mins')
    fig.write_html(plot_folder + r'\EEIP_output-' + tt + '.html')
    sleep(0.2)
    peak_tups.append((peak_list, tt))

fdf = pd.read_excel(ef, index_col='name') # export
with pd.ExcelWriter(outfile, engine="xlsxwriter") as writer:
    fdf.to_excel(writer, sheet_name = 'features')
    for ii in peak_tups: ii[0].to_excel(writer, sheet_name = ii[1], index=False)

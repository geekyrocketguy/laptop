import numpy as np
import matplotlib.pyplot as plt
import re
import pdb
import glob
from datetime import datetime

dir = r'jsons_2026-08'

def main(save=False, month_select='2026-12'):
    
    #get list of campsites
    files = glob.glob(dir+'/*'+month_select +'*.json')
    campsites = np.zeros(len(files)).astype('str')
    #times = np.zeros(len(files)).astype('str') #not used, defined later
    for i in range(len(files)):
        files[i] = files[i].replace(dir, '').replace('.json', '').replace('\\', '').replace('2026', ';').replace('2027', ';')
        campsites[i] = files[i].split(';')[0].strip()

    campsites = np.unique(campsites)
#Return here. Make different plot for each month?

    #get times at which each campsite was scraped
    for j in range(len(campsites)):
        #iterate over each campsite
        files = glob.glob(dir+'/'+campsites[j]+'*'+month_select +'*.json')
        times = np.zeros(len(files)).astype('str')
        for i in range(len(files)):
            #files[i] = files[i].replace(dir, '').replace('.json', '').replace('\\', '').replace('2026', ';').replace('2027', ';')
            #pdb.set_trace()
            times[i] = files[i].replace('.json', '').split()[-1]

        #convert times to seconds
        times_secs = np.zeros(len(times))
        #pdb.set_trace()
        for i in range(len(times)):
            times_secs[i] = float(times[i][:2]) * 60*60 + \
                            float(times[i][2:4]) * 60 + float(times[i][4:])
        times_secs -= 7*60*60 #make them relative to 7 AM
        time_labels = np.zeros(len(times_secs)).astype(str)
        for i in range(len(times_secs)):
            if np.abs(times_secs[i]) < 60:
                time_labels[i] = str(np.around(times_secs[i], 1)) + " sec"
            else:
                time_labels[i] = str(np.around(times_secs[i]/60, 1)) + " min"
        
        for i in range(len(files)):
            #open files and extract info
            with open(files[i], 'r') as f:
                raw = f.read()

            junk = raw.split('{')
            junk = junk[3].split('}')[0]
            junk = junk.replace("'", '').replace('"', '')
            #junk = junk.split(',')
            junk = re.split(r'[:,]+', junk) #split with multiple delimiters
            dates = junk[::2] #array of dates
            availability = [x=='true' for x in junk[1::2]] #array of true/false availabilities
        
            if i==0:
                avail_matrix = np.zeros((len(dates), len(times)))
            pdb.set_trace()
            avail_matrix[:,i] = availability
            
        #format date labels
        date_labels = np.zeros(len(dates)).astype('str')
        for k in range(len(date_labels)):
            date_labels[k] = datetime.strptime(dates[k], "%Y-%m-%d").strftime('%a %b %d')
        
        #if ax is None:
        plt.figure(figsize=(18,8))
        ax = plt.gca()

        im = ax.imshow(avail_matrix)

        # Show all ticks and label them with the respective list entries
        ax.set_xticks(range(len(times_secs)))
        ax.set_xticklabels(time_labels, rotation=45, ha="right", rotation_mode="anchor")
        ax.set_yticks(range(len(date_labels)))
        ax.set_yticklabels(date_labels)
        ax.spines[:].set_visible(False) # Turn spines off and create white grid.
        
        ax.set_xticks(np.arange(avail_matrix.shape[1]+1)-.5, minor=True)
        ax.set_yticks(np.arange(avail_matrix.shape[0]+1)-.5, minor=True)
        ax.grid(which="minor", color="w", linestyle='-', linewidth=1)
        ax.tick_params(which="minor", bottom=False, left=False)
        # Correctly set the visibility of all spines
        #for spine in ax.spines.values():
        #    spine.set_visible(False)

        #create legend
        ax.plot(np.nan, np.nan, 's', color='#440154', label="not available")
        ax.plot(np.nan, np.nan, 's', color='#fde724', label="available")
        ax.legend(loc='upper right')

        mytitle=campsites[j] + " Campsite Availability, " + datetime.strptime(dates[0], "%Y-%m-%d").strftime('%B %Y')
        plt.title(mytitle)
        plt.xlabel("Time since sites released (8 AM MST)")
        plt.tight_layout()
        
        if save:
            plt.savefig(dir.replace('jsons', 'plots') + '/' + mytitle + '.png')
            print("Saved " + dir.replace('jsons', 'plots') + '/' + mytitle + '.png')
            plt.close('all')
        else:
            plt.show()
        
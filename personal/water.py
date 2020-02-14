import numpy as np
import matplotlib.pyplot as plt
import pdb
import datetime
import matplotlib.dates as mdates
import matplotlib.units as munits
converter = mdates.ConciseDateConverter()
munits.registry[np.datetime64] = converter
munits.registry[datetime.date] = converter
munits.registry[datetime.datetime] = converter

def main():
    alldates = np.loadtxt('water_20year.txt', skiprows=32, dtype=str, usecols=2)
    allflows = np.loadtxt('water_20year.txt', skiprows=32, dtype=float, usecols=5)
    print('done reading')
    
    avgflows = np.zeros(len(np.unique(alldates)))
    dates = np.zeros(len(avgflows)).astype(str)
    index = 0
    print("averaging each day's flows")
    for date in np.unique(alldates):
        loc = np.where(alldates == date)
        #if 693668 in loc: pdb.set_trace()
        avgflows[index] = np.median(allflows[loc])
        dates[index] = date
        index += 1
    print('done')
    
    doy = np.zeros(365).astype(str)
    for i in range(len(doy)):
        doy[i] = dates[i][5:]
    
    print('populating flow grid')
    flow_grid = np.zeros((365, 20))
    for i in range(np.shape(flow_grid)[1]):
        year = str(i)
        if len(year)==1: year='0'+year
        loc = np.squeeze(np.where(dates == '20'+year+'-01-02')) #jan 1 is missing in one year
        if np.size(loc) != 1: continue
        #pdb.set_trace()
        flow_grid[:,i] = avgflows[loc-1 : loc+364]
     
    mymed = np.zeros(365)
    mymean = np.zeros(365)
    for i in range(365):
        mymed[i] = np.median(flow_grid[i,:][flow_grid[i,:] != 0])
        mymean[i] = np.mean(flow_grid[i,:][flow_grid[i,:] != 0])
    pdb.set_trace()
    
    base = datetime.datetime(2010, 1, 1)
    dates = np.array([base + datetime.timedelta(days=i) for i in range(365)])
    
    fig, ax = plt.subplots(figsize=(8,6))
    lims = [np.datetime64('2010-01-01'), np.datetime64('2010-12-31')]
    
    ax.plot(dates, mymed, label='median')    
    ax.plot(dates, mymean, label='mean')    
    ax.set_xlim(lims)   

    #plt.legend()
    #ax.set_xlabel('day of year')
    #ax.set_ylabel('flow rate')
    
    
    #ax.set_xlim(lims)
        
    plt.show()
    
    pdb.set_trace()
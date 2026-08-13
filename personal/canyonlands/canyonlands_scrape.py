from urllib.request import urlopen
import numpy as np
import pdb
import time
import datetime
import os

#declare important stuff
t_start = datetime.datetime(2026, 8, 10, 7).timestamp() #Time of permit release. year, month, day, hour, [min, sec] converted to seconds in epoch. 
t_in_sec = [-60, -5, 60, 120, 60*60] #seconds, define refresh rates and times
t_refresh = [10,  0,  10, 60] #seconds, define refresh rates and times

month = '2' #what month of campsites to scrape? MUST NOT HAVE LEADING 0
year = '2027' #what year of campsites to scrape?


url_base = "https://www.recreation.gov/api/permititinerary/4675315/division/4675315" #applies to all campgrounds

'''
#Maze
campsite_nums = (np.arange(20)+31).astype(str) #31-50
campsite_names = ["Doll House 1", "Doll House 2", "Doll House 3", "Chimney Rock", "The Wall", "Standing Rock", \
                "Maze Overlook 1", "Maze Overlook 2", "Golden Stairs", "Teapot Rock", "Sunset Pass", "The Neck", \
                "Happy Canyon", "North Point", "Panorama Point", "Cleopatra's Chair", "High Spur", "Millard Canyon", \
                "Ekker Butte", "Flint Seep"]
'''
#White Rim Road
campsite_nums = (np.arange(20)+11).astype(str) #11-30
campsite_names = ["Shafer Campsite", "Airport A", "Airport B", "Airport C", "Airport D", "Gooseberry A", "Gooseberry B", \
                    "White Crack", "Murphy A", "Murphy B", "Murphy C", "Candlestick", "Potato Bottom A", "Potato Bottom B", \
                    "Potato Bottom C", "Hardscrabble A", "Hardscrabble B", "Labyrinth A", "Labyrinth B", "Taylor"]

data_dir = 'jsons_'+ datetime.datetime.now().strftime("%Y-%m-%d")

def get_jsons():
    
    os.makedirs(data_dir, exist_ok=True) # Create the directory if it does not exist
    
    now=time.time() #seconds since 1950 or whatever the default epoch is
    while now < t_start + np.min(t_in_sec): #if we're before the first data save window
        if round(now) % 10 == 0:
            print("Code will start in " + str(int(np.around((t_start + np.min(t_in_sec) - now) / 60, 1))) + " minutes.")
            time.sleep(1) #sleep a second so this doesn't print again for a minute
        
        time.sleep(0.1)
        now=time.time()
        
    for i in range(len(t_in_sec)-1):
        print(str(t_in_sec[i]) + " seconds since the start time. The interval time is " + str(np.around(t_refresh[i], 2)) + " seconds.")
        
        while time.time() < t_start + t_in_sec[i+1]:
            t1 = time.time()
            for j in range(len(campsite_nums)):
                url = url_base + campsite_nums[j] + "/availability/month?month=" + month + "&year=" + year
                #complete URL: https://www.recreation.gov/api/permititinerary/4675315/division/467531531/availability/month?month=11&year=2025
                
                try:
                    page = urlopen(url, timeout=2)
                    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H%M%S.%f")
                    pagecontents = str(page.read())
                    
                    filename = data_dir + '/' + campsite_names[j] + ' ' + year + '-' + month + ' ' + now_str + ".json"
                    #np.savetxt(filename, pagecontents)
                    with open(filename, 'w') as output:
                        output.write(pagecontents)
                except:
                    print("Failed to retrieve data for " + campsite_names[j])
            t2 = time.time()
            
            if t2 - t1 < t_refresh[i]: #if we haven't already spent the entire interval downloading files
                #if sleeping the remainder of the refresh period won't overrun the change in t_in_sec
                if  t2 + t_refresh[i] < t_start + t_in_sec[i+1]:
                    sleepduration = t_refresh[i] - (t2 - t1)
                else: #there's less than t_refresh[i] remaining before we need to change to the next t_in_sec
                    sleepduration = t_in_sec[i+1] - (t2 - t_start)
                print("   Will save data again in: " + str(np.around(sleepduration, 1)) + " seconds.")
                time.sleep(sleepduration)

    print("Done.")
import numpy as np
import ephem
from datetime import datetime
import pylunar
from geographiclib.geodesic import Geodesic
import pdb

######################################
'''
This code calculates when moonbows or rainbows are possible.
It works by comparing the alt/az of the observer looking at the scene (e.g.
a waterfall) to the alt/az of the moon/sun. If they are 
41.5 +/- (angular size of mist cloud) degrees apart, a rain/moonbow is possible.
This code just considers angles. Obviously there needs to be direct sun/moonlight
on the mist cloud and there needs to be mist for the rain/moonbow to occur. It
does not check for things (e.g. mountains) casting shadows onto the subject.

The user must input the following information in the top of the code:
 - lat/lon/alt of observer (degrees, meters)
 - lat/lon/alt of target (degrees, meters)
 ^these two are used for calculating alt/az between the two
 - size of mist cloud. If the cloud is 10 degrees wide, mist_radius=5.
 - timezone offset between the local time and UTC, including daylight savings. PST: -7 during the summer.
 
Call the code from inside python with:
>> import moonbows
>> moonbows.main(year, month, day) 
year, month, day, should be numbers, e.g. 
>> moonbows.main(2018, 5, 3)
If you would like to calculate daytime rainbows instead of nighttime moonbows, do something like
>> moonbows.main(2018, 5, 3, body='sun')

If you get an error like "ModuleNotFoundError: No module named 'ephem'", you need to install packages.
>> pip install ephem
>> pip install pylunar
etc
'''
######################################

#THE USER SHOULD SET observer, target, mist_radius, and timezone_offset

observer = np.array([37.73036 , -119.57362, 7208./3.281]) #lat lon alt of glacier point
#observer = np.array([37.7441 , -119.5913, 3965./3.281]) #lat lon alt of meadow lookout with view of Lower YF
#observer = np.array([37.754496 , -119.60288, 7238./3.281]) #lat lon alt of Eagle Peak lookout rock, averaged from many actual GPS points
#observer = np.array([37.74993 , -119.59575, 3965./3.281]) #lat lon alt of Lower YF Bridge

#target = np.array([37.75139, -119.59742, 4212/3.281]) #lat lon alt of lower yosemite falls
#target = np.array([37.75473, -119.5982, 5080/3.281]) #lat lon alt of upper yosemite falls
target = np.array([37.75554, -119.59804, 5132/3.281]) #lat lon alt of upper yosemite falls
#target = np.array([37.75530, -119.59729, 5033/3.281]) #lat lon alt of stream just below upper yosemite falls

#mist_radius = 2. #half of diameter of mist cloud, degrees. 2 = Glacier Point value.
#mist_radius = 6. #half of diameter of mist cloud, degrees. for viewing from meadow
mist_radius = 10. #half of diameter of mist cloud, degrees. for viewing from Eagle Peak Lookout
#mist_radius = 15. #half of diameter of mist cloud, degrees. for viewing from Lower Yosemite Falls Bridge

timezone_offset = -7 #hours, daylight saving during summer, UTC+time_offset = PST 


#year, month, day should be numbers, e.g. 2018, 4, 15
#body='sun' gives rainbows instead of moonbows. Default is moonbows.
def main(year, month, day, body='moon'):
    
    #find alt-az between observer and waterfall
    lib = Geodesic.WGS84.Inverse(observer[0], observer[1], target[0], target[1])
    az_obs_targ = np.radians(lib['azi1']) #azimuth in radians. Geodesic returns degrees
    if az_obs_targ < 0: az_obs_targ += 2*np.pi #no negative azimuths
    d = lib['s12'] #distance
    alt_obs_targ = np.arctan2(target[2] - observer[2], d) #altitude of target as viewed by observer, radians
    
    print("The distance, elevation, az, alt from observer to the waterfall is: " + \
        str(int(round(d))) + ' m, ' + str(int(round(target[2]-observer[2]))) + ' m, ', \
        str(round(np.degrees(az_obs_targ), 1)) + '°, ' + str(round(np.degrees(alt_obs_targ), 1)) + '°.')
    print()
  
    #initialize dates and ephemeris parameters
    date_pst = ephem.Date(str(year)+'/'+str(month)+'/'+str(day)+ ' 0:00') #midnight local time on date
    date_utc = ephem.date(date_pst - timezone_offset * ephem.hour) #UTC of midnight local time

    me = ephem.Observer()
    me.lon = str(observer[1])
    me.lat = str(observer[0])
    me.elevation = observer[2]
    me.temp = 5 #deg C
    me.pressure = 12.2 / 14.7 * 1000 #mbar
    me.date = ephem.date(date_utc)
    
    #get sunrise/sunset/moonrise/moonset times
    sun = ephem.Sun()
    sunrise = me.next_rising(sun)
    sunset = me.next_setting(sun)
    moon = ephem.Moon()
    moonrise = me.next_rising(moon)
    moonset = me.next_setting(moon)
    
    print("On " + str(datetime.strftime(date_pst.datetime(), '%a %b %d %Y')) + \
        ", sunrise occurs at " + str(datetime.strftime(ephem.date(sunrise+timezone_offset* ephem.hour).datetime(), '%X')) + \
        " and sunset occurs at " + str(datetime.strftime(ephem.date(sunset+timezone_offset* ephem.hour).datetime(), '%X'))+' local time.')
    print("Moonrise occurs at " + str(datetime.strftime(ephem.date(moonrise+timezone_offset* ephem.hour).datetime(), '%X')) + \
        " and moonset occurs at " + str(datetime.strftime(ephem.date(moonset+timezone_offset* ephem.hour).datetime(), '%X'))+' local time.')
    print()
    
    #initialize moon object to get the phase later
    mi = pylunar.MoonInfo([round(observer[0]), round((observer[0] - np.floor(observer[0]))*60.), 0], \
                          [round(observer[1]), round((observer[1] - np.floor(observer[1]))*60.), 0] ) 
    
    #initize booleans to guide later code flow
    moonbow_occurring = False
    moonbow_occurred = False
    
    #Now do a for loop over each minute in the 24 hours of the date given to see if/when moonbows occur
    for time_offset in np.arange(0, 24*60, 1):
        me.date = ephem.date(date_utc + time_offset * ephem.minute)
        
        if (body.lower()=='moon'): #Are we interested in moonbows?
            if (me.date > sunrise) & (me.date < sunset): #if daytime, skip to next loop iteration
                continue
            v = ephem.Moon(me)
            bowtype='moon'
            body='moon'
        elif (body.lower()=='sun'): #Are we interested in rainbows?
            if (me.date < sunrise) | (me.date > sunset): #if nighttime, skip to next loop iteration
                continue
            v = ephem.Sun(me)
            bowtype='rain'
            body='sun'
        else: #The user was ham-fisted and mis-typed something
            print("Set body='moon' or body='sun'. Cannot continue.")
            return
        
        
        m_alt = v.alt #radians
        m_az = v.az #radians
        
        if m_alt < 0: #if the moon is below the horizon, you're not getting a moonbow.
            continue #skip to next minute

        #The relevant vector for calculating moonbows is directly opposite the vector from the observer to the moon.
        m_alt_opp = -1.*m_alt #moonbow is opposite the moon
        m_az_opp = m_az + np.pi
        
        #calculate angle between (observer to waterfall vector) and (observer to opposite moon ray vectors)
        angle = ephem.separation((az_obs_targ, alt_obs_targ), (m_az_opp, m_alt_opp)) #saves me from doing a cross product and dot product
        
        #print(ephem.date(date_pst + time_offset * ephem.minute), np.degrees([angle, m_alt_opp, m_az_opp])
        if np.abs(41.5 - np.degrees(angle)) < mist_radius: #Is a moonbow occuring now? Moon/rainbows form ~41.5* circles
            if not moonbow_occurring: #is this the first minute of the moonbow?
                moonbow_occurred=True
                moonbow_occurring=True
                print('A '+bowtype+'bow begins at ' + str(datetime.strftime(ephem.date(date_pst + time_offset * ephem.minute).datetime(), '%X'))+'.')
                mi.update(ephem.date(date_utc + time_offset * ephem.minute).datetime())
                print('The ' + body + ' is at az, alt: ' + str(round(np.degrees(m_az), 1)) + ', ' + str(round(np.degrees(m_alt), 1))+'.')
                print("The moon has a phase of " + str(int(round(mi.fractional_phase()*100.)))+'%.')
                
        else: #moonbow is not occurring at this minute
            if moonbow_occurring: #but moonbow occurred the previous minute
                print('The ' + bowtype+'bow ends at ' + str(datetime.strftime(ephem.date(date_pst + time_offset * ephem.minute).datetime(), '%X'))+'.')
                print('The ' + body + ' is at az, alt: ' + str(round(np.degrees(m_az), 1)) + ', ' + str(round(np.degrees(m_alt), 1))+'.')
                print()
                moonbow_occurring = False
                
    if not moonbow_occurred: #if nothing happened on this date
        print("No " + bowtype+"bow occurred on this day.")
        print()
        
        
        
        
def test():
    #tests code by comparing code predictions to online photos of moonbows.
    
    global observer, target, mist_radius
    
    print('Upper Falls from Meadow 1')
    print('https://www.flickr.com/photos/catconnor/8865153474/')
    print('Azi 356.7')
    print('May 25 2013 23:50 PM')
    print()
    
    observer = np.array([37.7413 , -119.5962, 3965./3.281])
    target = np.array([37.75554, -119.59804, 5132/3.281])
    mist_radius = 6.
    main(2013, 5, 25)
    
    print('-------------------------------')
    print()
    print()
    
    
    
    print('Upper Falls from Meadow 2')
    print('https://www.flickr.com/photos/dublinphotography/26952652770/')
    print('Azi 337')
    print('May 21 2016 23:30 PM (description) or 21:56 (exif)')
    print()
    
    observer = np.array([37.7441 , -119.5913, 3965./3.281]) #lat lon alt of meadow lookout with view of Lower YF
    target = np.array([37.75554, -119.59804, 5132/3.281])
    mist_radius = 6.
    main(2016, 5, 21)
    
    print('-------------------------------')
    print()
    print()
    
    
    
    print('Lower Falls from bridge')
    print('https://www.flickr.com/photos/jeffreysullivan/40756678453/')
    print('Azi 320')
    print('April 18 2019 19:54')
    print()
   
    observer = np.array([37.74993 , -119.59575, 3965./3.281])
    target = np.array([37.75139, -119.59742, 4212/3.281])
    mist_radius = 15.
    main(2019, 4, 18)
    
    print('-------------------------------')
    print()
    print()
    
    
    
    print('Upper Falls from Glacier Point 1')
    print('https://images.squarespace-cdn.com/content/v1/5adf6636e17ba3f996b39514/1525029670564-MU2UMTCUS026PWP61373/ke17ZwdGBToddI8pDm48kIbjV-s7o2MLanQlZ8IRkqx7gQa3H78H3Y0txjaiv_0fDoOvxcdMmMKkDsyUqMSsMWxHk725yiiHCCLfrh8O1z5QPOohDIaIeljMHgDF5CVlOqpeNLcJ80NK65_fV7S1US1CwS58ewNEcH9esa2Eu1XXPVfMO6JTiQ27YnmqzjSWZCkVnhDMoqWnIzF2cFonXg/Moonbow+in+Yosemite+Falls+from+Glacier+Point+by+Brian+Hawkins+180428-09912.JPG?format=2500w')
    print('Azi 320')
    print('April 28 2018 23:54')
    print()
   
    observer = np.array([37.73036 , -119.57362, 7208./3.281])
    target = np.array([37.75554, -119.59804, 5132/3.281])
    mist_radius = 2.
    main(2018, 4, 28)
    

    print('-------------------------------')
    print()
    print()


    
    print('Upper Falls from Eagle Peak Lookout Daytime Rainbow')
    print('')
    print('Azi 80')
    print('May 1 2017 12:38')
   
    observer = np.array([37.754496 , -119.60288, 7238./3.281])
    target = np.array([37.75473, -119.5982, 5080/3.281])
    mist_radius = 6.
    main(2017, 5, 1, body='sun')
    

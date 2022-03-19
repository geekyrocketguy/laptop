#Checks site to see if it has changed.
#syntax: python3 checkforchange.py test
#test is optional

#written for recreation.gov trailheads

#Google will occasionally get grumpy and block the login attempt (maybe
# if the IP address changes?). Either open a browser on the computer and log
# in to scexaonotifier@gmail.com, or click the "Yes that was me" on the
# "Someone has your password!" security emails that gmail sends out.
# Then everything will be happy again.


import smtplib
import os.path
#import urllib
from urllib.request import urlopen
#import numpy as np
import sys
import subprocess
import pdb

args=sys.argv
 
to_address = 'geekyrocketguy@gmail.com' #Who should the email be sent to?
#to_address = ['geekyrocketguy@gmail.com', 'savillephotographer@gmail.com'] #Who should the email be sent to?
url='https://www.recreation.gov/api/camps/availability/campground/232451/month?start_date=2022-05-01T00%3A00%3A00.000Z'

page = urlopen(url) #python 3 version of command
#page = urllib.urlopen(url) #python 2 version of command
pagecontents = str(page.read())

campground_names = ['Hodgdon Meadow']
#trailheads = [ '44585939', '44585954' ] #Porcupine creek, yose falls
dates = ['2022-05-15' ]
message = ''
success = False
    
#for i in range(len(trailheads)):
for i in range(len(dates)):
    locs = [i for i in range(len(pagecontents)) if pagecontents.startswith('Available', i)] #where "Available" is found
    for j in locs:
        if dates[i] in pagecontents[j-25 : j-5]:
            print(date, "found!")
            success = True
            message += campground_names[j] + " has available spots on " + dates[i] + ". "
        
if success:
    print('An available date was found.')
else:
    print("No permits were available.")

#check if file exists
if not os.path.isfile('status_campgrounds.txt'): #if someone deleted the file, recreate it
    f=open('status_campgrounds.txt', 'w')
    f.write(message)
    f.close()
    print( 'status_campgrounds.txt was deleted by some goon, but it has been restored.')

f=open('status_campgrounds.txt', 'r')
oldcontents=f.read() #has the user been emailed recently?
f.close()

if (message != oldcontents) or ('test' in args): #has something changed? Then email user.
    #print new availability into text document
    f=open('status_campgrounds.txt', 'w')
    f.write(message)
    f.close()

    #send email saying the detector is cooled again and ready to use
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    #pw = np.loadtxt('notthepassword.txt', dtype='str')
    pw = subprocess.check_output('cat notthepassword.txt', shell=True).decode('ascii')
    #pw = os.system('cat notthepassword.txt')
    #pdb.set_trace()
    server.login('scexaonotifier@gmail.com', pw)

    if 'test' in args:
        #message = 'THIS IS A TEST.\n\n'
        mysubject = 'Yosemite campsites code is working'
    else:
        mysubject = 'Change in Campsite Availability'

    message = "The campsite availability has changed. " + message + \
           "The reservation URL is https://www.recreation.gov/camping/campgrounds/232451. We want to check in 5/14 and check out 5/15.\n\n" + \
           "Thought you might want to know.\n\n"\
           "Love,\n"\
           "Sean"
    
    server.sendmail("scexaonotifier@gmail.com", to_address, 
                    'Subject: '+mysubject+'\n\n'+message)
    server.quit()


else:
    print( "Nothing has changed, code is happy.")
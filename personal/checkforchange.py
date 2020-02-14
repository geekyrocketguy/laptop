#!/usr/bin/env python

#Checks site to see if it has changed.
#syntax: python checkforchange.py test
#test is optional

#Google will occasionally get grumpy and block the login attempt (maybe
# if the IP address changes?). Either open a browser on SCExAO2 and log
# in to scexaonotifier@gmail.com, or click the "Yes that was me" on the
# "Someone has your password!" security emails that gmail sends out.
# Then everything will be happy again.


import smtplib
import os.path
import urllib
import numpy as np
import sys
import pdb

args=sys.argv
 
to_address = 'geekyrocketguy@gmail.com' #Who should the email be sent to?
url='https://www.nps.gov/yose/planyourvisit/fulltrailheads.htm'

#page = urllib.request.urlopen(url) #python 3 version of command
page = urllib.urlopen(url) #python 2 version of command
pagecontents = str(page.read())

trailheads = [  ('Cathedral Lakes', 'Deer Camp'), 
                ('Glacier Point-&gt;Little Yosemite', 'Glen Aulin'),
                ('Sunrise Lakes', 'Tamarack Creek') ]
dates = [23, 24]
message = ''
success = False
    
for i in range(len(trailheads)):
    crop = pagecontents[pagecontents.find(trailheads[i][0]) : pagecontents.find(trailheads[i][1])]
    
    if len(crop)==0: #failed to download or trailhead disappeared
        print(trailheads[i][0] + "has disappeared! Quitting.")
        quit
    
    july_loc = crop.find('July')
    crop = crop[july_loc :]
    end_loc = crop.find('August')
    if end_loc != -1:
        crop = crop[ : end_loc]
     
    #clean HTML
    while crop.find('<') != -1: #remove html tags
        crop = crop.replace(crop[crop.find('<') : crop.find('>')+1], '')
    crop = crop.replace('July', '').replace('\\n', '')
    crop = np.array(crop.split()).astype(int)
    
    for date in dates:
        if date not in crop:
            message += 'July ' + str(date) + ' is available for ' + trailheads[i][0]+'. '
            success = True

if success:
    print('An available date was found.')
else:
    print("No permits were available.")

#check if file exists
if not os.path.isfile('status.txt'): #if someone deleted the file, recreate it
    f=open('status.txt', 'w')
    f.write(message)
    f.close()
    print( 'status.txt was deleted by some goon, but it has been restored.')

f=open('status.txt', 'r')
oldcontents=f.read() #has the user been emailed recently?
f.close()

if (message != oldcontents) or ('test' in args): #has something changed? Then email user.
    #print new availability into text document
    f=open('status.txt', 'w')
    f.write(message)
    f.close()

    #send email saying the detector is cooled again and ready to use
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    pw = np.loadtxt('notthepassword.txt', dtype='str')
    server.login('scexaonotifier@gmail.com', pw)

    if 'test' in args:
        message = 'THIS IS A TEST\n\n'
        mysubject = 'Code is Working'
    else:
        mysubject = 'Change in Permit Availability'

    message = "The trailhead availability has changed. " + message + \
           "The reservation phone number is 209-372-0740 and the trailhead URL is https://www.nps.gov/yose/planyourvisit/wpres.htm \n\n" + \
           "Thought you might want to know.\n\n"\
           "Love,\n"\
           "Sean"
    
    server.sendmail("scexaonotifier@gmail.com", to_address, 
                    'Subject: '+mysubject+'\n'+message)
    server.quit()


else:
    print( "Nothing has changed, code is happy.")
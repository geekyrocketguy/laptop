#Checks site to see if it has changed.
#syntax: python3 checkforchange.py test
#test is optional

#written for recreation.gov trailheads

#Google will occasionally get grumpy and block the login attempt (maybe
# if the IP address changes?). Either open a browser on the computer and log
# in to scexaonotifier@gmail.com, or click the "Yes that was me" on the
# "Someone has your password!" security emails that gmail sends out.
# Then everything will be happy again.


#import smtplib
import yagmail #pip3 install yagmail
import os.path
#import urllib
from urllib.request import urlopen
#import numpy as np
import sys
import subprocess
import pdb

args=sys.argv
 
to_address = 'geekyrocketguy@gmail.com'#, 'joygoebel@gmail.com'] #Who should the email be sent to?
url='https://www.recreation.gov/api/camps/availability/campground/232461/month?start_date=2022-06-01T00%3A00%3A00.000Z'

page = urlopen(url) #python 3 version of command
#page = urllib.urlopen(url) #python 2 version of command
pagecontents = str(page.read())

campground_names = ['Lodgepole Campground']
#trailheads = [ '44585939', '44585954' ] #Porcupine creek, yose falls
dates = ['2022-06-14' ]
message = ''
success = False
    
#for i in range(len(trailheads)):
for i in range(len(dates)):
    locs = [i for i in range(len(pagecontents)) if pagecontents.startswith('Available', i)] #where "Available" is found
    for j in locs:
        if dates[i] in pagecontents[j-25 : j-5]:
            print(dates[i], "found!")
            success = True
            message += campground_names[0] + " has available spots on " + dates[i] + ". "
        
if success:
    print('An available date was found.')
else:
    print("No permits were available.")

#check if file exists
if not os.path.isfile('status_lodgepole.txt'): #if someone deleted the file, recreate it
    f=open('status_lodgepole.txt', 'w')
    f.write(message)
    f.close()
    print( 'status_lodgepole.txt was deleted by some goon, but it has been restored.')

f=open('status_lodgepole.txt', 'r')
oldcontents=f.read() #has the user been emailed recently?
f.close()

if (message != oldcontents) or ('test' in args): #has something changed? Then email user.
    #print new availability into text document
    f=open('status_lodgepole.txt', 'w')
    f.write(message)
    f.close()

    pw = subprocess.check_output('cat notthepassword.txt', shell=True).decode('ascii')
    user = 'scexaonotifier@gmail.com'

    if 'test' in args:
        message = 'THIS IS A TEST.\n\n'
        subject = 'Lodgepole campground code is working'
    else:
        subject = 'Change in Campsite Availability'
        message = "The campsite availability has changed. " + message + \
'''The reservation URL is https://www.recreation.gov/camping/campgrounds/232461. We want to check in 7/2 and check out 7/3.

Thought you might want to know.

Love,
Sean'''
   
    print(message)

    with yagmail.SMTP(user, pw) as yag:
        yag.send(to_address, subject, message)
        print('Sent email successfully')


else:
    print( "Nothing has changed, code is happy.")

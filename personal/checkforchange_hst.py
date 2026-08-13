#Checks site to see if it has changed.
#syntax: python checkforchange.py test
#test is optional

#written for recreation.gov trailheads

#Google will occasionally get grumpy and block the login attempt (maybe
# if the IP address changes?). Either open a browser on SCExAO2 and log
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
 
to_address = ['geekyrocketguy@gmail.com', 'joygoebel@gmail.com'] #Who should the email be sent to?
#to_address = ['geekyrocketguy@gmail.com', 'savillephotographer@gmail.com'] #Who should the email be sent to?
url='https://www.recreation.gov/api/permitinyo/445857/availability?start_date=2022-07-01&end_date=2022-07-31&commercial_acct=false'

page = urlopen(url) #python 3 version of command
#page = urllib.urlopen(url) #python 2 version of command
pagecontents = str(page.read())

trailhead_names = ['High Sierra Trail']
trailheads = [ '44585711' ] #hst
dates = ['2022-07-10', '2022-07-11']
message = ''
success = False
    
for i in range(len(dates)):
    for j in range(len(trailheads)):
    
        endday = str(int(dates[i][-2:])+1)
        if len(endday)==1: endday = '0'+endday #make sure the day is double digit
        enddate = dates[i][:-2] + endday #add month and year
        crop = pagecontents[pagecontents.find(dates[i]) : pagecontents.find(enddate)]

        crop = crop[crop.find(trailheads[j]) :]
        crop = crop[crop.find("remaining")+11 : crop.find("is_walkup")].replace(',"', "")
        

        if len(crop)==0: #failed to download or trailhead disappeared
            print("Error finding date! Quitting.")
            quit

        if crop != '0':
            success = True
            message += trailhead_names[j] + " has available permits on " + dates[i] + ". "
        
if success:
    print('An available date was found.')
else:
    print("No permits were available.")
    message = 'No permits are available.'

#check if file exists
if not os.path.isfile('status_hst.txt'): #if someone deleted the file, recreate it
    f=open('status_hst.txt', 'w')
    f.write(message)
    f.close()
    print( 'status_hst.txt was deleted by some goon, but it has been restored.')

f=open('status_hst.txt', 'r')
oldcontents=f.read() #has the user been emailed recently?
f.close()

if (message != oldcontents) or ('test' in args): #has something changed? Then email user.
    #print new availability into text document
    f=open('status_hst.txt', 'w')
    f.write(message)
    f.close()

    pw = subprocess.check_output('cat notthepassword.txt', shell=True).decode('ascii')
    user = 'scexaonotifier@gmail.com'

    if 'test' in args:
        message = 'THIS IS A TEST. '+message +'\n\n'
        subject = 'High Sierra Trail Code is Working'
    else:
        subject = 'Change in Permit Availability'
        message = "The High Sierra Trail trailhead availability has changed. " + message + \
'''The reservation URL is https://www.recreation.gov/permits/445857/registration/detailed-availability?date=2022-07-01&type=overnight-permit and the possible entry dates are 7/10 or 7/11.
Thought you might want to know.

Love,
Sean'''

    print(message)

    with yagmail.SMTP(user, pw) as yag:
        yag.send(to_address, subject, message)
        print('Sent email successfully')


else:
    print( "Nothing has changed, code is happy.")

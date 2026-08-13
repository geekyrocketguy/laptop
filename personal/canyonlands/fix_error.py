import shutil
import glob
import numpy as np
import pdb

'''
In November 2025 code, the campsite indexing started at 30 instead of 31. Therefore, the
campsite names in the saved json files were wong; they started with Taylor (White Rim Road)
instead of Doll House 1 (Maze). This code copies the old json files to a new folder and 
renames them so they are correct.
'''

campsite_names = ["Taylor", "Doll House 1", "Doll House 2", "Doll House 3", "Chimney Rock", "The Wall", "Standing Rock", \
                "Maze Overlook 1", "Maze Overlook 2", "Golden Stairs", "Teapot Rock", "Sunset Pass", "The Neck", \
                "Happy Canyon", "North Point", "Panorama Point", "Cleopatra's Chair", "High Spur", "Millard Canyon", \
                "Ekker Butte", "Flint Seep"]

old_dir = r'D:\Dropbox\canyonlands_scrape\jsons_original'
new_dir = r'D:\Dropbox\canyonlands_scrape\jsons'
    

def fix_error():
    #get list of campsites
    files = glob.glob(old_dir+'/*json')
    
    for i in range(len(files)):
        for j in range(len(campsite_names)):
            if campsite_names[j] in files[i]:
                new_fn = files[i].replace(campsite_names[j], campsite_names[j-1]).replace(old_dir, new_dir)
                break
        new_fn = new_fn.replace(old_dir, new_dir)
         
        shutil.copy2(files[i], new_fn)
        print("Copied " + files[i] + " to " + new_fn)
        #print('copied to ' + new_fn)
        
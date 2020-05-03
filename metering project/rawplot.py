import rawpy
import numpy as np
import matplotlib.pyplot as plt
import glob
import pdb
import exifread
from scipy.interpolate import interp1d
from pathlib import Path

EV_step = 1 #what was the step size for the LED?
max_bright = 0 #what was the max brightness in EV?
min_bright = -10 #what was the min brightness in EV?

#INPUT DIR AS A LITERAL, i.e. r'mydir'
def main(dir, fno=2.8 ,save=False):
    dir = Path(dir)
    files = [str(pp) for pp in dir.glob("*.arw")]
    files = np.append(files, [str(pp) for pp in dir.glob("*cr2")])
    files = np.append(files, [str(pp) for pp in dir.glob("*cr3")])
    files = np.append(files, [str(pp) for pp in dir.glob("*nef")])
    
    if len(files) == 0:
        print("No files found.")
        return
    elif (len(files) != (max_bright - min_bright)/EV_step + 1):
        print(str(len(files)) + " were found, but " + str((max_bright - min_bright)/EV_step + 1) + " were expected. Quitting.")
        print(files)
        return
    else:
        print(files)
  
    means = np.zeros((4, len(files))) #channels, files
    settings = np.array([])
    
    for i in range(len(files)):
        print("Reading file", i+1, "of", len(files))
        raw = rawpy.imread(files[i])
        for j in range(len(raw.raw_pattern.flatten())):
            #compute mean of channel, subtract off black level
            means[j, i] = np.mean(raw.raw_image_visible[np.where(raw.raw_colors_visible == raw.raw_pattern.flatten()[j])]) - \
                            raw.black_level_per_channel[j]
        raw.close()
        
        #extract metadata
        raw = open(files[i], 'rb')
        tags = exifread.process_file(raw, details=False)
        if i==0: #extract metadata for title
            make = str(tags['Image Make'])
            model = str(tags['Image Model'])
        settings = np.append(settings, str(tags['EXIF ExposureTime']) + ',' + str(tags['EXIF FNumber']) + ',' + str(tags['EXIF ISOSpeedRatings']))
        
    means = np.mean(means, 0) #average the colors together
    
    xaxis = np.linspace(max_bright, min_bright, (max_bright-min_bright)/EV_step + 1)
    xaxis_finespace = np.linspace(max_bright, min_bright, (max_bright-min_bright)*100 + 1)
    splinefit = interp1d(xaxis, means, kind='quadratic') #quadratic spline interpolation
    myfit = splinefit(xaxis_finespace)


    #This equation gives the EV of darkening from one image to the next
    deriv = (np.log2(myfit[1:]) - np.log2(myfit[:-1]))/(xaxis_finespace[0] - xaxis_finespace[1])
    #failure occurs when the camera fails to compensate at least 2/3 of a stop when ambient light drops by 1 whole stop
    #Equivalently, this occurs when the derivative of our data points is -0.33 EV of image brightness per EV of LED dimming
    failurepoint = robustfindmin(xaxis_finespace[1:], np.abs(deriv + 1./3.)) #np.where( np.abs(deriv + 1./3.) == np.min(np.abs(deriv + 1./3.)))
    DN_of_failure_def1 = np.asscalar(myfit[failurepoint])
    ev_of_failure_def1 = np.asscalar(xaxis_finespace[failurepoint])
    print("Metering limit (definition 1):", ev_of_failure_def1)

    DN_of_failure_def2 = means[0]/2#np.mean(means[0:2]) #average of first two points
    failurepoint = np.where( np.abs(myfit - DN_of_failure_def2) == np.min( np.abs(myfit - DN_of_failure_def2))) #where does the brightness drop by 1 EV?
    ev_of_failure_def2 = np.asscalar(xaxis_finespace[failurepoint])
    print("Metering limit (definition 2):", ev_of_failure_def2)

    
    if settings[-1] == settings[-2]:
        print("The camera completely gives up at settings equivalent to (SS, f#, ISO):", settings[-1])
    else:
        print("The camera has nonzero sensitivity until dimmer than", min_bright, "EV.")
        

    plt.figure(figsize=(12, 8))
    plt.plot(xaxis, means , 'o', markersize=12, label="Image")
    plt.plot(xaxis_finespace, myfit, label="Fit")

    plt.hlines(DN_of_failure_def1, 0, ev_of_failure_def1, linestyles='dotted', colors='gray')
    plt.vlines(ev_of_failure_def1, 0, DN_of_failure_def1, linestyles='dotted', colors='gray')
    plt.annotate("1/3 stop image darkening per 1 EV scene darkening", [np.min([0, (ev_of_failure_def1+6)/2]), DN_of_failure_def1*1.03], size=16 )
    #plt.annotate(str(np.around(ev_of_failure_def1,2))+" EV", [ev_of_failure_def1+0.98, (np.min(means) + DN_of_failure_def1)/2.], size=16 )
    bbox_props = dict(boxstyle="square,pad=0.2", fc="white", lw=0, alpha=0.5)
    t=plt.text(ev_of_failure_def1, np.min(means) + 0.03*(np.max(means)-np.min(means)), str(np.around(ev_of_failure_def1,2))+" EV", ha="center", va="center", size=16, bbox=bbox_props)

    plt.hlines(DN_of_failure_def2, 0, ev_of_failure_def2, linestyles='dotted', colors='gray')
    plt.vlines(ev_of_failure_def2, 0, DN_of_failure_def2, linestyles='dotted', colors='gray')
    plt.annotate("1 stop darkening from 0 EV image", [np.min([0, (ev_of_failure_def2+3.5)/2]), DN_of_failure_def2*1.03], size=16 )
    #plt.annotate(str(np.around(ev_of_failure_def2,2))+" EV", [ev_of_failure_def2+0.98, (np.min(means) + DN_of_failure_def2)/2.], size=16 )
    t=plt.text(ev_of_failure_def2, np.min(means) + 0.03*(np.max(means)-np.min(means)), str(np.around(ev_of_failure_def2,2))+" EV", ha="center", va="center", size=16, bbox=bbox_props)

    plt.legend(fontsize=16)
    plt.xlim(max_bright, min_bright) #reverse x axis so dimmer is to the right
    plt.ylim(np.min(means)*0.9, np.max(means)*1.1)
    plottitle = make + ' ' + model + " Metering, f/" + str(fno) + " Lens"
    plottitle = plottitle.replace("SONY", "Sony").replace("Canon Canon", "Canon") #fix annoying formatting from EXIF
    plt.title(plottitle, size=20)
    plt.xlabel("Ambient light level [EV]", size=16)
    plt.ylabel("Average image brightness [DN]", size=16)
    plt.tick_params(axis='both', which='both', labelsize=16)
    plt.tight_layout()

    if save:
        plottitle = plottitle.replace(" Metering, f/" + str(fno) + " Lens", '').replace(" ", "_")
        plt.savefig(dir / plottitle)
        print("Figure saved as " + str(dir / plottitle))
    #pdb.set_trace()


def fluxcal():
    files = glob.glob('flux_cal/*arw')
    n_stops_dimming = np.array([0,1,2,3,4,5,6,7, 5,6,7,8,9,10])
    
    fluxes = np.zeros((4, len(files)))
    for i in range(len(files)):
        print("Reading file", i+1, "of", len(files))
        raw = rawpy.imread(files[i])
        for j in range(len(raw.raw_pattern.flatten())):
            #compute mean of channel, subtract off black level
            fluxes[j, i] = np.mean(raw.raw_image_visible[np.where(raw.raw_colors_visible == raw.raw_pattern.flatten()[j])]) - \
                            raw.black_level_per_channel[j]
        
        #fluxes[i] = np.mean(raw.raw_image_visible)
        colors = raw.color_desc.decode("utf-8").lower()
        raw.close()
        
        raw = open(files[i], 'rb')
        tags = exifread.process_file(raw, details=False)
        exptime = str(tags['EXIF ExposureTime'])
        fluxes[:, i] /= float(exptime) #assumes exposure time >= 1 second
        
    for i in range(np.shape(fluxes)[0]):
        plt.semilogy(n_stops_dimming, fluxes[i,:], colors[i]+'o-')
    fit = fluxes[0,0] / 2.**np.arange(11)
    plt.plot(fit)
    plt.show()
    
def moonphase_EV_plot():
    pi = np.linspace(0,100,101) #percent of moon illuminated
    pa = np.arccos(pi/50.-1) #corresponding phase angle
    m = -12.73 + 1.49 * np.abs(pa) + 0.043*pa**4 #eqn from https://astronomy.stackexchange.com/questions/10246/is-there-a-simple-analytical-formula-for-the-lunar-phase-brightness-curve
    flux = 2.512**(-1.*m)+4000 #4000 (arb units) is the brightness of stars
    t_exp = 242101/flux  #correct settings at iso 6400 f/2.8. 242101 is the magic number that comes from my "optimal exposure" fit.
    EV100 = np.log2(2.8**2 / t_exp * 100 / 6400) #convert to exposure values at ISO 100
    EV100 += 2 #I expose two stops above "correct" settings
    
    plt.figure(figsize=(12,8))
    plt.plot(pi, EV100)
    plt.tick_params(axis='both', which='both', labelsize=16)
    plt.xlabel("Moon Percent Illuminated", size=16)
    plt.ylabel("EV (ISO 100)", size=16)
    plt.title("Exposure Values as Function of Moon Phase", size=18)
    #plt.xlim(0,100)
    plt.grid(b=True, which='major', axis="both")
    plt.tight_layout()
    
    f= open("moonphase_vs_ev.csv","w+")
    for i in range(len(pi)):
        f.write("%i , %.1f\n" %(pi[i], EV100[i]))
    f.close()

def robustfindmin(x, y):
    #x is the x axis, y is the function we are trying to find the local minimum of.
    #This function returns the location of the local minimum in the y.
    #
    #Before, I had
    #failurepoint = np.where( np.abs(deriv + 1./3.) == np.min(np.abs(deriv + 1./3.)))
    #but sometimes this failed because there were multiple local minima of almost 0, and the 
    #global minimum wasn't the one at the highest EV. I want the one corresponding to the highest EV.
    #This selects all data near 0. Then takes the max of the EV corresponding to those. Then it
    #searches for a minimum within a small range around there, thereby excluding other local minima.
    
    threshold = 0.01 #points have to be below this to be considered.
    loc = np.where(y < threshold)
    x_guess = np.max(x[loc])
    min = np.min(y[np.where((x < x_guess + 0.2) & (x > x_guess - 0.2))])
    #np.asscalar(x[np.where(y == min)])
    
    return np.where(y == min)
import numpy as np
import matplotlib.pyplot as plt

def main(fn_spectra, plot=False):
    asd_lam, asd_flux = np.loadtxt(fn_spectra, skiprows=39, delimiter=',', unpack=True)
    #asd_flux has units of W m^-2 Sr^-1 m^-1
    #asd_flux *= 1e-9 #convert wavelength term to nm^-1
    
    lf_lam, lf_weight = np.loadtxt('luminosity_function_juddvoss1978.csv', delimiter=',', unpack=True)
    
    loc = np.where((asd_lam >= np.min(lf_lam)) & (asd_lam <= np.max(lf_lam)))
    asd_lam = asd_lam[loc]
    asd_flux = asd_flux[loc]
    
    if (np.unique(lf_lam - asd_lam) != 0.): #should be all zeros.
        print("Bad!")
        return

    if plot:
        fig, ax1 = plt.subplots()

        color = 'tab:red'
        lns1 = ax1.plot(asd_lam, asd_flux*1e6, label="integrating sphere set to 0 EV", color=color)
        ax1.set_xlabel("Wavelength [nm]")
        ax1.set_ylabel("Radiance [μW / (m^2 Sr nm)]", color=color)
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.set_ylim(0, 3)

        ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

        color = 'tab:blue'
        lns2 = ax2.plot(lf_lam, lf_weight, color=color, label="Judd/Voss 1978 human eye data",)
        ax2.set_ylabel("Normalized sensitivity", color=color)  # we already handled the x-label with ax1
        ax2.tick_params(axis='y', labelcolor=color)
        ax2.set_ylim(0, 1.01)
        
        lns = lns1+lns2
        labs = [l.get_label() for l in lns]
        ax1.legend(lns, labs)
        
        #plt.legend()
        plt.title("Spectrum of Integrating Sphere and Human Eye Sensitivity")
        fig.tight_layout()  # otherwise the right y-label is slightly clipped
    

    
    luminous_flux_lm = 683.002 * np.sum(asd_flux * lf_weight) #units of lm m^-2 Sr^-1
    
    print(luminous_flux_lm, "lm /(m^2 Sr), or cd/m^2")
    print(np.log2(luminous_flux_lm)+3, "EV")
    
    #return luminous_flux_lm

from gwpy.timeseries import TimeSeries

spec = data.asd(4,2)    # Calculate the amplitude spectral density of the data
specfig = spec.plot()   # Plot the ASD
ax = specfig.gca()
ax.set_xlabel('Frequency [Hz]')
ax.set_xlim(30, 1024)
ax.set_ylabel(r'Noise ASD [1/$\sqrt{\mathrm{Hz}}$]')
ax.set_ylim(1e-24, 1e-19)
ax.grid(True, 'both', 'both')
# to save this figure:
# spec.savefig('/full/path/to/image.png')
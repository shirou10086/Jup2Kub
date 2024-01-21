from gwpy.timeseries import TimeSeries

specgram = data.spectrogram2(fftlength=2,overlap=1.75) ** (1/2.)  # Generate a spectrogram from the data
medratio = specgram.ratio('median')                               # Generate a normalized spectrogram
specgramfig = medratio.plot(norm='log', vmin=0.1, vmax=10)        # Plot the normalized spectrogram
specgramfig.set_ylim(30,1024)
specgramfig.set_yscale('log')
specgramfig.add_colorbar(label='Amplitude relative to median',cmap='YlGnBu_r')
# to save this figure:
# specgramfig.savefig('/full/path/to/image.png')
from gwpy.timeseries import TimeSeries

ts = data.plot()     # Generate a time series plot from the data
ax = ts.gca()        # Grab the current axes of the plot
ax.set_ylabel('Gravitational-wave amplitude [strain]')
ax.set_title('LIGO Livingston Observatory data')
# to save this figure:
# ts.savefig('/full/path/to/image.png')
from gwpy.timeseries import TimeSeries

data = TimeSeries.fetch_open_data('L1', 1126259446, 1126259478)
# on a LIGO Data Grid cluster, you can use the following to grab data (leave off frametype if using NDS2):
# data = TimeSeries.get('L1:GDS-CALIB_STRAIN', 1126259446, 1126259478, frametype='L1_HOFT_C00')
import pygrib

grbs = pygrib.open("/home/yjtech/WRFmodel/geog_data/GFS/gfs_20250415_f024.grib2")
grb = grbs.message(1)

print("Reference time:", grb.analDate)
print("Forecast time (hours):", grb.forecastTime)
print("Valid time:", grb.validDate)

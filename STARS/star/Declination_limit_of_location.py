from astropy.coordinates import SkyCoord, EarthLocation, Angle
import astropy.units as u
from astropy.time import Time



def declination_limit(longitude, latitude, altitude, elevation_limit):
    time = Time('2020-01-01T20:00:00')
    # Time does not need to be changed. Declination limit doesn't change with time.
    site_inf = EarthLocation(lon = longitude*u.deg, lat = latitude*u.deg, height = altitude*u.m)
    if latitude >= 0:
        target = SkyCoord(alt = elevation_limit*u.deg, az = 180.0*u.deg, frame = 'altaz', obstime = time, location = site_inf)
    else:
        target = SkyCoord(alt = elevation_limit*u.deg, az = 0.0*u.deg, frame = 'altaz', obstime = time, location = site_inf)
    low_dec = target.icrs.dec.degree
    return low_dec
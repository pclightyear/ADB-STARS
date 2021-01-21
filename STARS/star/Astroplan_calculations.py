#!/usr/bin/env python
# coding: utf-8

# # Usage description
# 
# Once a member's equipment joined a project, we need to allocate observation schedule daily to each equipment. Before scheduling, we need to calculate the entire observable time range of targets in the joined projects everyday for each equipment. (Note: we only calculate the observable time range here, therefore the time for different targets might overlap.) To do this, we need the location information, target information, and a timestamp to start calculating.  
#   
# ### The columns you need for the databases are:  
# **U_have_E (user's equipment)**
# - UhaveE_ID
# - longitude (deg)
# - latitude (deg)
# - altitude (m)
# - elevation limit of equipment (deg)
# 
# **Target**
# - TID
# - RA (longitude) (deg)
# - Dec (latitude) (deg)
#   
# ### The returned values are:
# - start time
# - end time
# 
# This is the observable time range for the target.  
# If the returned value is nan, it means there is no possible observation this/the upcoming night.  
#   
# <span style="color:blue">***Do this calculation at least once a day for each equipment.***</span>
# 
# ### Requirement
# - python 3.5+
# - numpy 1.10+
# - astropy 4.2+
# - astroplan 0.7
# 
# https://astroplan.readthedocs.io/en/latest/installation.html

# ## Create an 'Observer' = Set 'Equipment location'

# In[1]:


from astroplan import Observer
import astropy.units as u

def site_information(UhaveE_ID, longitude, latitude, altitude):
    site_inf = Observer(longitude=longitude*u.deg, latitude=latitude*u.deg, elevation=altitude*u.m, name=UhaveE_ID)
    # u.deg set the unit to degree 
    return site_inf


# ## Set 'Target'

# In[2]:


from astroplan import FixedTarget
from astropy.coordinates import SkyCoord
import astropy.units as u

def target_information(TID, ra, dec):
    target_coord = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame='icrs', equinox='J2000') 
    # 'icrs' and 'J2000' are coordinate system specifications, keep it
    target = FixedTarget(coord=target_coord, name=TID)
    return target


# ## Calculate 'Observability'

# In[3]:


from astroplan import Observer
import numpy as np
from astropy.time import TimeDelta
import astropy.units as u

half_day = TimeDelta(0.5, format='jd')
## Note: Currently, no Sun observation, twilight observation allowed.

def observable_time_range(calculation_time, site_inf, target, elevation_limit):
    elevation_limit = elevation_limit*u.deg
    if site_inf.is_night(calculation_time, horizon=-18*u.deg) == False:
        t_dusk = site_inf.twilight_evening_astronomical(calculation_time, which="next")
        t_dawn = site_inf.twilight_morning_astronomical(calculation_time, which="next")
        
        if ("{0.jd}".format(t_dusk) == 'nan') and ("{0.jd}".format(t_dawn) == 'nan'):
            # Polar day, no observation avaliable.
            t_start = np.nan
            t_end = np.nan
        
        elif ("{0.jd}".format(t_dusk) != 'nan') and ("{0.jd}".format(t_dawn) == 'nan'):
            # The day before polar night, next sunrise is not within 24 hours.
            if site_inf.target_is_up(calculation_time, target) == True:
                T_rise = site_inf.target_rise_time(calculation_time, target, which="previous", horizon=elevation_limit)
                T_set = site_inf.target_set_time(calculation_time, target, which="next", horizon=elevation_limit)
                if "{0.jd}".format(T_set) != 'nan':
                    # Observe from dusk till target set.
                    t_start = t_dusk
                    t_end = T_set
                    
                elif "{0.jd}".format(T_set) == 'nan':
                    # Target never set, observation avaliable from dusk till 12 hours later (more calculations will be execute later).
                    t_start = t_dusk
                    t_end = t_start + half_day
                    
            else:
                T_rise = site_inf.target_rise_time(calculation_time, target, which="next", horizon=elevation_limit)
                T_set = site_inf.target_set_time(calculation_time, target, which="next", horizon=elevation_limit)
                if "{0.jd}".format(T_rise) != 'nan' and "{0.jd}".format(T_set) != 'nan':
                    t_end = T_set
                    if t_dusk > T_rise:
                        t_start = t_dusk
                    else:
                        t_start = T_rise
                    
                elif "{0.jd}".format(T_rise) == 'nan' and "{0.jd}".format(T_set) == 'nan':
                    t_start = np.nan
                    t_end = np.nan
                    
        elif ("{0.jd}".format(t_dusk) != 'nan') and ("{0.jd}".format(t_dawn) != 'nan'):
            if site_inf.target_is_up(calculation_time, target) == True:
                T_rise = site_inf.target_rise_time(calculation_time, target, which="previous", horizon=elevation_limit)
                T_set = site_inf.target_set_time(calculation_time, target, which="next", horizon=elevation_limit)
                if "{0.jd}".format(T_set) != 'nan':
                    if t_dusk >= T_set:
                        # Target set before dusk, no observation tonight.
                        t_start = np.nan
                        t_end = np.nan
                    else:
                        if t_dawn > T_set:
                            t_start = t_dusk
                            t_end = T_set
                        else:
                            t_start = t_dusk
                            t_end = t_dawn
                        
                elif "{0.jd}".format(T_set) == 'nan':
                    # Target never set, observation avaliable from dusk till 12 hours later (more calculations will be execute later).
                    t_start = t_dusk
                    t_end = t_start + half_day
                
            else:
                T_rise = site_inf.target_rise_time(calculation_time, target, which="next", horizon=elevation_limit)
                T_set = site_inf.target_set_time(calculation_time, target, which="next", horizon=elevation_limit)
                
                if ("{0.jd}".format(T_rise) == 'nan') and ("{0.jd}".format(T_set) == 'nan'):
                    # Target never rise.
                    t_start = np.nan
                    t_end = np.nan
                    
                elif ("{0.jd}".format(T_rise) != 'nan') and ("{0.jd}".format(T_set) != 'nan'):
                    if t_dawn <= T_rise:
                        # Target won't rise until dawn, no observation tonight.
                        t_start = np.nan
                        t_end = np.nan
                    else:
                        if t_dusk > T_rise:
                            t_start = t_dusk
                        else:
                            t_start = T_rise
        
                        if t_dawn > T_set:
                            t_end = T_set
                        else:
                            t_end = t_dawn


    elif site_inf.is_night(calculation_time, horizon=-18*u.deg) == True:
        t_dusk = site_inf.twilight_evening_astronomical(calculation_time, which="previous")
        t_dawn = site_inf.twilight_morning_astronomical(calculation_time, which="next")
        
        if ("{0.jd}".format(t_dusk) == 'nan') and ("{0.jd}".format(t_dawn) == 'nan'):
            # Polar night, can observe at any time.
            if site_inf.target_is_up(calculation_time, target) == True:
                T_rise = site_inf.target_rise_time(calculation_time, target, which="previous", horizon=elevation_limit)
                T_set = site_inf.target_set_time(calculation_time, target, which="next", horizon=elevation_limit)
                if ("{0.jd}".format(T_rise) == 'nan') and ("{0.jd}".format(T_set) == 'nan'):
                    # Target never set.
                    t_start = calculation_time
                    t_end = t_start + half_day
                    
                elif ("{0.jd}".format(T_rise) != 'nan') and ("{0.jd}".format(T_set) != 'nan'):
                    t_start = calculation_time
                    t_end = T_set
                    
            else:
                T_rise = site_inf.target_rise_time(calculation_time, target, which="next", horizon=elevation_limit)
                T_set = site_inf.target_set_time(calculation_time, target, which="next", horizon=elevation_limit)
                if ("{0.jd}".format(T_rise) == 'nan') and ("{0.jd}".format(T_set) == 'nan'):
                    # Target never rise.
                    t_start = np.nan
                    t_end = np.nan
                    
                elif ("{0.jd}".format(T_rise) != 'nan') and ("{0.jd}".format(T_set) != 'nan'):
                    t_start = T_rise
                    t_end = T_set
    
        elif ("{0.jd}".format(t_dusk) == 'nan') and ("{0.jd}".format(t_dawn) != 'nan'):
            # The last polar night, Sun will rise the next day.
            if site_inf.target_is_up(calculation_time, target) == True:
                T_rise = site_inf.target_rise_time(calculation_time, target, which="previous", horizon=elevation_limit)
                T_set = site_inf.target_set_time(calculation_time, target, which="next", horizon=elevation_limit)
                if ("{0.jd}".format(T_rise) == 'nan') and ("{0.jd}".format(T_set) == 'nan'):
                    # Target never set.
                    t_start = calculation_time
                    t_end = t_dawn
                    
                elif ("{0.jd}".format(T_rise) != 'nan') and ("{0.jd}".format(T_set) != 'nan'):
                    t_start = calculation_time
                    if t_dawn > T_set:
                        t_end = T_set
                    else:
                        t_end = t_dawn
                        
            else:
                T_rise = site_inf.target_rise_time(calculation_time, target, which="next", horizon=elevation_limit)
                T_set = site_inf.target_set_time(calculation_time, target, which="next", horizon=elevation_limit)
                if ("{0.jd}".format(T_rise) == 'nan') and ("{0.jd}".format(T_set) == 'nan'):
                    # Target never rise.
                    t_start = np.nan
                    t_end = np.nan
                    
                elif ("{0.jd}".format(T_rise) != 'nan') and ("{0.jd}".format(T_set) != 'nan'):
                    if t_dawn <= T_rise:
                        # Target won't rise until dawn, no observation tonight.
                        t_start = np.nan
                        t_end = np.nan
                    else:
                        t_start = T_rise
                        if t_dawn > T_set:
                            t_end = T_set
                        else:
                            t_end = t_dawn         

        elif ("{0.jd}".format(t_dusk) != 'nan') and ("{0.jd}".format(t_dawn) != 'nan'):
            if site_inf.target_is_up(calculation_time, target) == True:
                T_rise = site_inf.target_rise_time(calculation_time, target, which="previous", horizon=elevation_limit)
                T_set = site_inf.target_set_time(calculation_time, target, which="next", horizon=elevation_limit)
                if ("{0.jd}".format(T_rise) == 'nan') and ("{0.jd}".format(T_set) == 'nan'):
                    # Target never set.
                    t_start = calculation_time
                    t_end = t_dawn
                    
                elif ("{0.jd}".format(T_rise) != 'nan') and ("{0.jd}".format(T_set) != 'nan'):
                    t_start = calculation_time
                    if t_dawn > T_set:
                        t_end = T_set
                    else:
                        t_end = t_dawn
            
            else:
                T_rise = site_inf.target_rise_time(calculation_time, target, which="next", horizon=elevation_limit)
                T_set = site_inf.target_set_time(calculation_time, target, which="next", horizon=elevation_limit)
                if ("{0.jd}".format(T_rise) == 'nan') and ("{0.jd}".format(T_set) == 'nan'):
                    # Target never rise.
                    t_start = np.nan
                    t_end = np.nan
                    
                elif ("{0.jd}".format(T_rise) != 'nan') and ("{0.jd}".format(T_set) != 'nan'):
                    if t_dawn <= T_rise:
                        # Target won't rise until dawn, no observation tonight.
                        t_start = np.nan
                        t_end = np.nan
                    else:
                        t_start = T_rise
                        if t_dawn > T_set:
                            t_end = T_set
                        else:
                            t_end = t_dawn
    # If t_start or t_end is not given a value, jump warning.
    
    return t_start, t_end


# ## Main program

# In[4]:


# Given arguments. Import this from your databases!!!

# # Equipment information
# UhaveE_ID = 1
# latitude = 19.825
# longitude = -155.4761
# altitude = 4200
# elevation_limit = 20

# # Target Informaiton
# TID = 1
# ra = 90.752
# dec = -16.716


# In[6]:


from datetime import datetime
from astropy.time import Time
import time

# if __name__ == '__main__':
def astroplan_calculations(
    UhaveE_ID,
    latitude,
    longitude,
    altitude,
    elevation_limit,
    TID,
    ra,
    dec
):
    start_time = time.time()
    
    calculation_time = datetime.now()
    #calculation_time = datetime.fromisoformat('2020-12-21T20:05:00')
    site_inf = site_information(UhaveE_ID, longitude, latitude, altitude)
    calculation_time = site_inf.datetime_to_astropy_time(calculation_time)
    calculation_time = Time(calculation_time, format='fits', scale='utc')
    
    target = target_information(TID, ra, dec)
    t_start, t_end = observable_time_range(calculation_time, site_inf, target, elevation_limit)
    
    try:
        t_start.format = 'fits'
    except AttributeError:
        pass
    try:
        t_end.format = 'fits'
    except AttributeError:
        pass

    return t_start, t_end

    end_time = time.time()
    
    print("--- %s seconds ---\n" % (end_time - start_time))
    print('start observation: %s \nend observation %s' % (t_start, t_end))


# In[ ]:





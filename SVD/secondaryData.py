#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Zachary Allen
@supervisor: Tirge McCarthy
@function: From the extracted data, calculates bandwise SNR, baseline projection length and angle; and time in mjd format for each observation
'''

import math
import cmath
import numpy as np
from astropy import coordinates
from astropy.time import Time
from numerical import NumberMethods
from geodeticData import ExtractSourceCatalogue, ExtractStationCatalogue

source_data = ExtractSourceCatalogue()
station_data = ExtractStationCatalogue()
number_functions = NumberMethods()

CHANNELS = 32
BANDWISE_CHANNELS = 8
BANDS = 4

class ToBandwiseSNR:

    '''
    @__init__: ToBandwiseSNR class constructor

    @param self: instance variable of the class, ToBandwiseSNR
    @param total_SNR: a list of the total (average) SNR for each observation in a session
    @param channelwise_amplitude: a list of amplitudes per channel for each observation in a session
    @param channelwise_phase: a list of complex phases per channel for each observation in a session
    '''
    def __init__(self, total_SNR, channelwise_amplitude, channelwise_phase):
        
        self.bandwise_SNR_list = []
        
        # Number of observations in the session, can be calculated from any of the lists
        observation_number = len(total_SNR)
        
        # Calculating bandwise SNR for each observation
        for observation in range(observation_number):

            try:    
                self.bandwise_SNR_list.append(
                    ToBandwiseSNR.calculateBandwiseSNR(
                        self, 
                        total_SNR[observation], 
                        channelwise_amplitude[observation], 
                        channelwise_phase[observation]
                ))

            # If an error occoured during the calculation of data the entry is changed to Err
            except Exception:
                self.bandwise_SNR_list.append(['Err', 'Err', 'Err','Err'])
    
    '''
    @toToBandwiseSNR: converts SNR into channelwise SNR using the Gipson equation

    @param self: instance variable of the class, ToBandwiseSNR
    @param observation_total_SNR: the combinded SNR for all 4 bands for the observation
    @param observation_channelwise_amplitude: the amplitude per channel for the observation
    @param observation_channelwise_phase: the complex phase per channel for the observation
    @return: list of SNR values for each of the 4 bands for the observation
    '''
    def calculateBandwiseSNR(self, observation_total_SNR, observation_channelwise_amplitude, observation_channelwise_phase):

        bandwiseSNR = []
        
        # Calculating the total amplitude
        total_amplitude = sum([
            float(observation_channelwise_amplitude[channel]) for channel in range(CHANNELS)
        ])
        
        for band in range(BANDS):

            # Calculating the bandwise complex fringe visibility
            complex_fringe_visibility = number_functions.complex_add(*[
                float(observation_channelwise_amplitude[channel]) 
                * cmath.exp(1j * math.radians(float(observation_channelwise_phase[channel]))) 
                for channel in range(band*BANDWISE_CHANNELS,(band+1)*BANDWISE_CHANNELS)
            ])
            
            # Calculating the bandwise SNR using the Gipson equation
            bandwiseSNR.append(
                observation_total_SNR
                * abs(math.sqrt(CHANNELS) / total_amplitude) 
                * abs(complex_fringe_visibility / math.sqrt(BANDWISE_CHANNELS))
            )

        return bandwiseSNR

    '''
    @get_bandwise_SNR_list: grabs list of bandwise SNR

    @param self: instance variable of the class, ToBandwiseSNR
    @return: list of bandwise SNR for each observation
    '''
    def get_bandwise_SNR_list(self) -> list:
        return self.bandwise_SNR_list
    
    bandwise = property(get_bandwise_SNR_list)

class FindProjection:

    '''
    @__init__: FindProjection class constructor

    @param self: instance variable of the class, FindProjection
    @param time_utc: the list of UTC times for each observation
    @param source: a list of source names for each observation in a session
    @param baseline: a list of telescope pairs for each observation in a session
    '''
    def __init__(self, time_utc, source, baseline):
        
        self.projected_baseline_list = []
        self.projected_angle_list = []

        # Number of observations in the session, can be calculated from any of the lists
        observation_num = len(source) 

        # Calculating the projection angle and projected baseline length for each observation
        for observation in range(observation_num):
                    
            try:
                telescopes_x = []
                telescopes_y = []
                telescopes_z = []

                # Converting telescope position int celestial cartesian coordinates
                for index in range(len(baseline[observation])):
                    
                    # Extracting a telescope from the baseline
                    telescope = baseline[observation][index]

                    # Calculating telescope celestial coordinates
                    telescope_right_ascension, telescope_declination = FindProjection.terrestial_to_celestial(self, telescope, time_utc[index])
                        
                    # Celestial height is just the distance from the centre of the Earth to the telescope which is the modulus of the cartesian position vector
                    height = number_functions.modulus(station_data.cartesian[station_data.name.index(telescope)])

                    # Converting telescope celestial coordinates to cartesian coordinates
                    telescope_coordinates = [float(coordinate) for coordinate in coordinates.spherical_to_cartesian(height, math.radians(telescope_declination), math.radians(telescope_right_ascension))]

                    telescopes_x.append(telescope_coordinates[0])
                    telescopes_y.append(telescope_coordinates[1])
                    telescopes_z.append(telescope_coordinates[2])

                telescopes_coordinates = [telescopes_x, telescopes_y, telescopes_z]
                        
                # Calculating the displacement vector between the telescope position vectors
                baseline_vector = [coordinate[1] - coordinate[0] for coordinate in telescopes_coordinates]
                
                # Note that the missing sources are being accouted in the lists
                source_index = (source_data.name).index(source[observation])
                        
                # Extracting source coordinates
                source_right_ascension = (source_data.right_ascension)[source_index]
                source_declination = (source_data.declination)[source_index]
                height = 1 # As we want a unit vector of length 1

                # Calculating the cartesian unit vector pointing in the direction of the source
                source_unit_vector = [
                    float(coordinate) 
                    for coordinate in coordinates.spherical_to_cartesian(
                        height, 
                        math.radians(source_declination), 
                        math.radians(source_right_ascension)
                )]
                                    
                # Calculating the vector projection of the baseline vector in the direction of the source unit vector
                projection = [
                    float(np.dot(baseline_vector, source_unit_vector)) * coordinate for coordinate in source_unit_vector
                ]
                            
                # Calculating the projected baseline vector from vector addition
                projected_baseline_vector = [baseline_vector[i] - projection[i] for i in range(3)]

                # Calculating the projected baseline length
                self.projected_baseline_list.append(
                    number_functions.modulus(projected_baseline_vector)
                )
        
                # Calculating the polar unit vector in cartesian coordinates at the position of the source
                polar_angle= math.radians(90-source_declination)
                azimuth_angle = math.radians(source_right_ascension)
                polar_unit_vector = [
                    math.cos(polar_angle) * math.cos(azimuth_angle), 
                    math.cos(polar_angle) * math.sin(azimuth_angle), 
                    -math.sin(polar_angle)
                ]

                # Calculating the negative of the polar unit vector
                negative_polar_unit_vector = [-1 * coordinate for coordinate in polar_unit_vector]

                # Calculating the projected baseline angle
                projected_baseline_angle = math.degrees(
                    math.acos( 
                        float(np.dot(projected_baseline_vector, negative_polar_unit_vector)) 
                        / (number_functions.modulus(projected_baseline_vector))
                ))
                
                # Calculating the azimuth angle in spherical coordinates of the projected baseline vector
                azimuth = math.degrees(math.atan(projected_baseline_vector[1] / projected_baseline_vector[0]))
                
                # Adding a negative sign to the angle if it is to the left (from source perspective) of the polar unit vector
                if abs(azimuth - source_right_ascension) >= 180:
                    projected_baseline_angle = -1 * projected_baseline_angle

                self.projected_angle_list.append(projected_baseline_angle)

            # If an error occoured during the calculation of data the entry is changed to Err
            except Exception:
                self.projected_baseline_list.append('Err')
                self.projected_angle_list.append('Err')

    '''
    @terrestial_to_celestial: Converts telescope position from terrestial to celestial coordinates

    @param self: instance variable of the class, FindProjection
    @param telescope: name of the telescope
    @param time_utc: utc time of observation
    @return: telescope right_ascension and declination in decimal degrees
    '''
    def terrestial_to_celestial(self, telescope, time_utc):
        
        station_index = station_data.name.index(telescope)

        # Finding longitude and latitude coordinates of the telescope
        longitude, latitude = station_data.geographic[station_index]

        # Finding telescopes right ascension and declination angles
        right_ascension = float(
            Time(time_utc, format = 'isot', scale = 'utc', location = ('%dd' % longitude, '%dd' % latitude))
            .sidereal_time('mean', 'greenwich').deg)

        declination = latitude

        return right_ascension, declination

    '''
    @get_projected_baseline_list: grabs list of projected baseline lengths

    @param self: instance variable of the class, FindProjection
    @return: list of projected baseline lengths
    '''
    def get_projected_baseline_list(self):
        return self.projected_baseline_list
    
    '''
    @get_projected_angle_list: grabs list of projected angles

    @param self: instance variable of the class, FindProjection
    @return: list of projected angles
    '''
    def get_projected_angle_list(self):
        return self.projected_angle_list
    
    baseline = property(get_projected_baseline_list)
    angle = property(get_projected_angle_list)

class ToTimeMJD:

    '''
    @__init__: ToTimeMJD class constructor

    @param self: instance variable of the class, ToTimeMJD
    @param time_utc_list: the list of UTC times of the observations
    '''
    def __init__(self, time_utc_list):

        self.time_mjd_list = []
        
        # Converting each utc time in the list to mjd time
        for time_utc in time_utc_list:
        
            try:
                self.time_mjd_list.append(float(Time(time_utc, format='isot', scale='utc').mjd))

            # If an error occoured during the calculation of data the entry is changed to Err
            except Exception:
                self.time_mjd_list.append('Err')

    '''
    @get_time_mjd_list: grabs the list of times in MJD format

    @param self: instance variable of the class, ToTimeMJD
    @return: list of times in MJD format
    '''
    def get_time_mjd_list(self):
        return self.time_mjd_list
    
    time = property(get_time_mjd_list)

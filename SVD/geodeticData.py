#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Zachary Allen
@supervisor: Tiege McCarthy
@function: Extracts relevant geodetic radio telescope and source data into python lists
'''

import os
from astropy.table import Table
from numerical import NumberMethods

number_functions = NumberMethods()

STATION_DATA_FILE = os.path.join(os.path.dirname(__file__),'geodetic.station.catalogue')
SOURCE_DATA_FILE = os.path.join(os.path.dirname(__file__), 'geodetic.source.catalogue')
STATION_CHARACTER_LENGTH = 8
SOURCE_CHARACTER_LENGTH = 8

class ExtractStationCatalogue:

    '''
    @__init__: ExtractStationCatalogue class constructor

    @param self: instance variable of the class, ExtractStationCatalogue
    '''
    def __init__(self):

        self.station_name_list = []
        self.station_cartesian_coordinates_list = []
        self.station_geographic_coordinates_list = []

        # Converting the STATION_DATA_FILE ascii table to a data frame
        station_info = Table.read(
            STATION_DATA_FILE, 
            format='ascii.csv', 
            delimiter=' ', 
            comment='*',
            data_start= 0, 
            names=['ID', 'Name', 'X (m)', 'Y (m)', 'Z (m)', 'Occ.Code', 'Longitude', 'Latitude', 'Origin', '']
            )
        
        for station in station_info:
            
            # Extracting station name
            station_name = str(station[1])

            # Adding necessary whitespace for station name to be 8 characters long
            for i in range(len(station[1]), STATION_CHARACTER_LENGTH):
                station_name += ' '

            self.station_name_list.append(station_name)

            # Extracting the cartesian coordinates
            self.station_cartesian_coordinates_list.append([
                float(station[2]),
                float(station[3]),
                float(station[4])
            ])

            # Extracting the geographic coordinates
            self.station_geographic_coordinates_list.append([
                float(station[6]),
                float(station[7])
            ])

    '''
    @get_station_name_list: grabs list of station names

    @param self: instance variable of the class, ExtractStationCatalogue
    @return: list of station names
    '''
    def get_station_name_list(self):
        return self.station_name_list
    
    '''
    @get_cartesian_station_coordinates_list: grabs list of cartesian station coordinates

    @param self: instance variable of the class, ExtractStationCatalogue
    @return: list of station coordinates
    '''
    def get_cartesian_station_coordinates_list(self):
        return self.station_cartesian_coordinates_list
    
    '''
    @get_geographic_station_coordinates_list: grabs list of geographic station coordinates

    @param self: instance variable of the class, ExtractStationCatalogue
    @return: list of geographic station coordinates
    '''
    def get_geographic_station_coordinates_list(self):
        return self.station_geographic_coordinates_list
    
    name = property(get_station_name_list)
    cartesian = property(get_cartesian_station_coordinates_list)
    geographic = property(get_geographic_station_coordinates_list)

class ExtractSourceCatalogue:
    
    '''
    @__init__: ExtractSourceCatalogue class constructor

    @param self: instance variable of the class, ExtractSourceCatalogue
    '''
    def __init__(self):
        self.source_IAU_name_list=[]
        self.source_common_name_list = []
        self.declination_list=[]
        self.right_ascension_list=[]
        
        # Converting the SOURCE_DATA_FILE ascii table to a data frame
        source_info = Table.read(
            SOURCE_DATA_FILE, 
            format='ascii.csv', 
            delimiter=' ', 
            comment='*', 
            data_start= 0, 
            names=['IAU-Name', 'Common', 'RA hh', 'RA mm', 'RA ss.ssss', 'DC sdd', 'DC mm', 'DC ss.sssss', 'epoch year', 'epoch time', '0.0', 'source']
            )
        
        for source in source_info:
            
            # Extracting source IAU and common name and formatting with the correct amout of whitespace
            for name in range(2):

                # Extracting the selected source name
                source_name = source[name]

                # Checking the source is not a null entry ($)
                if source_name != '$':

                    # Adding necessary whitespace for source name to be 8 characters long
                    for i in range(len(source_name), SOURCE_CHARACTER_LENGTH):
                        source_name += ' '

                else:
                    source_name = ' ' * SOURCE_CHARACTER_LENGTH

                # Adding the source name to the appropriate list
                if name == 0:
                    self.source_IAU_name_list.append(source_name)

                else:
                    self.source_common_name_list.append(source_name)

            # Extracting right ascension and converting from hours-minutes-seconds to decimal degrees
            self.right_ascension_list.append(
                number_functions.hmsDecimal(*source[2:5]))

            # Extracting declination and converting from degrees-minutes-seconds to decimal degrees
            self.declination_list.append(
                number_functions.dmsDecimal(*source[5:8]))

    '''
    @get_source_IAU_name_list: grabs list of source names

    @param self: instance variable of the class, ExtractSourceCatalogue
    @return: list of source names
    '''
    def get_source_IAU_name_list(self):
        return self.source_IAU_name_list
    
    '''
    @get_source_common_name_list: grabs list of source common names

    @param self: instance variable of the class, ExtractSourceCatalogue
    @return: list of source names
    '''
    def get_source_common_name_list(self):
        return self.source_common_name_list
    
    '''
    @get_right_ascension_list: grabs list of source right ascensions

    @param self: instance variable of the class, ExtractSourceCatalogue
    @return: list of sources right ascension angles
    '''
    def get_right_ascension_list(self):
        return self.right_ascension_list
    
    '''
    @get_right_declination_list: grabs list of source declinations

    @param self: instance variable of the class, SourceData
    @return: list of sources declination angles
    '''
    def get_declination_list(self):
        return self.declination_list
    
    name = property(get_source_IAU_name_list)
    common = property(get_source_common_name_list)
    right_ascension = property(get_right_ascension_list)
    declination = property(get_declination_list)
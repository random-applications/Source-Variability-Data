#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Zachary Allen
@supervisor: Tirge McCarthy
@function: Extracts relevant observables data from given VgosDB directory into lists
'''

import os
import netCDF4 as nc
from pathlib import Path
from geodeticData import ExtractSourceCatalogue, ExtractStationCatalogue

source_data = ExtractSourceCatalogue()
station_data = ExtractStationCatalogue()

class ReadNetCDF4:

    '''
    @__init__: ReadNetCDF4 class constructor

    @param self: instance variable of the class, ReadNetCDF4
    @param vgosDB_path: path to the selected session VgosDB's
    '''
    def __init__(self, vgosDB_path):

        # Observing mode (S/X or VGOS)
        self.observing_mode = ''

        # Boolean dictating whether or not a source missing from the list has been found
        self.missing_source = False

        # Boolean dictating whether or not a station missing from the list has been found
        self.missing_station = False

        # Extracted observation data lists
        self.session_code = ''
        self.observation_time_UTC_list = []
        self.observation_source_list = []
        self.observation_duration_bX_list = [] # Used as the default duration list for the VGOS database
        self.observation_baselines_list = []
        self.observation_QC_bX_list = [] # Used as the default quality code for the VGOS database
        self.observation_QC_bS_list = []
        self.observation_SNR_bX_list = [] # Used as the default signal-to-noise ratio for the VGOS database
        self.observation_SNR_bS_list = []
        self.observation_channelwise_amplitude = [] # Used as the default amplitude list for the VGOS database
        self.observation_channelwise_phase = [] # Used as the default phase list for the VGOS database

        # Extracted source data lists  
        self.source_name_list = []
        self.source_right_ascension_list = []
        self.source_declination_list = []
        self.source_reference_list = []

        # Extracted station data lists
        self.station_name_list = []
        self.station_cartesian_coordinates_list = []

        # Status codes of data extraction
        self.status_code_time_UTC = '0'
        self.status_code_duration_bX = '0'
        self.status_code_source = '0'
        self.status_code_baseline = '0'
        self.status_code_QC_bX = '0'
        self.status_code_QC_bS = '0'
        self.status_code_SNR_bX = '0'
        self.status_code_SNR_bS = '0'
        self.status_code_channelwise_amplitude = '0'
        self.status_code_channelwise_phase = '0'
        self.status_code_source_name = '0'
        self.status_code_right_ascension = '0'
        self.status_code_declination = '0'
        self.status_code_reference = '0'
        self.status_code_station_name = '0'
        self.status_code_station_coordinates = '0'
        self.status_code_missing_data = '0'

        # Looping through all the subdirectories in the VgosDB
        for sub_directory in Path(vgosDB_path).rglob(''):
            
            # Select the observables sub_directory
            if sub_directory.name == 'Observables':
                
                # Calculating the session code from the name of the sessions vgosDB
                self.session_code = Path(vgosDB_path).name.upper() # TODO GET RID OF .upper() ONCE RENAMING ERROR IS FIXED IN extractFile

                observables_directory = sub_directory

                # Finds relevant files in observables
                for file_path in Path(observables_directory).rglob('*'):
                    
                    if file_path.name == 'TimeUTC.nc':
                        self.observation_time_UTC_list, self.status_code_time_UTC = ReadNetCDF4.extractUTCTime(self, file_path)

                    # Duration is only extracted from the X band list as for S/X sessions, the S band list is empty
                    elif 'CorrInfo' in file_path.name and '_bX.nc' in file_path.name: 
                        self.observation_duration_bX_list, self.status_code_duration_bX = ReadNetCDF4.extractDuration(self, file_path)

                    elif file_path.name == 'Source.nc':
                        self.observation_source_list, self.status_code_source = ReadNetCDF4.extractSource(self, file_path)

                    elif file_path.name == 'Baseline.nc':
                        self.observation_baselines_list, self.status_code_baseline = ReadNetCDF4.extractBaseline(self, file_path)

                    elif file_path.name == 'QualityCode_bX.nc':
                        self.observation_QC_bX_list, self.status_code_QC_bX = ReadNetCDF4.extractQC(self, file_path)

                    elif file_path.name == 'QualityCode_bS.nc':
                        self.observation_QC_bS_list, self.status_code_QC_bS = ReadNetCDF4.extractQC(self, file_path)

                    elif file_path.name == 'SNR_bX.nc':
                        self.observation_SNR_bX_list, self.status_code_SNR_bX = ReadNetCDF4.extractSNR(self, file_path)

                    elif file_path.name == 'SNR_bS.nc':
                        self.observation_SNR_bS_list, self.status_code_SNR_bS = ReadNetCDF4.extractSNR(self, file_path)

                    elif file_path.name == 'ChannelInfo_bX.nc':
                        self.observation_channelwise_amplitude, self.observation_channelwise_phase, self.status_code_channelwise_amplitude, self.status_code_channelwise_phase = ReadNetCDF4.extractChannelInfo(self, file_path)

        # If a missing source was detected, extracting it from the vgosDB and adding it to the catalogure    
        if self.missing_source == True: 

            # Path to file with source information
            file_path = os.path.dirname(__file__) + '\\VgosDB\\' + self.session_code + '\\Apriori\\Source.nc'

            # Extracting the file of source information from the Apriori directory
            self.source_name_list, self.source_right_ascension_list, self.source_declination_list, self.source_reference_list, self.status_code_source_name, self.status_code_right_ascension, self.status_code_declination, self.status_code_reference = ReadNetCDF4.extractSourceInfo(self, file_path)
    
        # If a missing source was detected, extracting it from the vgosDB and adding it to the catalogure    
        if self.missing_station == True: 

            # Path to file with station information
            file_path = os.path.dirname(__file__) + '\\VgosDB\\' + self.session_code + '\\Apriori\\Station.nc'

            # Extracting the file of source information from the Apriori directory
            self.station_name_list, self.station_cartesian_coordinates_list, self.status_code_station_name, self.status_code_station_coordinates = ReadNetCDF4.extractStationInfo(self, file_path)

    '''
    @extractTime: reads the utc time from a NetCDF file

    @param self: instance variable of the class, ReadNetCDF4
    @param file: NetCDF file containing the time
    @return: time in utc format
    '''
    def extractUTCTime(self,file):

        data_set = nc.Dataset(file)
        utc_time_list = []
        status_code = '0' # If no errors occoured in the data extraction, the status code is 0

        # Boolean whether all entries are errors
        all_errors = True
        
        try:
            # Extracting year-month-day-hour-minute (YMDHM) and seconds datasets
            ymdhm_ndarray = data_set['YMDHM'][:]
            seconds_ndarray = data_set['Second'][:]
            
            # Decoding sources from a numpy.ndarray and adding to a list
            for time in range(len(ymdhm_ndarray)):

                try:
                
                    # Extracting the specific times from the list
                    ymdhm = ymdhm_ndarray[time]
                    seconds = seconds_ndarray[time]
                    
                    # Adding 2000 to the year if not already added
                    if len(str(ymdhm[0])) != 4:
                        year = 2000 + int(ymdhm[0])

                    # If the year is already added:
                    else:
                        year = int(ymdhm[0])

                    month = int(ymdhm[1])
                    day = int(ymdhm[2])
                    hour = int(ymdhm[3])
                    minute = int(ymdhm[4])
                    second = float(seconds)

                    # Modifying the time into isot format so that it can be converted into other formats by astropy
                    utc_time_list.append(
                        str(year) 
                        + '-' 
                        + ''.join(['0' for zeros in range(2-len(str(month)))])
                        + str(month) 
                        + '-' 
                        + ''.join(['0' for zeros in range(2-len(str(day)))])
                        + str(day) 
                        + 'T' 
                        + ''.join(['0' for zeros in range(2-len(str(hour)))])
                        + str(hour) 
                        + ':' 
                        + ''.join(['0' for zeros in range(2-len(str(minute)))])
                        + str(minute) 
                        + ':' 
                        + ''.join(['0' for zeros in range(2-len(str(int(second))))])
                        + str(second)
                    )

                    all_errors = False

                # If an error occoured during the decoding of data the entry is changed to Err
                except Exception:
                    status_code = '1' # If some errors occoured in the data extraction, the status code is 1
                    utc_time_list.append('Err')
        
            # Converting the list to an empty list if all entries are errors 
            if all_errors == True:
                status_code = '2' # If a fatal error occoured in the data extraction, the status code is 2
                utc_time_list = []

        # If a fatal error occoured an empty list is returned
        except Exception:
            status_code = '2' # If a fatal error occoured in the data extraction, the status code is 2
            utc_time_list = []
            
        return utc_time_list, status_code
    
    '''
    @extractDuration: reads the observation durations from a NetCDF file into a list

    @param self: instance variable of the class, ReadNetCDF4
    @param file: NetCDF file containing scan durations
    @return: list of observation durations
    ''' 
    def extractDuration(self, file):

        data_set = nc.Dataset(file)
        status_code = '0' # If no errors occoured in the data extraction, the status code is 0
        duration_list = []

        # Boolean whether all entries are errors
        all_errors = True

        try:
            duration_ndarray = data_set['EffectiveDuration'][:] 

            # Decoding scan durations from a numpy.ndarray and adding to a list
            for element in duration_ndarray:

                try:
                    # Converting duration to a string to avoid error
                    duration_list.append(str(element))

                    all_errors = False

                # If an error occoured during the decoding of data the entry is changed to Err
                except Exception:
                    status_code = '1' # If some errors occoured in the data extraction, the status code is 1
                    duration_list.append('Err')

            # Converting the list to an empty list if all entries are errors 
            if all_errors == True:
                status_code = '2' # If a fatal error occoured in the data extraction, the status code is 2
                duration_list = []
        
        # If an error occours an empty list is returned
        except Exception:
            status_code = '2' # If a fatal error occoured in the data extraction, the status code is 2
            duration_list = []
            
        return duration_list, status_code

    '''
    @extractSource: reads the sources from a NetCDF file into a list

    @param self: instance variable of the class, ReadNetCDF4
    @param file: NetCDF file containing sources
    @return: list of sources
    ''' 
    def extractSource(self, file):

        data_set = nc.Dataset(file)
        status_code = '0' # If no errors occoured in the data extraction, the status code is 0
        source_list = []

        # Boolean whether all entries are errors
        all_errors = True

        try:
            source_ndarray = data_set['Source'][:]
            
            for element in range(0, len(source_ndarray)):

                try:
                    source = ''

                    # Decoding sources from a numpy.ndarray and adding to a list
                    for character in source_ndarray[element]:
                        source = source + str(character.decode('UTF-8'))
                        
                    # Changing the source name back to its IAU name if its labelled under its IVS common name
                    if source in source_data.common:
                        source = source_data.name[source_data.common.index(source)]
                    
                    # If the source is not in the common name or IAU name list, the program will 
                    if source not in source_data.name and source not in source_data.common:
                        self.missing_source = True

                    source_list.append(source)

                    all_errors = False
                
                # If an error occoured during the decoding of data the entry is changed to Err
                except Exception:
                    status_code = '1' # If some errors occoured in the data extraction, the status code is 1
                    source_list.append('Err')

            # Converting the list to an empty list if all entries are errors 
            if all_errors == True:
                status_code = '2' # If a fatal error occoured in the data extraction, the status code is 2
                source_list = []
        
        # If an error occours an empty list is returned
        except Exception:
            status_code = '2' # If a fatal error occoured in the data extraction, the status code is 2
            source_list = []
    
        return source_list, status_code
    
    '''
    @extractBaseline: reads the baselines from a NetCDF file into a list

    @param self: instance variable of the class, ReadNetCDF4
    @param file: NetCDF file containing baselines
    @return: list of baselines
    ''' 
    def extractBaseline(self, file):

        data_set = nc.Dataset(file)
        status_code = '0' # If no errors occoured in the data extraction, the status code is 0
        baseline_list = []

        # Boolean whether all entries are errors
        all_errors = True
        
        try:
            baseline_ndarray = data_set['Baseline'][:]

            for character in range(0, len(baseline_ndarray)):

                try:
                    station1 = ''
                    station2 = ''
            
                    # Decoding baselines from a numpy.ndarray and adding to a list
                    for element in baseline_ndarray[character][0]:
                        station1 += str(element.decode('UTF-8'))

                    # Replacing spaces with underscores in the unlikely event of stations having spaces within their name
                    if len(station1.rstrip().split(' ')) != 0:
                        station1 = station1.rstrip().replace(' ', '_') + station1.replace(station1.rstrip(), '')
                        
                    for element in baseline_ndarray[character][1]:
                        station2 += str(element.decode('UTF-8'))

                    # Replacing spaces with underscores in the unlikely event of stations having spaces within their name
                    if len(station2.rstrip().split(' ')) != 0:
                        station2 = station2.rstrip().replace(' ', '_') + station2.replace(station2.rstrip(), '')

                    if station1 not in station_data.name or station2 not in station_data.name:
                        self.missing_station = True
            
                    baseline_list.append((station1, station2))

                    all_errors = False

                # If an error occoured during the decoding of data the entry is changed to Err
                except Exception:
                    status_code = '1' # If some errors occoured in the data extraction, the status code is 1
                    baseline_list.append(('Err','Err'))

            # Converting the list to an empty list if all entries are errors 
            if all_errors == True:
                status_code = '2' # If a fatal error occoured in the data extraction, the status code is 2
                baseline_list = []
        
        # If an error occours an empty list is returned
        except Exception:
            status_code = '2' # If a fatal error occoured in the data extraction, the status code is 2
            baseline_list = []
        
        return baseline_list, status_code

    '''
    @extractQC: reads the quality codes (QC) from a NetCDF file into a list

    @param self: instance variable of the class, ReadNetCDF4
    @param file: NetCDF file containing quality codes
    @return: list of quality codes
    ''' 
    def extractQC(self, file):

        data_set = nc.Dataset(file)
        status_code = '0' # If no errors occoured in the data extraction, the status code is 0
        qc_list = []

        # Boolean whether all entries are errors
        all_errors = True
        
        try:
            qc_ndarray = data_set['QualityCode'][:] 
            
            # Decoding quality codes from a numpy.ndarray and adding to a list
            for element in qc_ndarray:
                
                try:
                    # Converting the quality code to a string to avoid possible error
                    qc_list.append(str(element.decode('UTF-8')))

                    all_errors = False
                
                # If an error occoured during the decoding of data the entry is changed to Err
                except Exception:
                    status_code = '1' # If some errors occoured in the data extraction, the status code is 1
                    qc_list.append('Err')

            # Converting the list to an empty list if all entries are errors 
            if all_errors == True:
                status_code = '2' # If a fatal error occoured in the data extraction, the status code is 2
                qc_list = []
        
        # If an error occours an empty list is returned
        except Exception:
            status_code = '2' # If a fatal error occoured in the data extraction, the status code is 2
            qc_list = []

        return qc_list, status_code
    
    '''
    @extractSNR: reads the signal to noise ratios (SNR) from a NetCDF file into a list

    @param self: instance variable of the class, ReadNetCDF4
    @param file: NetCDF file containing signal to noise ratios
    @return: list of signal to noise ratios
    '''
    def extractSNR(self,file):

        data_set = nc.Dataset(file)
        status_code = '0' # If no errors occoured in the data extraction, the status code is 0
        snr_list = []

        # Boolean whether all entries are errors
        all_errors = True

        try:
            snr_ndarray = data_set['SNR'][:]
            # Decoding signal to noise ratios from a numpy.ndarray and adding to a list
            for element in snr_ndarray:
                
                try:
                    snr_list.append(float(element))

                    all_errors = False
                
                # If an error occoured during the decoding of data the entry is changed to Err
                except Exception:
                    status_code = '1' # If some errors occoured in the data extraction, the status code is 1
                    snr_list.append('Err')

            # Converting the list to an empty list if all entries are errors 
            if all_errors == True:
                status_code = '2' # If a fatal error occoured in the data extraction, the status code is 2
                snr_list = []
        
        # If an error occours an empty list is returned
        except Exception:
            status_code = '2' # If a fatal error occoured in the data extraction, the status code is 2
            snr_list = []
            
        return snr_list, status_code

    '''
    @extractChannelInfo: reads the channelwise amplitude and phase from a NetCDF file into a list

    @param self: instance variable of the class, ReadNetCDF4
    @param : NetCDF file containing the channel infomation
    @return: a list of channelwise amplitudes and a list of channelwise phases for each observation
    ''' 
    def extractChannelInfo(self, file):

        data_set = nc.Dataset(file)
        amplitude_status_code = '0' # If no errors occoured in the data extraction, the status code is 0
        phase_status_code = '0'
        channelwise_amplitude_list = []
        channelwise_phase_list = []

        # Boolean whether all entries are errors
        amplitude_all_errors = True
        phase_all_errors = True

        try:
            channelwise_amplitude_phase_ndarray = data_set['ChanAmpPhase'][:]

            # Decoding channel amplitude and phase from a numpy.ndarray and adding to a list
            for element in channelwise_amplitude_phase_ndarray:

                amplitude_list = []
                phase_list = []

                # Each element contains a list of phase and amplitude for each of the 32 channels
                for channel in element:

                    try:
                        amplitude_list.append(float(channel[0]))
                    
                        amplitude_all_errors = False

                    # If an error occoured during the decoding of data the entry is changed to Err
                    except Exception:
                        amplitude_status_code = '1' # If some errors occoured in the data extraction, the status code is 1
                        amplitude_list.append('Err')
                       
                    try:    
                        phase_list.append(float(channel[1]))

                        phase_all_errors = False

                    # If an error occoured during the decoding of data the entry is changed to Err
                    except Exception:
                        phase_status_code = '1' # If some errors occoured in the data extraction, the status code is 1
                        phase_list.append('Err')

                channelwise_amplitude_list.append(amplitude_list)
                channelwise_phase_list.append(phase_list)

                # Determining the observing mode
                if amplitude_all_errors == False:
                    if len(amplitude_list) == 32:
                        self.observing_mode = 'VGOS'

                    else:
                        self.observing_mode = 'S/X'

                else:
                    self.observing_mode = ''

            # Converting the list to an empty list if all entries are errors 
            if amplitude_all_errors == True:
                status_code = '2' # If a fatal error occoured in the data extraction, the status code is 2
                channelwise_amplitude_list = []

            if phase_all_errors == True:
                status_code = '2' # If a fatal error occoured in the data extraction, the status code is 2
                channelwise_phase_list = []
        
        # If an error occours empty lists are returned
        except Exception:
            status_code = '2' # If a fatal error occoured in the data extraction, the status code is 2
            channelwise_amplitude_list = []
            channelwise_phase_list = []

        return channelwise_amplitude_list, channelwise_phase_list, amplitude_status_code, phase_status_code

    '''
    @extractSourceInfo: reads the source names, source coordinates and source references for all the sources used in the session from a NetCDF file into a list

    @param self: instance variable of the class, ReadNetCDF4
    @param file: NetCDF file containing source information
    @return: lists of source names, source right ascension coordinated, source declination coordinates and source references
    ''' 
    def extractSourceInfo(self, file):

        data_set = nc.Dataset(file)
        names_status_code = '0' # If no errors occoured in the data extraction, the status code is 0
        right_ascensions_status_code = '0'
        declinations_status_code = '0'
        references_status_code = '0'
        
        # Lists of source data
        source_names = []
        source_right_ascensions = []
        source_declinations = []
        source_references = []

        # Boolean whether all entries are errors
        names_all_errors = True
        right_ascensions_all_errors = True
        declinations_all_errors = True
        references_all_errors = True

        # Reading the three different variables from the masked array
        try:                
            source_ndarray = data_set['AprioriSourceList'][:]
                
            for element in source_ndarray:

                try:           
                    source_name = ''

                    # Decoding source name from a numpy.ndarray and adding to the list
                    for character in element:
                        source_name += str(character.decode('UTF-8'))

                    source_names.append(source_name)

                    names_all_errors = False
                
                # If an error occoured during the decoding of data the entry is changed to Err
                except Exception:
                    names_status_code = '1' # If some errors occoured in the data extraction, the status code is 1
                    source_names.append('Err')
                
            source_ndarray = data_set['AprioriSource2000RaDec'][:]
                
            for element in source_ndarray:
                    
                try:
                    source_right_ascensions.append(float(element[0])) # Note the right ascension coordinate is in radians
                    
                    right_ascensions_all_errors = False

                # If an error occoured during the decoding of data the entry is changed to Err
                except Exception:
                    right_ascensions_status_code = '1' # If some errors occoured in the data extraction, the status code is 1
                    source_right_ascensions.append('Err')

                try:    
                    source_declinations.append(float(element[1])) # Note the declination coordinate is in radians

                    declinations_all_errors = False

                # If an error occoured during the decoding of data the entry is changed to Err
                except Exception:
                    declinations_status_code = '1' # If some errors occoured in the data extraction, the status code is 1
                    source_declinations.append('Err')

            source_ndarray = data_set['AprioriSourceReference'][:]
                
            for element in source_ndarray:
                    
                try:
                    source_reference = ''

                    # Decoding source reference from a numpy.ndarray and adding to the list
                    for character in element:
                            
                        # Only decoding if the character is not '--'
                        if character != b'--' and character != b' ':
                            source_reference += str(character.decode('UTF-8'))

                    source_references.append(source_reference)

                    references_all_errors = False

                # If an error occoured during the decoding of data the entry is changed to Err
                except Exception:
                    references_status_code = '1' # If some errors occoured in the data extraction, the status code is 1
                    source_references.append('Err')            
            
            # Converting the list to an empty list if all entries are errors 
            if names_all_errors == True:
                names_status_code = '2' # If a fatal error occoured in the data extraction, the status code is 2
                source_names = []
            
            # Converting the list to an empty list if all entries are errors 
            if right_ascensions_all_errors == True:
                right_ascensions_status_code = '2' # If a fatal error occoured in the data extraction, the status code is 2
                source_right_ascensions = []

            # Converting the list to an empty list if all entries are errors 
            if declinations_all_errors == True:
                declinations_status_code = '2' # If a fatal error occoured in the data extraction, the status code is 2
                source_declinations = []

            # Converting the list to an empty list if all entries are errors 
            if references_all_errors == True:
                references_status_code = '2' # If a fatal error occoured in the data extraction, the status code is 2
                source_references = []

        # If an error occours empty lists are returned
        except Exception:
            names_status_code = '2' # If a fatal error occoured in the data extraction, the status code is 2
            right_ascensions_status_code = '2'
            declinations_status_code = '2'
            references_status_code = '2'
            source_names = []
            source_right_ascensions = []
            source_declinations = []
            source_references = []
            
        return source_names, source_right_ascensions, source_declinations, source_references, names_status_code, right_ascensions_status_code, declinations_status_code, references_status_code
    
    '''
    @extractStationInfo: reads the station names and station coordinates for all the stations used in the session from a NetCDF file into a list

    @param self: instance variable of the class, ReadNetCDF4
    @param file: NetCDF file containing station information
    @return: lists of station names and station cartesian coordinates
    ''' 
    def extractStationInfo(self, file):

        data_set = nc.Dataset(file)
        names_status_code = '0' # If no errors occoured in the data extraction, the status code is 0
        coordinates_status_code = '0'

        # Lists of source data
        station_names = []
        station_cartesian_coordinates = []

        # Boolean whether all entries are errors
        names_all_errors = True
        coordinates_all_errors = True

        # Reading the two different variables from the masked array
        try:
                
            station_ndarray = data_set['AprioriStationList'][:]
                
            for element in station_ndarray:

                try:
                    station_name = ''

                    # Decoding source name from a numpy.ndarray and adding to the list
                    for character in element:
                        station_name += str(character.decode('UTF-8'))

                    station_names.append(station_name)

                    names_all_errors = False

                # If an error occoured during the decoding of data the entry is changed to Err
                except Exception:
                    names_status_code = '1' # If some errors occoured in the data extraction, the status code is 1
                    station_names.append('Err')

            station_ndarray = data_set['AprioriStationXYZ'][:]
                
            for element in station_ndarray:

                try:                        
                    coordinates = []

                    # Adding each of the three coordinates to a list
                    for coordinate in element:
                        coordinates.append(float(coordinate))

                    station_cartesian_coordinates.append(coordinates)

                    coordinates_all_errors = False

                # If an error occoured during the decoding of data the entry is changed to Err
                except Exception:
                    coordinates_status_code = '1' # If some errors occoured in the data extraction, the status code is 1
                    station_cartesian_coordinates.append('Err')

            # Converting the list to an empty list if all entries are errors 
            if names_all_errors == True:
                names_status_code = '2' # If a fatal error occoured in the data extraction, the status code is 2
                station_names = []

            # Converting the list to an empty list if all entries are errors 
            if coordinates_all_errors == True:
                coordinates_status_code = '2' # If a fatal error occoured in the data extraction, the status code is 2
                station_cartesian_coordinates = []

        # If an error occours empty lists are returned
        except Exception:
            names_status_code = '2' # If a fatal error occoured in the data extraction, the status code is 2
            coordinates_status_code = '2'
            station_names = []
            station_cartesian_coordinates = []
            
        return station_names, station_cartesian_coordinates, names_status_code, coordinates_status_code

    '''
    @get_observing_mode: grabs the observing mode

    @param self: instance variable of the class, ReadNetCDF4
    @return: the observing mode
    '''
    def get_observing_mode(self):
        return self.observing_mode

    '''
    @get_session_code: grabs the session code

    @param self: instance variable of the class, ReadNetCDF4
    @return: the session code
    '''
    def get_session_code(self):
        return self.session_code
    
    '''
    @get_observation_time_UTC_list: grabs the list of UTC times

    @param self: instance variable of the class, ReadNetCDF4
    @return: the UTC time list
    '''
    def get_observation_time_UTC_list(self):
        return self.observation_time_UTC_list
    
    '''
    @get_observation_duration_bX_list: grabs the list of scan durations for X band

    @param self: instance variable of the class, ReadNetCDF4
    @return: the list of durations
    '''
    def get_observation_duration_bX_list(self):
        return self.observation_duration_bX_list
    
    '''
    @get_observation_source_list: grabs the list of sources

    @param self: instance variable of the class, ReadNetCDF4
    @return: the list of sources
    '''
    def get_observation_source_list(self):
        return self.observation_source_list
    
    '''
    @get_observation_baselines_list: grabs the list of baselines

    @param self: instance variable of the class, ReadNetCDF4
    @return: the list of baselines
    '''
    def get_observation_baselines_list(self):
        return self.observation_baselines_list
    
    '''
    @get_observation_QC_bX_list: grabs the list of quality codes from the X band

    @param self: instance variable of the class, ReadNetCDF4
    @return: the list of quality codes
    '''
    def get_observation_QC_bX_list(self):
        return self.observation_QC_bX_list
    
    '''
    @get_observation_QC_bS_list: grabs the list of quality codes from the S band

    @param self: instance variable of the class, ReadNetCDF4
    @return: the list of quality codes
    '''
    def get_observation_QC_bS_list(self):
        return self.observation_QC_bS_list
    
    '''
    @get_observation_SNR_bX_list: grabs the list of signal to noise ratios from the X band

    @param self: instance variable of the class, ReadNetCDF4
    @return: the list of signal to noise ratios
    '''
    def get_observation_SNR_bX_list(self):
        return self.observation_SNR_bX_list
    
    '''
    @get_observation_SNR_bS_list: grabs the list of signal to noise ratios from the S band

    @param self: instance variable of the class, ReadNetCDF4
    @return: the list of signal to noise ratios
    '''
    def get_observation_SNR_bS_list(self):
        return self.observation_SNR_bS_list
    
    '''
    @get_observation_channelwise_amplitude: grabs the list of channelwise amplitude

    @param self: instance variable of the class, ReadNetCDF4
    @return: the list of channelwise amplitudes
    '''
    def get_observation_channelwise_amplitude(self):
        return self.observation_channelwise_amplitude
    
    '''
    @get_observation_channelwise_phase: grabs the list of channelwise amplitude

    @param self: instance variable of the class, ReadNetCDF4
    @return: the list of channelwise amplitudes
    '''
    def get_observation_channelwise_phase(self):
        return self.observation_channelwise_phase
    
    '''
    @get_source_name_list: grabs the list of source names that participated in the session

    @param self: instance variable of the class, ReadNetCDF4
    @return: the list of participating source names
    '''
    def get_source_name_list(self):
        return self.source_name_list
    
    '''
    @get_source_right_ascension_list: grabs the list of the right ascension coordinates of the sources that participated in the session

    @param self: instance variable of the class, ReadNetCDF4
    @return: the list of participating source right ascensions
    '''
    def get_source_right_ascension_list(self):
        return self.source_right_ascension_list
    
    '''
    @get_source_declination_list: grabs the list of the declination coordinates of the sources that participated in the session

    @param self: instance variable of the class, ReadNetCDF4
    @return: the list of participating source declinations
    '''
    def get_source_declination_list(self):
        return self.source_declination_list
    
    '''
    @get_source_reference_list: grabs the list of the dreferences of the sources that participated in the session

    @param self: instance variable of the class, ReadNetCDF4
    @return: the list of participating source references
    '''
    def get_source_reference_list(self):
        return self.source_reference_list

    '''
    @get_station_name_list: grabs the list of station names that participated in the session

    @param self: instance variable of the class, ReadNetCDF4
    @return: the list of participating station names
    '''
    def get_station_name_list(self):
        return self.station_name_list
    
    '''
    @get_station_cartesian_coordinates_list: grabs the list of the Cartesian coordinates of the stations that participated in the session

    @param self: instance variable of the class, ReadNetCDF4
    @return: the list of participating station Cartesian coordinates
    '''
    def get_station_cartesian_coordinates_list(self):
        return self.station_cartesian_coordinates_list
    
    '''
    @get_status_codes: grabs the status codes of all the data extractions

    @param self: instance variable of the class, ReadNetCDF4
    @return: the list of status codes
    '''
    def get_status_codes(self):
        
        # Calculating the missing data status code
        if self.missing_source == True and self.missing_station == True:
            self.status_code_missing_data = '5' # A status code of 5 is returned if missing source and station information is detected

        elif self.missing_station == True:
            self.status_code_missing_data = '4' # A status code of 4 is returned if missing station information is detected
        
        elif self.missing_source == True:
            self.status_code_missing_data = '3' # A status code of 3 is returned if missing source information is detected

        return {
        'UTC time': self.status_code_time_UTC,
        'duration': self.status_code_duration_bX,
        'source': self.status_code_source,
        'baseline': self.status_code_baseline,
        'quality code (X)': self.status_code_QC_bX,
        'quality code (S)': self.status_code_QC_bS, 
        'signal to noise ratio (X)': self.status_code_SNR_bX,
        'signal to noise ratio (S)': self.status_code_SNR_bS,
        'channelwise amplitude': self.status_code_channelwise_amplitude,
        'channelwise phase': self.status_code_channelwise_phase,
        'missing data': self.status_code_missing_data,
        'missing source name': self.status_code_source_name,
        'missing source right ascension': self.status_code_right_ascension,
        'missing source declination': self.status_code_declination,
        'missing source reference': self.status_code_reference,
        'missing station name': self.status_code_station_name,
        'missing station coordinate': self.status_code_station_coordinates,
        }

    mode = property(get_observing_mode)
    session = property(get_session_code)
    time_utc = property(get_observation_time_UTC_list)
    duration_bX = property(get_observation_duration_bX_list)
    source = property(get_observation_source_list)
    baseline = property(get_observation_baselines_list)
    qc_bX = property(get_observation_QC_bX_list)
    qc_bS = property(get_observation_QC_bX_list)
    snr_bX = property(get_observation_SNR_bX_list)
    snr_bS = property(get_observation_SNR_bX_list)
    chan_amp = property(get_observation_channelwise_amplitude)
    chan_phase = property(get_observation_channelwise_phase)
    source_name = property(get_source_name_list)
    source_ra = property(get_source_right_ascension_list)
    source_dc = property(get_source_declination_list)
    source_ref = property(get_source_reference_list)
    station_name = property(get_station_name_list)
    station_xyz = property(get_station_cartesian_coordinates_list)
    status_code = property(get_status_codes)
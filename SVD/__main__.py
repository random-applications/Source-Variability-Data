#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Zachary Allen
@supervisor: Tirge McCarthy
@function: Main method of SVD. Calls all classes and relevant functions, as well as calls for user input and outputs status messages
'''

import os
import math
import argparse
import importlib
import astropy
from astropy import coordinates
from astropy.coordinates import Angle
from decimal import Decimal
from collections import Counter
from astropy.table import Table
from datetime import datetime
from ftplib import FTP_TLS
from numerical import NumberMethods
from geodeticData import ExtractSourceCatalogue, ExtractStationCatalogue
from extractFile import ExtractTGZ
from extractData import ReadNetCDF4
from secondaryData import ToBandwiseSNR, FindProjection, ToTimeMJD
from formatData import CreateTextFile

number_functions  = NumberMethods()

# Geodetic source and station data
source_data = ExtractSourceCatalogue()
station_data = ExtractStationCatalogue()

# Path to folder containing text files with all current session codes
SESSION_CODE_FILE = os.path.dirname(__file__) + '\\Session Codes'

# Server containing the VgosDB's
SERVER = 'gdc.cddis.eosdis.nasa.gov'

class MainMethod:

    '''
    @__init__: MainMethod class constructor

    @param self: instance variable of the class, MainMethod
    '''
    def __init__(self):   

        # Whether or not to allow for user input
        allow_user_input = False

        # List of VGOS DB file names that have been matched to session codes
        matched_files= []

        # Program boolean checks
        continue_application = True
        calculate_projection = False

        # Stages of program completion
        valid_session_code_entry = False
        server_found = False
        valid_server_recall_entry = False
        matched_all_session_codes = False
        download_successful = False
        valid_download_retry_entry = False
        valid_continue_application_entry = False

        # User entry's
        session_code_entry = ''
        server_recall_entry = ''
        download_retry_entry = ''
        continue_application_entry = ''

        # List of enterred session codes
        enterred_session_code_list = []

        # Command line argument specifications contructor
        parser = argparse.ArgumentParser(
            prog = 'SOURCE VARIABILITY DATA',
            usage = f'\n  python "{os.path.dirname(__file__)}" [-h] [-p] [session codes...]',
            description = 'description: \n  SVD Takes a Geodetic VLBI session code and extracts data from the relevant vgosDB \n  into a text file.',
            epilog = 'Thankyou for using the SVD application',
            formatter_class = argparse.RawTextHelpFormatter,
            exit_on_error = False
        )
        
        # Adding the session code argument to the command line. If nothing is enterred, the program asks for user input
        parser.add_argument(
            'session_codes', 
            nargs='?',
            const='',
            help = 'name of the Geodetic VLBI session of which data is to be extracted \nSVD takes between zero and infinitely many session codes as input'
        )
        
        # Adding the optional projection selection argument to the command line.
        parser.add_argument(
            '-p',
            '--projection', 
            help = 'specify calculation of projcted baseline angles and lengths',
            action= 'store_true'
        )
        
        # Running the parser. If there are more than one session codes added, these will be put into the spillover list
        args, spillover = parser.parse_known_args()
        
        # Creating list of user enterred session codes if they exist
        if args.session_codes:
            enterred_session_code_list = [args.session_codes]
        
        # Adding remaining session codes to the list if they exist
        if spillover:
            enterred_session_code_list += spillover
        
        # Selecting projection to be calculated if selected
        if args.projection:
            calculate_projection = True

        # If no session codes have been enterred the program proceeds to ask for user input
        if args.session_codes == None:

            # Allowing user input
            allow_user_input = True

            print('-' * 32 + 'SOURCE VARIABILITY DATA' + '-' * 32)
            print('Type "help" for more information or type "quit" to end this application\n')
            print('-' * 87)

            # Only displaying text explaining projections if it has not already been specified
            if calculate_projection == False:
                print('Note that by default, SVD will not calculate baseline projection angles or lengths as \nthe computations take significant time. To enable calculation of projections, type \n"projection" after enterring the VgosDB session code(s).\n')
            
            # Otherwise reminding the user that projections have been specified
            else:
                print('Note that SVD will calculate baseline projection angles and lengths, of which the \ncomputations will take significant time.\n')

            print('Warning, SVD only accepts session codes in the VGOS format.')
            print('To compile data for multiple VgosDB sessions, separate individual entries by a space (" ").')
            print('-' * 87 + '\n')

            # Passing the users entry through stage one of processing.
            while valid_session_code_entry == False and continue_application == True:

                session_code_entry = input('Enter VgosDB session code(s):\n> ').lower()

                # Testing if the entry is "quit"
                if 'quit' in session_code_entry or session_code_entry == '':
                    continue_application = False

                # Testing if the entry is "help"
                elif 'help' in session_code_entry:
                    HelpMethod()

                # Testing if the entry specified "projection"
                elif 'projection' in session_code_entry:
                    calculate_projection = True
                    valid_session_code_entry = True

                    # Removeing the text "projection" from the entry
                    session_code_entry = session_code_entry.replace('projection','')

                # If the entry is not "quit" or "help" the 
                else:
                    valid_session_code_entry = True

            # Creating a list of session codes from the users entry
            if continue_application == True:

                # Splitting the entry over the spaces and removing empty entries to create a list of the selected sessions
                enterred_session_code_list = [code for code in session_code_entry.upper().split(' ') if code != '']
        
        if continue_application == True:
            
            # Eliminating duplicate entries of enterred code list
            enterred_session_code_list = [code for code, count in Counter(enterred_session_code_list).items() if count == 1]

            # List of downloaded files
            vgosDB_file_SVD_list = os.listdir(os.path.dirname(__file__) + '\\VgosDB')

            # Checking that the sessions VGOS DB file has not already been downloaded and extracted
            for file in vgosDB_file_SVD_list:

                # Looping through all enterred session codes
                for enterred_session_code in enterred_session_code_list:

                    # Determining if any of the enterred VgosDB codes lie in the list of files
                    if enterred_session_code.lower() in file.lower() and file[-4:] != '.tgz': # TODO REMOVE .lower() ONCE CAPITISATION RENAME HAS WORKED

                        print(f'Found match for {enterred_session_code} in VgosDB file folder')

                        # Adding the file name to the list of matched files
                        matched_files.append(file.lower())
                                
                        # Removing the matched code from the code_list
                        enterred_session_code_list.remove(enterred_session_code)

                    if len(enterred_session_code_list) == 0:
                        break
                    
                if len(enterred_session_code_list) == 0:
                    break
            
            # If all files have been already downloaded and extracted, the next stages of the program do not need to run
            if len(enterred_session_code_list) == 0:
                server_found = True
                valid_server_recall_entry = True
                matched_all_session_codes = True
                download_successful = True
                valid_download_retry_entry = True
                valid_continue_application_entry = True 

        # Requesting the server
        while server_found == False and continue_application == True:

            # Loading the required directory in the server
            try:

                print(f'Requesting the {SERVER} server...')
                
                # Requesting the server
                ftps = FTP_TLS(host = SERVER)

                # Anonymously logging into the ftp server        
                ftps.login()
                            
                # Securing the data connection
                ftps.prot_p()

                # Sending a response string to the server, for all data to be converted to binary
                ftps.sendcmd('TYPE I')

                # Navigating to the directory of VgosDB's per year
                ftps.cwd('pub/vlbi/ivsdata/vgosdb')
                        
                # If the server calls successfully run without error, the server is said to be found
                server_found = True

                # Finding the year in which the program is currently running
                current_year = datetime.now().year
                
                # Adding missing session code files to the session code folder
                for year in range(2023, current_year+1):
                    
                    session_code_file_path = os.path.dirname(__file__) + '\\Session Codes' + '\\session.codes.' + str(year) + '.catalogue'

                    # As all the current years sessions are unlikely to be complete
                    if year == current_year:
                        session_code_file_path = os.path.dirname(__file__) + '\\Session Codes' + '\\session.codes.incomplete.' + str(year) + '.catalogue'
                        
                    # Checking if the years folder is incomplete
                    if year != current_year and f'session.codes.incomplete.{year}.catalogue' in os.listdir(os.path.dirname(__file__) + '\\Session Codes'):
                        
                        # Removing the incomplete file
                        os.remove(os.path.dirname(__file__) + '\\Session Codes' + '\\session.codes.incomplete.' + str(year) + '.catalogue')
                    
                    # Determining if the session code folder for that year exists in the folder
                    if f'session.codes.{year}.catalogue' not in os.listdir(os.path.dirname(__file__) + '\\Session Codes'):

                        # Navigating to that years directory in the server
                        ftps.cwd(str(year))
                        
                        # Writing an empty session code file
                        with open(session_code_file_path, 'w') as file_write:
                            file_write.write('')
                        
                        # List of files in that years directory
                            file_list = ftps.nlst()
                        
                        # Opening the session code file for appending
                        with open(session_code_file_path, 'a') as file_append:

                            # Looping through all files in the list
                            for session_code in file_list:
                                
                                # Making sure the session code is valid
                                if len(session_code) >= 9 and session_code[:4] == str(year):

                                    # Adding a new line if the session code is not the first one in the list
                                    if session_code != file_list[0]:
                                        file_append.write('\n')

                                    # Appending the session code, and ommiting '.tgz' from the end of the file to get the session code
                                    file_append.write(session_code[:-4].upper())

                        # Changing the directory back from the specific year to the list of years
                        ftps.cwd('..')
            
            except Exception as error:

                print('~' * 87)
                print(f'{error}! Internet connection failed, SVD could not request the required server.')
                print('~' * 87)

                # Only allowing user to recall the server if user input is specified
                if allow_user_input == True:

                    # Passing the users entry through stage two of processing
                    while valid_server_recall_entry == False and continue_application == True:

                        # Asking user if they want to re-request the server 
                        server_recall_entry = input('To recall the server, type "recall", to end the application type "quit":\n>  ').lower()
                                    
                        # Testing if the entry is "quit"
                        if 'quit' in server_recall_entry or server_recall_entry == '':
                            continue_application = False

                        # Testing if the entry is "help"
                        elif 'help' in server_recall_entry:
                            HelpMethod('4')

                        # Testing if the entry is "recall"
                        elif 'recall' in server_recall_entry:
                            valid_server_recall_entry = True

                        # Otherwise an error is thrown
                        else:
                            print('~' * 87)
                            print('[Error 400] Invalid Request! Your entry is invalid.')
                            print('~' * 87)

                # If user input is not specified the program ends
                else:
                    continue_application = False

        # Searching for a match for the enterred session codes
        while matched_all_session_codes == False and continue_application == True:

            print(f'Searching for a match for the session code(s) {MainMethod.concatList(enterred_session_code_list)}...')

            # Creating list of session code catalogs loaded into SVD
            session_code_catalogue_list = (os.listdir(SESSION_CODE_FILE))[::-1]
            
            # Looping through all the VgosDB's session codes in the directories to see if a match with the input is found
            for session_code_catalogue in session_code_catalogue_list:
                    
                # Converting the specified session_code_catalogue ascii table to a single-column data frame
                session_name_list = Table.read(
                    SESSION_CODE_FILE + '\\' + session_code_catalogue, 
                    format='ascii.csv',
                    delimiter = '\t',
                    data_start= 0,
                    names = ['VGOS DB format','Mk3 format']
                )
                
                # Looping through all session codes in the list
                for session_name_row in session_name_list:

                    # Only finding a match for the VGOS DB format of session code
                    session_name = str(session_name_row[0])
                    
                    # Looping through all the entered session codes
                    for session_code in enterred_session_code_list:
                        
                        # Determining if any of the enterred VgosDB codes lie in that list.
                        if session_code in session_name:

                            print(f'Found match for {session_code}')

                            # Extracting the year which the session comes from
                            year = session_name[:4]
                            
                            # Setting the name of the downloaded file to be the same as the VgosDB name
                            vgosDB_file_SVD_name = session_name
                            
                            # Setting path of the downloaded file
                            vgosDB_file_SVD_path = os.path.dirname(__file__) + '\\VgosDB\\' + vgosDB_file_SVD_name + '.tgz'

                            # List of downloaded files
                            vgosDB_file_SVD_list = os.listdir(os.path.dirname(__file__) + '\\VgosDB')

                            # Name of file in the server
                            vgosDB_file_server_name = ''

                            # Transforming session code to the old format if applicable and adding '.tgz' to turn into file name
                            if int(year) <= 2022:
                                vgosDB_file_server_name = session_name_row[1] + '.tgz'
                            
                            else:
                                vgosDB_file_server_name = session_name.lower() + '.tgz'
                            
                            # Checking that the VgosDB has not already been downloaded
                            if vgosDB_file_SVD_name + '.tgz' not in vgosDB_file_SVD_list and vgosDB_file_SVD_name not in vgosDB_file_SVD_list:
                                
                                download_successful = False

                                # Checking if the VGOS DB can be downloaded without errors
                                while download_successful == False and continue_application == True:
                                    
                                    # If the download has already been tried and failed, resetting
                                    if valid_download_retry_entry == True:
                                        valid_download_retry_entry = False

                                    try: 
                                        # Changing directory to the specified year
                                        ftps.cwd(year)
                                        
                                        print(f'Downloading {session_code} as "{vgosDB_file_SVD_name}.tgz"...')
                                        
                                        # Downloading the VgosDB to the VgosDB directory
                                        with open(vgosDB_file_SVD_path, 'wb') as download:
                                            ftps.retrbinary(f"RETR {vgosDB_file_server_name}", download.write)
                                        
                                        # Changing the directory back from the specific year to the list of years
                                        ftps.cwd('..')

                                        download_successful = True

                                    except Exception as error:

                                        print('~' * 87)
                                        print(f'{error} SVD failed to locate or download {vgosDB_file_SVD_name}')
                                        print('~' * 87)

                                        # Only allowing user to retry the download if user input is specified
                                        if allow_user_input == True:

                                            # Passing the users entry through stage four of processing
                                            while valid_download_retry_entry == False and continue_application == True:

                                                # Asking user if they want to re-request the server 
                                                download_retry_entry = input('To retry the download, type "retry", to end the application type "quit":\n> ').lower()
                                                            
                                                # Testing if the entry is "quit"
                                                if 'quit' in download_retry_entry or download_retry_entry == '':
                                                    continue_application = False

                                                # Testing if the entry is "help"
                                                elif 'help' in download_retry_entry:
                                                    HelpMethod('4')

                                                # Testing if the entry is "recall"
                                                elif 'retry' in download_retry_entry:
                                                    print('Retrying download...')
                                                    valid_download_retry_entry = True

                                                # Otherwise an error is thrown
                                                else:
                                                    print('~' * 87)
                                                    print('[Error 400] Invalid Request! Your entry is invalid.')
                                                    print('~' * 87)

                                        # If user input is not specified the program ends
                                        else:
                                            continue_application = False

                            # Checking that the VgosDB has not already been extracted
                            if vgosDB_file_SVD_name not in vgosDB_file_SVD_list and continue_application == True:
                                    
                                print(f'Extracting {vgosDB_file_SVD_name} from TGZ file format...')

                                # Current .tgz file name
                                vgosDB_tgzfile_SVD_name = vgosDB_file_server_name[:-4].upper()

                                # Destination directory for extracted file
                                vgosDB_folder_SVD_path = os.path.dirname(__file__) + '\\VgosDB'

                                # Extracting the file from TGZ format into the same directory, under the same name
                                ExtractTGZ(vgosDB_file_SVD_path, vgosDB_tgzfile_SVD_name, vgosDB_folder_SVD_path, vgosDB_file_SVD_name)

                            if continue_application == True:

                                # Adding the file name to the list of matched files
                                matched_files.append(vgosDB_file_SVD_name.lower()) # TODO REMOVE .lower() ONCE CAPITISATION RENAME HAS WORKED
                                
                                # Removing the matched code from the code_list
                                enterred_session_code_list.remove(session_code)

                        # Determining if all the session codes have been matched
                        if len(enterred_session_code_list) == 0 and continue_application == True:
                            matched_all_session_codes = True
                            break
                        
                        elif continue_application == False:
                            break

                    # Stopping the loop if all VgosDB's have been found
                    if matched_all_session_codes == True or continue_application == False:
                        break

                # Stopping the loop if all VgosDB's have been found
                if matched_all_session_codes == True or continue_application == False:
                    break
            
            # Checking if all codes have been matched
            if len(enterred_session_code_list) != 0 and continue_application == True:

                print('~' * 87)
                print(f'[Errno 2] No such file or directory! SVD could not match {MainMethod.concatList(enterred_session_code_list)}')
                print('~' * 87)

                # Only allowing the user to manually download if user input is specified
                if allow_user_input == True:
                            
                    while valid_continue_application_entry == False and continue_application == True:
                                
                        # Asking the user if they want to continue the apllication
                        continue_application_entry = input(f'To continue this application without these session(s) type "continue", to end the application type "quit":\n> ').lower()
                                
                        # Testing if the entry is "quit"
                        if 'quit' in continue_application_entry or continue_application_entry == '':
                            continue_application = False

                        # Testing if the entry is "help"
                        elif 'help' in continue_application_entry:
                            HelpMethod('5')
                                
                        elif 'continue' in continue_application_entry:
                            valid_continue_application_entry = True
                            matched_all_session_codes = True

                # If no user input is specified the program continues, skipping the unmatched session
                else:
                    matched_all_session_codes = True
        
        if continue_application == True:
            
            # Creating a text file of extracted relevant data for each sessions DB
            for session_directory in os.scandir(os.path.dirname(__file__) + '\\VgosDB'):
                
                # Making sure the session_directory is actually a directory and not a file
                if session_directory.is_dir() and session_directory.name.lower() in matched_files: # TODO REMOVE .lower() ONCE CAPITISATION RENAME HAS WORKED

                    print(f'Extracting data from {session_directory.name}...')
                    
                    # Extracting the data from the relevant files in the sessions VgosDB
                    extract = ReadNetCDF4(session_directory)
                    
                    # Scanning through all the status codes of the extracted lists to check if the data was all extracted successfully
                    for status_code_name in extract.status_code:
                        
                        # An error message is displayed if a fatal error occoured in the data extraction
                        if extract.status_code[status_code_name] == '2':
                            print(f'Error! SVD could not extract the {status_code_name} data')

                        # A warning message is displayed if some entries were errors
                        elif extract.status_code[status_code_name] == '1':
                            print(f'Warning! SVD detected invalid entries in the {status_code_name} data')
                        
                    # If a missing source was found adding it to the catalogue file
                    if extract.status_code['missing data'] == '3' or extract.status_code['missing data'] == '5':
                        
                        # Only proceeding if all the data was successfully extracted
                        if extract.status_code['missing source name'] == '0' and extract.status_code['missing source right ascension'] == '0' and extract.status_code['missing source declination'] == '0' and extract.status_code['missing source reference'] == '0':
                            
                            print('Formatting the missing sources...')

                            # Creating list of source names that are missing
                            missing_source_names = [name for name in extract.source_name if name not in source_data.name and name not in source_data.common]

                            # Creating corresponding list of right ascension coordinates
                            missing_source_right_ascensions = [extract.source_ra[extract.source_name.index(name)] for name in missing_source_names]

                            # Creating corresponding list of declinations coordinates
                            missing_source_declinations = [extract.source_dc[extract.source_name.index(name)] for name in missing_source_names]
                            
                            # Creating corresponding list of references
                            missing_source_references = [extract.source_ref[extract.source_name.index(name)] for name in missing_source_names]

                            # Opening the source text file for appending
                            with open(os.path.dirname(__file__) + '\\geodetic.source.catalogue', 'a') as source_file_append:

                                # Appending a title line
                                source_file_append.write(
                                    f'* Sources used in {extract.session[9:].upper()}/{extract.session[:4]} added {datetime.now().strftime('%d/%m/%Y')}\n'
                                )

                                # Formatting the data into new lines for the geodetic source data text file
                                for line in range(len(missing_source_names)):
                                    
                                    # Note that the common name will be used as the IAU name if only the common name is specified
                                    formatted_IAU_name = str(missing_source_names[line]) + ''.join([' ' for white_space in range(8-len(str(missing_source_names[line])))])
                                    
                                    # Adding the common name if the source name is labelled under the common name, otherwise '$' is added
                                    if '-' not in missing_source_names[line] and '+' not in missing_source_names[line]:
                                        formatted_common_name = formatted_IAU_name

                                    else:
                                        formatted_common_name = '$' + ' '*7

                                    # Converting right ascension from radians to hours-minutes-seconds
                                    right_ascension_hour, right_ascension_minute, right_ascension_second = number_functions.hours_minutes_seconds(math.degrees(missing_source_right_ascensions[line]))

                                    # Rounding the seconds to 6 decimal places
                                    rounded_right_ascension_seconds = number_functions.roundNumber(right_ascension_second, 6)

                                    # Formatting the right ascension coordinates
                                    formatted_right_ascension_hour = ''.join(['0' for zeros in range(2-len(str(right_ascension_hour)))]) + str(right_ascension_hour)
                                    formatted_right_ascension_minute = ''.join(['0' for zeros in range(2-len(str(right_ascension_minute)))]) + str(right_ascension_minute)
                                    formatted_right_ascension_second = ''.join(['0' for zeros in range(2-len(str(int(rounded_right_ascension_seconds))))]) + str(rounded_right_ascension_seconds) + ''.join([' ' for white_space in range(8-len(str( float(Decimal(str(rounded_right_ascension_seconds)) % 1) )))])

                                    # Converting declination from radians to hours-minutes-seconds
                                    declination_degrees, declination_minute, declination_second = number_functions.degrees_minutes_seconds(math.degrees(missing_source_declinations[line]))
                                    
                                    # Formatting the sign of the integer degrees
                                    if str(declination_degrees)[0] == '-': 
                                        sign = '-'

                                    # Otherwise a negative symbol is added
                                    else:
                                        sign = '+'

                                    # Rounding the seconds to 5 decimal places
                                    rounded_declination_seconds = number_functions.roundNumber(declination_second, 5)

                                    # Formatting the declination coordinates
                                    formatted_declination_degree = str(sign) + ''.join(['0' for zeros in range(2-len(str(abs(declination_degrees))))]) + str(abs(declination_degrees))
                                    formatted_declination_minute = ''.join(['0' for zeros in range(2-len(str(declination_minute)))]) + str(declination_minute)
                                    formatted_declination_second = ''.join(['0' for zeros in range(2-len(str(int(rounded_declination_seconds))))]) + str(rounded_declination_seconds) + ''.join([' ' for white_space in range(7-len(str( float(Decimal(str(rounded_declination_seconds)) % 1) )))]) #''.join([' ' for white_space in range(8-len(str(rounded_right_ascension_seconds-int(rounded_right_ascension_seconds))))])

                                    # Formatting the source reference
                                    formatted_source_reference = missing_source_references[line].replace(' ','').replace('-',' ')

                                    # Appending a new source line to the document
                                    source_file_append.write(
                                        ' ' 
                                        + formatted_IAU_name 
                                        + ' ' 
                                        + formatted_common_name 
                                        + '  ' 
                                        + formatted_right_ascension_hour 
                                        + ' ' 
                                        + formatted_right_ascension_minute 
                                        + ' ' 
                                        + formatted_right_ascension_second 
                                        + '     ' 
                                        + formatted_declination_degree
                                        + ' '
                                        + formatted_declination_minute
                                        + ' '
                                        + formatted_declination_second
                                        + ' 2000.0 0.0  '
                                        + formatted_source_reference
                                        + '\n'
                                    )
                                
                        # If errors occoured in data extraction
                        else:
                            print('Error! could not formatt missing sources')

                    # If a missing station was found adding it to the catalogue file
                    if extract.status_code['missing data'] == '4' or extract.status_code['missing data'] == '5':
                        
                        # Only proceeding if all the data was successfully extracted
                        if extract.status_code['missing station name'] == '0' and extract.status_code['missing station coordinate'] == '0':

                            print('Formatting the missing stations...')

                            # Creating list of station names that are missing
                            missing_station_names = [name for name in extract.station_name if name not in station_data.name]

                            # Creating corresponding list of station cartesian coordinates
                            missing_station_xyz = [extract.station_xyz[extract.station_name.index(name)] for name in missing_station_names]

                            # Opening the station text file for appending
                            with open(os.path.dirname(__file__) + '\\geodetic.station.catalogue', 'a') as station_file_append:

                                # Formatting the data into new lines for the geodetic source data text file
                                for line in range(len(missing_station_names)):

                                    # Formatting the station name
                                    formatted_name = str(missing_station_names[line]) + ''.join([' ' for white_space in range(8-len(str(missing_station_names[line])))])

                                    # Extracting the individual cartesian coordinates
                                    station_x, station_y, station_z = missing_station_xyz[line]

                                    # Rounding the cartesian coordinates
                                    rounded_station_x = number_functions.roundNumber(station_x, 4)
                                    rounded_station_y = number_functions.roundNumber(station_y, 4)
                                    rounded_station_z = number_functions.roundNumber(station_z, 4)

                                    # Formatting the cartesian coordinates
                                    formatted_station_x = ''.join([' ' for white_space in range(8-len(str(int(station_x))))]) + str(rounded_station_x) + ''.join(['0' for zeros in range(6-len(str( float(Decimal(str(abs(rounded_station_x))) % 1) )))])
                                    formatted_station_y = ''.join([' ' for white_space in range(8-len(str(int(station_y))))]) + str(rounded_station_y) + ''.join(['0' for zeros in range(6-len(str( float(Decimal(str(abs(rounded_station_y))) % 1) )))])
                                    formatted_station_z = ''.join([' ' for white_space in range(8-len(str(int(station_z))))]) + str(rounded_station_z) + ''.join(['0' for zeros in range(6-len(str( float(Decimal(str(abs(rounded_station_z))) % 1) )))])

                                    # Converting the cartesian coordinates to geodetic coordinates
                                    station_latitude, station_longitude = [float(Angle(coordinate).degree) for coordinate in coordinates.cartesian_to_spherical(*missing_station_xyz[line]) if type(coordinate) != astropy.units.quantity.Quantity]

                                    # Rounding the geodetic coordinates
                                    rounded_station_latitude = number_functions.roundNumber(station_latitude, 2)
                                    rounded_station_longitude = number_functions.roundNumber(station_longitude, 2)

                                    # Formatting the geodetic coordinates
                                    formatted_station_latitude = ''.join([' ' for white_space in range(4-len(str(int(station_latitude))))]) + str(rounded_station_latitude) + ''.join(['0' for zeros in range(4-len(str( float(Decimal(str(abs(rounded_station_latitude))) % 1) )))])
                                    formatted_station_longitude = ''.join([' ' for white_space in range(3-len(str(int(station_longitude))))]) + str(rounded_station_longitude) + ''.join(['0' for zeros in range(4-len(str( float(Decimal(str(abs(rounded_station_longitude))) % 1) )))])

                                    # Appending a new station line to the document
                                    station_file_append.write(
                                        '-- '
                                        + formatted_name
                                        + '    '
                                        + formatted_station_x
                                        + '   '
                                        + formatted_station_y
                                        + '   '
                                        + formatted_station_z
                                        + '   --------  '
                                        + formatted_station_longitude
                                        + ' '
                                        + formatted_station_latitude
                                        + ' -------\n'
                                    )
                    
                        # If errors occoured in data extraction
                        else:
                            print('Error! could not formatt missing stations')
                    
                    # Only calculating bandwise SNR if the bands have not already been separated
                    if extract.mode == 'VGOS':

                        print('Calculating bandwise SNR...')

                        # Only proceeding if some of the required data exists
                        if extract.status_code['signal to noise ratio (X)'] != '2' and extract.status_code['channelwise amplitude'] != '2' and extract.status_code['channelwise phase'] != '2':
                        
                            # Calculating a list of bandwise SNR for each observation
                            snr = ToBandwiseSNR(
                                extract.snr_bX,
                                extract.chan_amp,
                                extract.chan_phase
                            )

                            # Giving a warning message if not all values were successfully calculated
                            if extract.status_code['signal to noise ratio (X)'] == '1' or extract.status_code['channelwise amplitude'] == '1' or extract.status_code['channelwise phase'] == '1':
                                print('Warning! SVD detected invalid entries in the bandwise signal to noise ratio data')

                        else:
                            print('Error! insufficient data to calculate bandwise SNR')
                    
                    # Calculating projections only if specified
                    if calculate_projection == True:
                        
                        print('Calculating projection angles and lengths...')

                        # Only proceeding if some of the required data exists
                        if extract.status_code['UTC time'] != '2' and extract.status_code['source'] != '2' and extract.status_code['baseline'] != '2':
                            
                            # Reimporting the FindProjection class from the secondaryData module as the geodetic text files might have been modified
                            importlib.reload(importlib.import_module('secondaryData'))
                            FindProjection = getattr(importlib.import_module('secondaryData'), 'FindProjection')

                            # Calculating a list of projected baseline length and projected angle for each observation
                            projection = FindProjection(
                                extract.time_utc,
                                extract.source,
                                extract.baseline
                            )

                            # Giving a warning message if not all values were successfully calculated
                            if extract.status_code['UTC time'] == '1' or extract.status_code['source'] == '1' or extract.status_code['baseline'] == '1':
                                print('Warning! SVD detected invalid entries in the projection data')

                        else:
                            print('Error! insufficient data to calculate projections')

                    print('Converting UTC time to MJD time...')

                    # Only proceeding if some of the required data exists
                    if extract.status_code['UTC time'] != '2':
                        
                        # Converting the UTC time into MJD time
                        mjd = ToTimeMJD(
                            extract.time_utc
                        )

                        # Giving a warning message if not all values were successfully calculated
                        if extract.status_code['UTC time'] == '1':
                            print('Warning! SVD detected invalid entries in the MJD time data')

                    else:
                        print('Error! insufficient data to convert time into MJD format')

                    # Calculating the number of observations in the session
                    observation_number = len(extract.source)

                    # Creating list of data
                    data_list = []

                    # Creating header row
                    header_row = []

                    print('Formatting data...')
                    
                    # Formatting data into a list of lists
                    for observation in range(observation_number):

                        # Creating a new row for the data list
                        data_row = []

                        # Adding the session name
                        try: 
                            data_row.append(extract.session)

                            # Adding the entry to the header
                            if observation == 0:
                                header_row.append('SESSION')

                        except Exception: 
                            pass
                        
                        # Adding the observation time in mjd format
                        try: 
                            data_row.append(mjd.time[observation])

                            # Adding the entry to the header
                            if observation == 0:
                                header_row.append('TIME (MJD)')
                            
                        except Exception: 
                            pass

                        # Adding the X band observation duration
                        try: 
                            data_row.append(extract.duration_bX[observation])

                            # Adding the entry to the header
                            if observation == 0:
                                header_row.append('DURATION (s)')

                        except Exception: 
                            pass

                        # Adding the source observed for the observation
                        try: 

                            data_row.append(extract.source[observation])

                            # Adding the entry to the header
                            if observation == 0:
                                header_row.append('SOURCE')

                        except Exception: 
                            pass
                        
                        # Adding the baseline of the observation
                        for telescope in range(2):

                            try: 

                                data_row.append(extract.baseline[observation][telescope])

                                # Adding the entry to the header
                                if observation == 0:
                                    header_row.append(f'STATION {telescope + 1}')

                            except Exception: 
                                pass

                        
                        # Adding the X band quality code
                        try: 
                            data_row.append(extract.qc_bX[observation])

                            # Adding the entry to the header
                            if observation == 0:
                                if extract.mode == 'S/X':
                                    header_row.append('QC [X]')
                                else:
                                    header_row.append('QC')

                        except Exception: 
                            pass

                        # Adding bandwise quality code depending on the format
                        if extract.mode == 'S/X':

                            # Adding the S band quality code
                            try: 
                                data_row.append(extract.qc_bS[observation])

                                # Adding the entry to the header
                                if observation == 0:
                                    header_row.append('QC [S] (s)')

                            except Exception: 
                                pass

                        # Adding the X band SNR
                        try: 
                            data_row.append(extract.snr_bX[observation])

                            # Adding the entry to the header
                            if observation == 0:
                                if extract.mode == 'S/X':
                                    header_row.append('SNR [X]')
                                else:
                                    header_row.append('SNR [TOTAL]')

                        except Exception: 
                            pass

                        # Adding bandwise quality code depending on the format
                        if extract.mode == 'S/X':

                            # Adding the S band SNR
                            try: 
                                data_row.append(extract.snr_bS[observation])

                                # Adding the entry to the header
                                if observation == 0:
                                    header_row.append('SNR [S]')

                            except Exception: 
                                pass

                        else:

                            for band in range(4):

                                # Adding the S band SNR
                                try: 
                                    data_row.append(snr.bandwise[observation][band])

                                    # Adding the entry to the header
                                    if observation == 0:
                                        header_row.append(f'SNR [{['a', 'b', 'c', 'd'][band]}]')

                                except Exception: 
                                    pass

                        # Adding the projections if calculated
                        if calculate_projection == True:

                            # Adding projected baseline length
                            try: 
                                data_row.append(projection.baseline[observation])

                                # Adding the entry to the header
                                if observation == 0:
                                    header_row.append('BASELINE [PROJ.]')

                            except Exception: 
                                pass
                            
                            # Adding projected baseline angle
                            try: 
                                data_row.append(projection.angle[observation])

                                # Adding the entry to the header
                                if observation == 0:
                                    header_row.append('ANGLE [PROJ.]')

                            except Exception: 
                                pass

                        # Adding the data row to the data list
                        data_list.append(data_row)
                    
                    print(f'Writing data from {session_directory.name} to a text file...')

                    # Writing the data to a text file
                    CreateTextFile(
                        data_list,
                        os.path.dirname(__file__) + '\\Extracted Data',
                        extract.session,
                        header = header_row
                    )
                    print(f'The path to the text file is: {os.path.dirname(__file__) + '\\Extracted Data' + '\\' + extract.session}')

        # If the application was forceably closed
        if continue_application == False:
            print('Ending application...')

        # Closing remark for the application
        print('Thankyou for using the SVD application.\n')

    '''
    @concatList: returns elements in a list formatted into a string

    @param self: instance variable of the class, MainMethod
    @param file: list to be formatted
    @return: the list as a formatted string
    '''
    def concatList(item_list):

        item_string = ''

        # Looping through all items in the string
        for i in range(len(item_list)):

            # Adding the item to the formatted string
            item_string += str(item_list[i])

            # Determining if a comma deliminator should be used between items
            if len(item_list) > 2 and i + 2 < len(item_list):
                item_string += ', '

            # Determining if an 'and' should deliminate the items
            elif len(item_list) >= 2 and i + 2 == len(item_list):
                item_string += ' and '

        return item_string
    
class HelpMethod:

    '''
    @__init__: MainMethod class constructor

    @param self: instance variable of the class, HelpMethod
    @param index: a specific index of the menu to instantly select
    '''
    def __init__(self, index = 0):

        # Program boolean check
        continue_to_help = True

        # Displaying the opening message and allowing user input if no index selected
        if index == 0:
            print('-' * 39 + 'HELP MENU' + '-' * 39)
            print('Type "1" for more information about the session code')
            print('Type "2" for more information about the projections')
            print('Type "3" for more information about the output')
            print('Type "4" for more information about the CDDIS server error')
            print('Type "5" for more information about the matching process error')
            print('Type "quit" to close the help menu')
            print('-' * 87)

            while continue_to_help == True:
                
                help_menu_entry = input('help> ').lower().replace(' ','')

                # Testing if the entry is "quit"
                if 'quit' in help_menu_entry or help_menu_entry == '':
                    continue_to_help = False

                # Texting if the entry is "1", "2", "3", "4", "5" or "help" and selecting the correct output message
                elif help_menu_entry in ["1", "2", "3", "4", "5", "help"]:
                    print('-' * 87)
                    print(HelpMethod.helpMessage(self, help_menu_entry))
                    print('-' * 87)

                else:
                    print('Invalid entry')
                    print('-' * 87)
                    print(HelpMethod.helpMessage(self, help_menu_entry))
                    print('-' * 87)

        # If an index is specified, immediately navigate to the selected message
        else:
            print('-' * 87)
            print(HelpMethod.helpMessage(self,index))
            print('-' * 87)

    '''
    @helpMessage: returns the selected help message

    @param self: instance variable of the class, HelpMethod
    @param index: the selected index of the menu
    @return: a help message string
    '''
    def helpMessage(self, index):
    
        # Returning the chosen help message
        if index == "1":
            return 'The session code is a unique identifyer of each Geodetic VLBI session. They are usually \n4 to 6 digits long, formed from an assortment of numbers and letters (e.g. "VO3012"). \nTo find a full list of all session codes, open any of the yearly catalogue files in the \nsession codes folder in the SVD application folder. The collection of characters after \nthe dash (-) in the first column of each file is a session code (e.g. from \n"20191230-B19364", "B19364" is a session code) To learn more about these sessions, \nsearch "IVS VLBI SESSIONS" followed by the session code, in your web browser. \n\nTo enter multiple session codes, separate each code by a comma "," (e.g. to enter the \ncodes "VO3012" and "B19364", type "VO3012, B19364").'
        
        elif index == "2":
            return 'The calculation of projection angles and lengths for this program is a timely process, \nand can take a while to compute. By default, SVD will not compute the projections \nunless it is specified in the first user entry. To specify calculation of projections, \ntype "projection" after typing your session code(s) (e.g. for one code with projection\n type "VO3012 projection". For multiple codes with projection type \n"B19364, VO3012 projection") Note that if projection is specified, projections for all \nsessions will be calculated.'
        
        elif index == "3":
            return 'The SVD application will output source variability data for each individual session \nentered, in the form of a text file. The text files cn be found in the extracted data \nfolder in the SVD application folder. Each text file is labelled under its session name \nof which the session code is the second half (after the dash). The program will notify \nthe path to the text file once it has been written so that the data may be easily\n imported for use in other applications.'
        
        elif index == "4":
            return 'The server error will occur if the SVD application cannot find the server containing \nthe data for downloading, or if the SVD application cannot find the requested session \nin the server. If SVD cannot find the server, either the server is no longer \nopperational (and the SVD application will no longer be able to download files) or \nthere is no internet connection. \n\nIf SVD cannot find a file in the server, either there is no internet connection, or the \nsession name in the session code folder in the SVD application folder contains an \nincorrect session name.'
        
        elif index == "5":
            return 'The matching process error will occur if SVD could not find a match for an enterred \nsession code in the session codes folder in the SVD application folder. Common causes \nof this are misspelling the session code, forgetting to place commas (,) separating \nindividual session code entries, misspelling "projection", misspelling "quit" or \nmisspelling "help".'
        
        else:
            return 'To use the help menu type the number "1", "2", "3", "4" or "5" which relates to the \nparticular aspect of the application that needs a further explanation as dictated by \nthe menu. To leave the help menu and return to the application type "quit".'
            
MainMethod()
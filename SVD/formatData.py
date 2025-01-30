#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Zachary Allen
@supervisor: Tirge McCarthy
@function: Takes individual data lists and header names, and turns the data into a txt file
'''

import pandas as pd

class CreateTextFile:

    '''
    @__init__: CreateTextFile class constructor

    @param self: instance variable of the class, CreateTextFile
    @param data: data to be formatted into a txt file
    @param path_to_directory: path of the directory of the intended file
    @param file_name: intended name of the file
    @param header: the header of the data
    '''
    def __init__(self, data, path_to_directory, file_name, header = None):
        
        # Converting the data into a dataframe using pandas
        data_frame = pd.DataFrame(data, columns = header)

        # Creating the full txt file path
        write_path = path_to_directory + '\\' + file_name 

        # Writing the dataframe as a text file under the name of the session code, and placing it into the Extracted Data directory
        with open(write_path, 'w') as data_file:
            data_file.write(data_frame.to_string(index=False))
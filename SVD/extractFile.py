#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Zachary Allen
@supervisor: Tirge McCarthy
@function: Extracts VgosDB files from .tgz format and exports then to the VgosDB directory
'''

import tarfile 
import os

class ExtractTGZ:

    '''
    @__init__: ExtractTGZ class constructor

    @param self: instance variable of the class, ExtractTGZ
    @param path: path to the VgosDB .tgz file
    '''
    def __init__(self, file_path, file_name, extracted_file_directory, extracted_file_name):

        # Opening the specified .tgz file
        with tarfile.open(file_path, 'r', encoding='utf-8') as file: # TODO I JUST REMOVED .upper() FROM THE file_path NOT SURE IF THATS A PROBLEM

            # Extracting the .tgz file into the given directory
            file.extractall(extracted_file_directory)
            
            # Renaming the file from mk3 format to VGOS format if necessary
            if file_name != extracted_file_name:
                os.rename(extracted_file_directory + '\\' + file_name, extracted_file_directory + '\\' + extracted_file_name)

            # Closing the .tgz file
            file.close() 

            # Deleting the .tgz file
            os.remove(file_path)
#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Zachary Allen
@supervisor: Tiege McCarthy
@function: Performs some more drawn-out mathmatical transformations and functions needed for the application
'''

import math

class NumberMethods:

    '''
    @__init__: NumberMethods class constructor

    @param self: instance variable of the class, NumberMethods
    '''
    def __init__(self):
        pass

    '''
    @complex_add: adds complex numbers together

    @param self: instance variable of the class, NumberMethods
    @param *complex_numbers: the complex numbers to be added together
    @return: the sum of complex numbers numbers
    '''
    def complex_add(self, *complex_numbers):

        real_parts = []
        imaginary_parts = []

        # Creating a list of real and imaginary components of the complex numbers
        for complex_number in complex_numbers:
            real_parts.append(complex_number.real)
            imaginary_parts.append(complex_number.imag)

        return sum(real_parts) + sum(imaginary_parts) * 1j
        
    '''
    @modulus: Calculates the modulus of a cartesian vector

    @param self: instance variable of the class, NumberMethods
    @param vector: the list of cartesian vector components
    @return: tmodulus of the vector
    '''
    def modulus(self, vector):
        return math.sqrt(sum([coordinate**2 for coordinate in vector]))
    
    '''
    @dmsDecimal: converts an angle in degrees-minutes-seconds to decimal degrees

    @param self: instance variable of the class, NumberMethods
    @param degrees: the component of the angle in integer degrees
    @param minutes: the component of the angle in minutes
    @param seconds: the component of the angle in seconds
    @return: the angle in decimal degrees
    '''
    def dmsDecimal(self, degrees, minutes, seconds):
        return (int(degrees)) + (int(minutes)/60) + (float(seconds)/3600)
    
    '''
    @hmsDecimal: converts an angle in hours-minutes-seconds to decimal degrees

    @param self: instance variable of the class, NumberMethods
    @param hours: the component of the angle in hours
    @param minutes: the component of the angle in minutes
    @param seconds: the component of the angle in seconds
    @return: the angle in decimal degrees
    '''
    def hmsDecimal(self, hours, minutes, seconds):
        return (int(hours)*15) + (int(minutes)/60) + (float(seconds)/3600)

    '''
    @hours_minutes_seconds: converts an angle in decimal to hours-minutes-seconds

    @param self: instance variable of the class, NumberMethods
    @param decimal_degrees: the angle in decimal degrees
    @return: the angle in hours-minutes-seconds
    '''
    def hours_minutes_seconds(self, decimal_degrees):

        decimal_hours = decimal_degrees / 15

        decimal_minutes = 60 * (decimal_hours - int(decimal_hours))
        
        decimal_seconds = 60 * (decimal_minutes - int(decimal_minutes))
        
        hours = int(decimal_hours)
        minutes = int(decimal_minutes)
        seconds = decimal_seconds
        
        return (hours, minutes, seconds)

    '''
    @degrees_minutes_seconds: converts an angle in decimal to degrees-minutes-seconds

    @param self: instance variable of the class, NumberMethods
    @param decimal_degrees: the angle in decimal degrees
    @return: the angle in degrees-minutes-seconds
    '''
    def degrees_minutes_seconds(self, decimal_degrees):

        # Accountinging for the sign of the angle
        sign = decimal_degrees / abs(decimal_degrees)

        decimal_minutes = sign * 60 * (decimal_degrees - int(decimal_degrees))
        
        decimal_seconds = 60 * (decimal_minutes - int(decimal_minutes))
        
        degrees = int(decimal_degrees)
        minutes = int(decimal_minutes)
        seconds = decimal_seconds
        
        return (degrees, minutes, seconds)
    
    '''
    @roundNumber: rounds a number to the given number of decimal places

    @param self: instance variable of the class, NumberMethods
    @param number: an arbitrary decimal number
    @param round_to: the number of decimal places to round to
    @return: rounded number
    '''
    def roundNumber(self, number, round_to = 0) -> float:

        multiplier = 10 ** round_to 
        
        # Extract the last digit of the number
        last_digit = int(str(number)[-1])

        # Determine if rounding up or rounding down
        if last_digit >= 5:

            # Rounding up
            rounded_number = math.ceil(number * multiplier) / multiplier
        else:

            # Rounding down
            rounded_number = math.floor(number * multiplier) / multiplier
        
        return rounded_number
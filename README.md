# Source-Variability-Data

***Extracts data for investigating variability of radio sources used in Geodetic VLBI from VgosDB files.***

> **Author:** Zachary Allen
> 
> **Supervisor:** Tiege McCarthy

## Disclaimer

> *The writing of this program was under the bases of a 8-week research project and will not be maintained by the author henceforth. The code cannot be gauranteed to work apropriately and it is not written in a professional style. Some attempt has been made to document the code, in the expectation that the application may be reworked by a professional developer.*

## Purpose

This application was written to provide a database of information to aid research into the understanding the variability in performance of radio sources that are used in Geodetic *VLBI*. 

## Description

This program takes a *VGOS* format session code as input of, extracts the *VgosDB* file of this session, and produces a text file of data investigating source variability. Also there is an optional parameter of calculating the projected baseline lengths and angles which are geometric parameters of the system that take a while to comput due to the numerous vector calculations needed. Depending on whether the telescopes in the observation used the *VGOS* or legacy *S/X* recievers, some of the data may be displayed per frequency band rather than as the total average value.

The entirety of the program was written in the *Python* programming language due to its versatility and use in the field of Astrophysics. The structure of this application is predominantly class-based and revolves around a main-method class that deals with all user interaction. The six other classes were designed with a small degree of independence such that they could be used independently as part of some other application.

The main challenges that were faced when writing this application came from the requesting of a *CDDIS* server which after trying and failing to use the *HTTP* server, a secure *FTP* server was used instead. Unfortunately this means that the downloading of the *VgosDB* files from the *CDDIS* server is quite a timely process as no multiprocessing is utilised.

Future improvements to this application may include the extraction of more data that is relevant to source performance, optimising the runtime or modifying into a graphical-user-interface.

## Output

Depending on the format of data collection (*VGOS* or *S/X*) slightly different data will be displayed in the text files. However, it is important to note that if a certain list of data could not be properly extracted from the VgosDB file (source of all data displayed here) then that list will be omitted from file. Also, due to its timely computation, the projected baseline angles and lengths may or may not have been calculated. Assuming all data was successfully extracted, the following lists of data will be present in the text files.

Lists of data displayed by both *VGOS* format and *S/X* format sessions:

> **SESSION** The name of the session from which the data was extracted
>
> **TIME (MJD)** Time at which the observation started in the *MJD* time format
>
> **DURATION (s)** Duration of the observation session in seconds
>
> **SOURCE** *IAU* name of the radio source observed
> 
>**STATION 1** Name of the first of the two radio telescopes that were observing the source for the observation
>
> **STATION 2** Name of the second of the two radio telescopes that were observing the source for the observation
>
> **ANGLE [PROJ.]** Projected baseline angle as seen by the source

Lists of data only displayed by *S/X* format sessions:

> **QC [X]** Quality code of the fringe fit for the *X* band
>
> **QC [S]** Quality code of the fringe fit for the *S* band
>
> **SNR [X]** Signal to noise ratio of the radio sources flux density for the *X* band
>
> **SNR [S]** Signal to noise ratio of the radio sources flux density for the *S* band

Lists of data only displayed by the *VGOS* format sessions:

> **QC** Quality code of the fringe fit
>
> **SNR [TOTAL]** Signal to noise ratio of the radio sources flux density averaged over all the bands
>
> **SNR [a]** Signal to noise ratio of the radio sources flux density for the *a* band
>
> **SNR [b]** Signal to noise ratio of the radio sources flux density for the *b* band
>
> **SNR [c]** Signal to noise ratio of the radio sources flux density for the *c* band
>
> **SNR [d]** Signal to noise ratio of the radio sources flux density for the *d* band

Lists of data only displayed if the user specifies *projection*:

> **BASELINE [PROJ.]** Projected baseline length as seen by the source
>
> **ANGLE [PROJ.]** Projected baseline angle as seen by the source

## Dependencies

The following is the list of dependencies and their versions used when writting this application:

> **numpy** (2.2.2)
>
> **astropy** (7.0.0)
>
> **netCDF4** (1.7.2)
>
> **pandas** (2.2.3)

## Application use

To use this application, the *SVD* folder must be downloaded to the users device. 

### Calling the application

Once the *SVD* folder downloaded, the program can be called from the command line interface by enterring the name of the programming environment, followed by the path to the *SVD* folder on the users device. To call the program from the commandline interface, enter ``` python "path/to/SVD" ``` where ``` "path/to/SVD" ``` should be replaced with the actual path to the file on the users computer. Below is an example of calling the folder from the *Windows command line*:

```
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Users\User> python "Desktop\SVD"
```

### Program input

At this point, there are two different ways to run the application. The program can either be run allowing for user input, or run directly from the command line interface. To see the command line interface method explanation, navigate to the [command line interface tab](#command-line-interface-method).

#### User input method

To activate the user input method of this applucation, after typing the path to the command line interface (as shown above) press enter and the following message will be displayed. Note that the application may take up to 5 seconds to load all the required modules before the user input message is displayed. Below is an example of the text displayed when user input is specified:

```
--------------------------------SOURCE VARIABILITY DATA--------------------------------
Type "help" for more information or type "quit" to end this application

---------------------------------------------------------------------------------------
Note that by default, SVD will not calculate baseline projection angles or lengths as
the computations take significant time. To enable calculation of projections, type
"projection" after enterring the VgosDB session code(s).

Warning, SVD only accepts session codes in the VGOS format.
To compile data for multiple VgosDB sessions, separate individual entries by a space.
---------------------------------------------------------------------------------------

Enter VgosDB session code(s):
>
```

At this point, there are a number of possible entries for the program.

##### Calling "quit"

If ```quit``` is enterred into the user input entry, the program will end. Note that a similar result will be displayed for quitiing at any stage in the program. See the example below:

```
Enter VgosDB session code(s):
> quit
Ending application...
Thankyou for using the SVD application.
```

##### Calling "help"

If ```help``` is enterred into the user input entry, the program will enter the help method. See the example below:

```
Enter VgosDB session code(s):
> help
---------------------------------------HELP MENU---------------------------------------
Type "1" for more information about the session code
Type "2" for more information about the projections
Type "3" for more information about the output
Type "4" for more information about the CDDIS server error
Type "5" for more information about the matching process error
Type "quit" to close the help menu
---------------------------------------------------------------------------------------
help>
```

To use the help menu, type ```1```, ```2```, ```3```, ```4``` or ```5``` and an explanatory message about the topic will be displayed. Below is an example of calling the help method with ```1``` and asking for more information about the session code.

```
help> 1
---------------------------------------------------------------------------------------
The session code is a unique identifyer of each Geodetic VLBI session. They are usually
4 to 6 digits long, formed from an assortment of numbers and letters (e.g. "VO3012").
To find a full list of all session codes, open any of the yearly catalogue files in the
session codes folder in the SVD application folder. The collection of characters after
the dash (-) in the first column of each file is a session code (e.g. from
"20191230-B19364", "B19364" is a session code) To learn more about these sessions,
search "IVS VLBI SESSIONS" followed by the session code, in your web browser.

To enter multiple session codes, separate each code by a comma "," (e.g. to enter the
codes "VO3012" and "B19364", type "VO3012, B19364").
---------------------------------------------------------------------------------------
help>
```

Note that the program will stay in the help method until ```quit``` is enterred, where it returns to the main method.

If ```help``` or any other message is enterred, the following message will be dispayed:

```
help> help
---------------------------------------------------------------------------------------
To use the help menu type the number "1", "2", "3", "4" or "5" which relates to the
particular aspect of the application that needs a further explanation as dictated by
the menu. To leave the help menu and return to the application type "quit".
---------------------------------------------------------------------------------------
help>
```

##### Entering a session code

A *VGOS* format session code (or session codes) is what the program takes as input. The *VGOS* session codes are a 4-6 digit collection of alphanumeric characters that uniquely identify different observing sessions.

To enter a session code into the user interface, type the session code after the ```> ```. See the example below for the session code ```VO3012```:

```
Enter VgosDB session code(s):
> VO3012
```

To enter multiple session codes, separate each entry by a space. See the example below for the session codes ```VO3012``` and ```B19364```:

```
Enter VgosDB session code(s):
> VO3012 B19364
```

##### Specifying projection

By default, due to its slow computation, the application will not calculate the projected bandwise. To specify to the program to calculate projections, ```projection``` must be enterred into the interface after the session code. 

Below is an example of calling projection for the session code ```VO3012```:

```
Enter VgosDB session code(s):
> VO3012 projection
```

Below is an example of calling projection for the session codes ```VO3012``` and ```B19364```:

```
Enter VgosDB session code(s):
> VO3012 B19364 projection
```

#### Command line interface method

To use the command line interface method, all instructions for the application are enterred into a single line. 

##### Calling "--help"

Below is an example of calling the help method via the command line:

```
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Users\User> python "Desktop\SVD" --help
usage:
  python "C:\Users\User\Desktop\SVD" [-h] [-p] [session codes...]

description:
  SVD Takes a Geodetic VLBI session code and extracts data from the relevant vgosDB
  into a text file.

positional arguments:
  session_codes     name of the Geodetic VLBI session of which data is to be extracted
                    SVD takes between zero and infinitely many session codes as input

options:
  -h, --help        show this help message and exit
  -p, --projection  specify calculation of projcted baseline angles and lengths

Thankyou for using the SVD application
```

Note that one ```--help``` or ```-h``` is enterred, the program will instantly end.

##### Entering a session code

A *VGOS* format session code (or session codes) is what the program takes as input. The *VGOS* session codes are a 4-6 digit collection of alphanumeric characters that uniquely identify different observing sessions.

To enter a session code directly into the command line interface, type the session code after enterring the programming environment and the path to the *SVD* folder. See the example below for the session code ```VO3012```:

```
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Users\User> python "Desktop\SVD" VO3012
```

To enter multiple session codes, separate each entry by a space. See the example below for the session codes ```VO3012``` and ```B19364```:

```
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Users\User> python "Desktop\SVD" VO3012 B19364
```

##### Calling "--projection"

By default, due to its slow computation, the application will not calculate the projected bandwise. To specify to the program to calculate projections, ```--projection``` or ```-p``` must be enterred into the interface before the session code. 

Below is an example of calling projection for the session code ```VO3012```:

```
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Users\User> python "Desktop\SVD" -p VO3012
```

Below is an example of calling projection for the session codes ```VO3012``` and ```B19364```:

```
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Users\User> python "Desktop\SVD" --projection VO3012 B19364
```

As an added level of functionality, if projection is specified by no session code enterred, the program will change to the user input method. As projection is already specified, the program instead displays a warning message that the calculations will be undertaken.

```
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Users\User> python "Desktop\SVD" --projection
--------------------------------SOURCE VARIABILITY DATA--------------------------------
Type "help" for more information or type "quit" to end this application

---------------------------------------------------------------------------------------
Note that SVD will calculate baseline projection angles and lengths, of which the
computations will take significant time.

Warning, SVD only accepts session codes in the VGOS format.
To compile data for multiple VgosDB sessions, separate individual entries by a space.
---------------------------------------------------------------------------------------

Enter VgosDB session code(s):
>
```

### Program errors

In most cases, the program will run to completion without error (a process that takes around 60-100 seconds). There are several instances in the code that possible errors have excepted and the program will throw a status error.

If the user input mode is used to enter session codes, the sections in which errors occoured may be retried. Otherwise, of the program was only called through the command line, the program will end.

There are 3 types of errors that have been excepted by the code. Any other type of error will cause the program to crash.

#### Server errors

There are two points in the code where the *CDDIS* server is requested. First the server is requested to update the session codes catalogues and second, the server is requested to download the *VgosDB* file. In both cases, errors are excepted if the program has issues connecting to the internet.

#### Matching file error

The matching file error will occur if the application cannot find a match in the session codes catalogue for the user enterred session code. This will occur if there are mistakes in the users entry, or if the session code does not exist in the catalogue. The only ways for the session code to not appear in the catalogue are if the catalogue has been modified to provide incorrect data, or the *CDDIS* server does not contain the selected session.

If the program cannot find a specific session, the *VgosDB* must be downloaded and extracted manually to the *VgosDB* File Folder in the *SVD* application folder. Then, the program must be re-run with the name of the manually added file called. For conformity, if any *VgosDB* files are downloaded and extracted manually, they should be named under the *VGOS* session name with lowercase letters.

#### Data extraction errors

During the process of extracting data from the *NetCDF4* files in the *VgosDB*, numerous errors are excepted. Due to the change of file documenting in 2010 from the *Mk3* format to the *VGOS* format, the *VgosDB* files from earlier than 2010 are likely to have a large number of miss-displayed information, and it is likely that only a small amount of the relevant data will be able to be extracted.

For each list of data extracted the program identifies their extraction status and either provides a warning or error message to the user. The program displays no message if no errors occur, a warning message if the program detected that some entries in the list were errors, and an error message if the program detected that all the entries were errors. A similar process is used for all calculations using this data.

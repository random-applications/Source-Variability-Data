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












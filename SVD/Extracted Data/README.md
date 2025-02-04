# Extracted Data

This directory is designed to hold the text files containg the extracted source variability data produced by the application. Each text file is named under the *VGOS* session name assigned to the session of which the data was extracted from.

Depending on the format of data collection (*VGOS* or *S/X*) slightly different data will be displayed in the text files. However, it is important to note that if a certain list of data could not be properly extracted from the VgosDB file (source of all data displayed here) then that list will be omitted from file. Also, due to its timely computation, the projected baseline angles and lengths may or may not have been calculated. Assuming all data was successfully extracted, the following lists of data will be present in the text files.

Lists of data displayed by both *VGOS* format and *S/X* format sessions:

>
> **SESSION** <span style="padding-left: 83px;"></span> The name of the session from which the data was extracted
>
> **TIME (MJD)** <span style="padding-left: 58px;"></span> Time at which the observation started in the *MJD* time format
>
> **DURATION (s)** <span style="padding-left: 39px;"></span> Duration of the observation session in seconds
>
> **SOURCE** <span style="padding-left: 85px;"></span> *IAU* name of the radio source observed
> 
>**STATION 1** <span style="padding-left: 65px;"></span> Name of the first of the two radio telescopes that were observing the source for the observation
>
> **STATION 2** <span style="padding-left: 65px;"></span> Name of the second of the two radio telescopes that were observing the source for the observation
>
> **ANGLE [PROJ.]** <span style="padding-left: 32px;"></span> Projected baseline angle as seen by the source
>

Lists of data only displayed by *S/X* format sessions:

>
> **QC [X]** <span style="padding-left: 89px;"></span> &nbsp; Quality code of the fringe fit for the *X* band
>
> **QC [S]** <span style="padding-left: 90px;"></span> &nbsp; Quality code of the fringe fit for the *S* band
>
> **SNR [X]** <span style="padding-left: 87px;"></span> Signal to noise ratio of the radio sources flux density for the *X* band
>
> **SNR [S]** <span style="padding-left: 89px;"></span> Signal to noise ratio of the radio sources flux density for the *S* band
>

Lists of data only displayed by the *VGOS* format sessions:

>
> **QC** <span style="padding-left: 127px;"></span> Quality code of the fringe fit
>
> **SNR [TOTAL]** <span style="padding-left: 49px;"></span> Signal to noise ratio of the radio sources flux density averaged over all the bands
>
> **SNR [a]** <span style="padding-left: 90px;"></span> Signal to noise ratio of the radio sources flux density for the *a* band
>
> **SNR [b]** <span style="padding-left: 88px;"></span> Signal to noise ratio of the radio sources flux density for the *b* band
>
> **SNR [c]** <span style="padding-left: 90px;"></span> Signal to noise ratio of the radio sources flux density for the *c* band
>
> **SNR [d]** <span style="padding-left: 88px;"></span> Signal to noise ratio of the radio sources flux density for the *d* band
>

Lists of data only displayed if the user specifies *projection*:

>
> **BASELINE [PROJ.]** <span style="padding-left: 10px;"></span> Projected baseline length as seen by the source
>
> **ANGLE [PROJ.]** <span style="padding-left: 32px;"></span> Projected baseline angle as seen by the source
>
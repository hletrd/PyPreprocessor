## preprocessor.py
### Example
```sh
$ python preprocessor.py --masterbias=masterbias_-20.0.fits --masterdark=masterdark_300.0_-20.0.fits --masterflat=masterflat_L_-20.0.fits --light=light.list
```
### Options
#### Bias
* ```--bias```
  * List of bias files.
  * The list contains name of each bias files to be combined, one by one in each line.
* ```--masterbias```
  * Name of master bias file.
  * Cannot be used together with --bias option.
* ```--bias_method```
  * Combining option for bias frames. ```average```, and ```median``` supported.
  * Default value is ```average```
* ```--bias_sigmaclip```
  * Pass ```1``` to enable 10 pass 3-sigma clipping when combining bias frames, or pass ```0``` to disable sigma clipping.
  * Default value is ```1```.
  
#### Dark
* ```--dark```
  * List of dark files.
  * The list contains name of each dark files to be combined, one by one in each line.
* ```--masterdark```
  * Name of master dark file.
  * Cannot be used together with --dark option.
* ```--dark_method```
  * Combining option for dark frames. ```average```, and ```median``` supported.
  * Default value is ```average```
* ```--dark_exptime```
  * Exposure time for master dark frame to be created, in seconds, when creating new master dark frame.
  * Will be ignored if --masterdark option is enabled.
  * Default value is ```300```.
* ```--dark_sigmaclip```
  * Pass ```1``` to enable 10 pass 3-sigma clipping when combining dark frames, or pass ```0``` to disable sigma clipping.
  * Default value is ```1```.
  
#### Flat
* ```--flat```
  * List of flat files.
  * The list contains name of each flat files to be combined, one by one in each line.
* ```--masterflat```
  * Name of master flat file.
  * Cannot be used together with --flat option.
* ```--flat_method```
  * Combining option for flat frames. ```average```, and ```median``` supported.
  * Default value is ```average```
* ```--flat_sigmaclip```
  * Pass ```1``` to enable 10 pass 3-sigma clipping when combining flat frames, or pass ```0``` to disable sigma clipping.
  * Default value is ```1```.

#### Light 
* ```--light```
  * List of light files.
  * The list contains name of each light files to be combined, one by one in each line.
* ```--light_method```
  * Combining option for light frames. ```average```, and ```median``` supported.
  * Default value is ```average```
* ```--light_sigmaclip```
  * Pass ```1``` to enable 10 pass 3-sigma clipping when combining light frames, or pass ```0``` to disable sigma clipping.
  * Default value is ```1```.
* ```--output```
  * Output file name for final light frame combined and calibrated.
  * Will be automatically generated if not given.
  
#### FITS headers
* ```--fits_header_exptime```
  * Name of FITS header contains exposure time.
  * Default value is ```EXPTIME```
* ```--fits_header_ccdtemp```
  * Name of FITS header contains temperature of CCD sensor.
  * Default value is ```CCD-TEMP```
* ```--fits_header_filter```
  * Name of FITS header contains information of filter.
  * Default value is ```FILTER```

#### Image offset
* ```--offset```
  * Accepts offset file output from [cometregister.py](../cometregister.py).
  * Automatically shifts each image before combining to make sure comet is aligned in final image.
  
#### Misc
* ```--header_from```
  * Select an image to provide the header for the final image.
  * By default, 1st light image is selected.

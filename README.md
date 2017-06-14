## Python tools for preprocess for astrophotography & astrophotometry
* Compatible with Python 2/3

### Dependencies
* Depends on [ccdproc](https://github.com/astropy/ccdproc), [astropy](http://www.astropy.org/), [numpy](http://www.numpy.org/)
```sh
$ pip install ccdproc
$ pip install astropy
$ pip install numpy
```

### Components

#### ```autorenamer.py```
* Automatically renames(add prefix) FITS file according to their headers.

##### Options
* ```--list```
  * The name of the file containing the list of input files.
  
* ```--rename_by```
  * FITS keyword to classify images.
  
* ```--reparse```
  * If ```1```, previously classification will be initialized.
  * Default value is ```0```

#### ```cometregister.py```
* Find comet in images, and make offset data to align comet in each image.
* The 1st image will be the reference.

##### Options
* ```--list```
  * The name of the file containing the list of input files.

* ```--xrange```, ```--yrange```
  * Initial x and y range to search for comet, comma separated.
  * Default value is ```350,650```.
  
* ```--movement_x```, ```--movement_y```
  * Maximum shift between each image.
  * Default value is ```10```.
  
* ```--output```
  * Name of the output file.
  * Default value is ```offset.txt```

#### ```filter.py```
* Filters out the image with significantly different average ADU compared to other images.

##### Options
* ```--list```
  * The name of the file containing the list of input files.

* ```--output```
  * Name of the output file.
  
* ```--reference```
  * If given, the reference ADU will be set to given value.
  * By default, the reference ADU is average ADU of the first image.
  
* ```--threshold```
  * Set ADU range to be allowed.
  * Default value is ```0.2```, which means ± 20% from reference ADU is allowed.

#### ```listcreator_jd.py```
* Classify images by time.

##### Options
* ```--list```
  * The name of the file containing the list of input files.
  
* ```--fits_header_juliandate```
  * FITS keyword stores Julian Date(JD.)
  * Default value is ```JD```.
  
* ```--output_prefix```
  * If given, prefix will be applied to the name of the output directories.

* ```--time_interval```
  * Time interval to group images.
  * Unit is seconds.
  * Default value is ```3600``` (seconds.)
  
* ```--time_start```
  * If given, the image will be grouped from given time by given ```time_interval```.
  * Default value is set to the JD of the first image.

#### ```preprocessor.py```
* Simple preprocessor performs bias / dark / flat calibration.
* Full options are described [here](docs/preprocessor.py.md).

### TODO
#### ```preprocessor.py```
* Support GPU computing (based on [Pytorch](http://pytorch.org/)? or maybe just [OpenCL](https://www.khronos.org/opencl/)?) for calibration, like [GPUPhotometry](https://github.com/hletrd/GPUPhotometry).
 * GPUPhotometry was also a simple preprocessing program utilizes GPU, but it does not support various options, and does not support Windows.
* Adding options for masterbias, masterdark, masterflat output.
* Using [sum combiner](https://github.com/astropy/ccdproc/pull/508).

### Known bugs
#### ```preprocessor.py```
* Even if exposure time of dark frames are different from each other, each frame cannot be weighted one by one, but just devided by exposure time of each dark frames, and summed.
 * By this reason, it is strongly recommended to use multiple dark frames with same exposure time.

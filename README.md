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

#### ```cometregister.py```
* Find comet in images, and make offset data to align comet in each image.

#### ```filter.py```
* Filters out the image with significantly different average ADU compared to other images.

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

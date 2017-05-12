## Python preprocessor for astrophotography
* Compatible with Python 2/3

### Dependencies
* Depends on [ccdproc](https://github.com/astropy/ccdproc), [astropy](http://www.astropy.org/), [numpy](http://www.numpy.org/)
```sh
$ pip install ccdproc
$ pip install astropy
$ pip install numpy
```

### TODO
* Support GPU computing (based on [Pytorch](http://pytorch.org/)? or maybe just [OpenCL](https://www.khronos.org/opencl/)?) for calibration, like [GPUPhotometry](https://github.com/hletrd/GPUPhotometry).
 * GPUPhotometry was also a simple preprocessing program utilizes GPU, but it does not support various options, and does not support Windows.
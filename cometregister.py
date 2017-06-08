from ccdproc import CCDData
import astropy.io.fits as fits, astropy.units as units
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--list', default='list.list')
parser.add_argument('--xrange', default='350,650')
parser.add_argument('--yrange', default='350,650')
parser.add_argument('--movement_x', default=10, type=int)
parser.add_argument('--movement_y', default=10, type=int)
parser.add_argument('--output', default='offset.txt')

args = parser.parse_args()

def error(description):
	print("Error: " + description)
	exit()

def warning(description):
	print("Warning: " + description)

def log(description):
	print(description)

xrange = [eval(args.xrange)]
yrange = [eval(args.yrange)]

try:
	lst_f = open(args.list, 'r')
except:
	error("List file list not found: " + args.list)

lst = lst_f.read()
lst = lst.replace('\r\n', '\n')
lst = lst.replace('\r', '\n')
lst = lst.split('\n')

log("Loading file(s)...")

f = open(args.output, 'w')

xstart = int(args.xrange.split(',')[0])
ystart = int(args.yrange.split(',')[0])
xsize_init = int(args.xrange.split(',')[1]) - xstart
ysize_init = int(args.yrange.split(',')[1]) - ystart

xsize = args.movement_x
ysize = args.movement_y

xinit = 0
yinit = 0

first = True

for i in lst:
	try:
		data = CCDData.read(i, unit='adu')
		hdulist = fits.open(i)
		hdulist.verify('fix')
		npdata = np.array(data)
		if first == True:
			first = False
			npdata = npdata[ystart:ystart+ysize_init, xstart:xstart+xsize_init]
			y, x = np.unravel_index(npdata.argmax(), npdata.shape)
			xinit = x + xstart
			yinit = y + ystart
		else:
			npdata = npdata[ystart:ystart+ysize, xstart:xstart+xsize]
			y, x = np.unravel_index(npdata.argmax(), npdata.shape)
		x += xstart
		y += ystart
		log("Comet location of " + i + ": x " + str(x) + ", y " + str(y))
		xoffset = x - xinit
		yoffset = y - yinit
		log("Offset is: x " + str(xoffset) + ", y " + str(yoffset))
		f.write(i + "\t" + str(xoffset) + "\t" + str(yoffset) + "\n")
		xstart = int(x-xsize/2)
		ystart = int(y-ysize/2)
	except:
		log("Error while reading file " + i)
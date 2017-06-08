from ccdproc import CCDData
import astropy.io.fits as fits, astropy.units as units
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--list', default='list.list')
parser.add_argument('--output', default='output.list')
parser.add_argument('--reference', default=False)

args = parser.parse_args()

def error(description):
	print("Error: " + description)
	exit()

def warning(description):
	print("Warning: " + description)

def log(description):
	print(description)


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


first = True
avg = float(args.reference) or False
lst_out = []

for i in lst:
	try:
	#if True:
		data = CCDData.read(i, unit='adu')
		log('Reading file ' + i)
		if avg == False:
			avg = np.mean(data)
			log('Reference pixel value: ' + str(avg))
		else:
			avg_tmp = np.mean(data)
			log('Pixel value: ' + str(avg_tmp))
			var = float(avg_tmp) / avg
			if var > 1.2 or var < 0.8:
				log('Filtering out the image ' + i)
			else:
				log('Accepted image ' + i)
				lst_out.append(i)
	except:
		log("Error while reading file " + i)

out = '\n'.join(lst_out)

log('Writing output to ' + args.output)
with open(args.output, 'w') as f:
	f.write(out)
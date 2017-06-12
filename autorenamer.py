import astropy.io.fits as fits
import argparse, os, re, copy

parser = argparse.ArgumentParser()
parser.add_argument('--list', default='list.list')
parser.add_argument('--rename_by', default='DATA-TYP')
parser.add_argument('--reparse', default=0, type=int)

args = parser.parse_args()

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


for i in lst:
	try:
	#if True:
		hdulist = fits.open(i)
		hdulist.verify('fix')
		log("Loading file: " + i)
		headers = dict(hdulist[0].header)
		typ = headers[args.rename_by].strip()
		if args.reparse == 1:
			newname = typ + '_' + i.split('_')[-1]
		else:
			newname = typ + '_' + i
		log("Renamed to " + newname)
		os.rename(i, newname)
	except:
		log("Error while reading file " + i)
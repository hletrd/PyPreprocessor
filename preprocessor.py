from ccdproc import combine, CCDData, ccd_process, subtract_bias, subtract_dark, flat_correct
import astropy.io.fits as fits, astropy.units as units
import astroscrappy
import numpy as np
import argparse, os, re, copy
#import tensorflow as tf

parser = argparse.ArgumentParser()
parser.add_argument('--bias')
parser.add_argument('--masterbias')
parser.add_argument('--bias_method', default='average')
parser.add_argument('--bias_sigmaclip', default=1, type=int)


parser.add_argument('--dark')
parser.add_argument('--masterdark')
parser.add_argument('--dark_method', default='average')
parser.add_argument('--dark_exptime', default=300.0, type=float)
parser.add_argument('--dark_sigmaclip', default=1, type=int)

parser.add_argument('--flat')
parser.add_argument('--masterflat')
parser.add_argument('--flat_method', default='average')
parser.add_argument('--flat_sigmaclip', default=1, type=int)

parser.add_argument('--light')
parser.add_argument('--light_method', default='average')
parser.add_argument('--light_sigmaclip', default=1, type=int)
parser.add_argument('--output', default='light_combined')

parser.add_argument('--crrejection', default='0')

args = parser.parse_args()

def error(description):
	print("Error: " + description)
	exit()

def warning(description):
	print("Warning: " + description)

def log(description):
	print(description)

biascal = False
darkcal = False
flatcal = False

bias = None
dark = None
flat = None

darkexp = 1.0

if args.masterbias == None and args.bias != None:
	biascal = True
	#Creating master bias

	try:
		biaslist_f = open(args.bias, 'r')
	except:
		error("Bias file list not found: " + args.bias)

	biaslist = biaslist_f.read()
	biaslist = biaslist.replace('\r\n', '\n')
	biaslist = biaslist.replace('\r', '\n')
	biaslist = biaslist.split('\n')

	log("Loading bias file(s)...")

	biascnt = 0
	temperature = False

	biaslist_real = copy.copy(biaslist)

	for i in biaslist:
		if os.path.isfile(i) == False:
			warning("Bias file not found: " + i)
			biaslist_real.remove(i)
		else:
			try:
				hdulist = fits.open(i)
				biascnt = biascnt + 1
				log("Using bias file: " + i)
				headers = dict(hdulist[0].header)
				if temperature == False:
					temperature = headers['CCD-TEMP']
					log("Temperature: " + str(temperature) + "°C")
				else:
					if temperature != headers['CCD-TEMP']:
						warning("Temperature mismatch: " + i + " (" + str(headers['CCD-TEMP']) + "°C)")
				exptime = headers['EXPTIME']
				if exptime != 0.0:
					warning("Exposure time is not 0 second: " + i + " (" + str(exptime) + " second(s))")
			except OSError:
				warning("Not proper FITS format: " + i)
				biaslist_real.remove(i)

	if biascnt == 0:
		error("No proper bias file loaded.")

	biasindex = 0
	mbias = 'masterbias_' + str(temperature) + '.fits'

	while True:
		if os.path.isfile(mbias) == False:
			break
		mbias = 'masterbias_' + str(temperature) + '_' + str(biasindex) + '.fits'
		biasindex = biasindex + 1

	log("Combining " + str(biascnt) + " bias frame(s) to " + mbias + ", 3-sigma clipping")

	if args.bias_sigmaclip == 1:
		bias_sigmaclip = True
	else:
		bias_sigmaclip = False

	bias = combine(biaslist_real, output_file=mbias, method=args.bias_method, unit='adu', sigma_clip=bias_sigmaclip)

	hdulist = fits.open(mbias, mode='update')
	hdulist[0].header.set('EXPTIME', 0.0)
	hdulist[0].header.set('CCD-TEMP', temperature)
	hdulist.flush()
	hdulist.close()

elif args.masterbias != None:
	biascal = True

	mbias = args.masterbias

	if os.path.isfile(mbias) == False:
		error("Master bias file not found: " + mbias)

	try:
		hdulist = fits.open(mbias)
	except OSError:
		error("Not proper FITS format: " + mbias)

	log("Using master bias file: " + mbias)
	headers = dict(hdulist[0].header)
	log("Master bias temperature: " + str(headers['CCD-TEMP']) + "°C")
	exptime = headers['EXPTIME']
	if exptime != 0.0:
		warning("Exposure time is not 0 second: " + str(exptime) + " second(s)")

	bias = CCDData.read(mbias, unit='adu')


if args.masterdark == None and args.dark != None:
	if bias == None:
		error("Master bias needed to create master dark frame.")
	darkcal = True
	#Creating master dark

	try:
		darklist_f = open(args.dark, 'r')
	except:
		error("Dark file list not found: " + args.dark)

	darklist = darklist_f.read()
	darklist = darklist.replace('\r\n', '\n')
	darklist = darklist.replace('\r', '\n')
	darklist = darklist.split('\n')

	log("Loading dark file(s)...")

	darkcnt = 0
	temperature = False

	darklist_real = copy.copy(darklist)
	darkscales = []

	for i in darklist:
		if os.path.isfile(i) == False:
			warning("Dark file not found: " + i)
			darklist_real.remove(i)
		else:
			try:
				hdulist = fits.open(i)
				darkcnt = darkcnt + 1
				log("Using dark file: " + i)
				headers = dict(hdulist[0].header)
				if temperature == False:
					temperature = headers['CCD-TEMP']
					log("Temperature: " + str(temperature) + "°C")
				else:
					if temperature != headers['CCD-TEMP']:
						warning("Temperature mismatch: " + i + " (" + str(headers['CCD-TEMP']) + "°C)")
				exptime = headers['EXPTIME']
				darkscales.append(args.dark_exptime/exptime)
			except OSError:
				warning("Not proper FITS format: " + i)
				darklist_real.remove(i)

	if darkcnt == 0:
		error("No proper dark file loaded.")

	darkindex = 0
	mdark = 'masterdark_' + str(args.dark_exptime) + '_' + str(temperature) + '.fits'

	while True:
		if os.path.isfile(mdark) == False:
			break
		mdark = 'masterdark_' + str(args.dark_exptime) + '_' + str(temperature) + '_' + str(darkindex) + '.fits'
		darkindex = darkindex + 1

	log("Combining " + str(darkcnt) + " dark frame(s) to " + mdark + ", 3-sigma clipping")

	if args.dark_sigmaclip == 1:
		dark_sigmaclip = True
	else:
		dark_sigmaclip = False

	darkscales = np.array(darkscales)
	#print(darkscales)

	dark = combine(darklist_real, method=args.dark_method, unit='adu', sigma_clip=dark_sigmaclip, scale=darkscales)

	dark = ccd_process(dark, master_bias=bias)
	dark.write(mdark)

	hdulist = fits.open(mdark, mode='update')
	hdulist[0].header.set('EXPTIME', args.dark_exptime)
	hdulist[0].header.set('CCD-TEMP', temperature)
	darkexp = args.dark_exptime
	hdulist.flush()
	hdulist.close()


elif args.masterdark != None:
	darkcal = True

	mdark = args.masterdark

	if os.path.isfile(mdark) == False:
		error("Master dark file not found: " + mdark)

	try:
		hdulist = fits.open(mdark)
	except OSError:
		error("Not proper FITS format: " + mdark)

	log("Using master dark file: " + mdark)
	headers = dict(hdulist[0].header)
	log("Master dark temperature: " + str(headers['CCD-TEMP']) + "°C")
	log("Master dark exposure: " + str(headers['EXPTIME']) + " second(s)")

	darkexp = headers['EXPTIME']

	dark = CCDData.read(mdark, unit='adu')


if args.masterflat == None and args.flat != None:
	if bias == None or dark == None:
		error("Master bias and master dark needed to create master flat frame.")
	flatcal = True
	#Creating master flat

	try:
		flatlist_f = open(args.flat, 'r')
	except:
		error("Flat file list not found: " + args.flat)

	flatlist = flatlist_f.read()
	flatlist = flatlist.replace('\r\n', '\n')
	flatlist = flatlist.replace('\r', '\n')
	flatlist = flatlist.split('\n')

	log("Loading flat file(s)...")

	flatcnt = 0
	temperature = False
	flatfilter = False
	flats = []

	flatlist_real = copy.copy(flatlist)

	for i in flatlist:
		if os.path.isfile(i) == False:
			warning("Flat file not found: " + i)
			flatlist_real.remove(i)
		else:
			try:
				hdulist = fits.open(i)
				log("Using flat file: " + i)
				headers = dict(hdulist[0].header)
				if temperature == False:
					temperature = headers['CCD-TEMP']
					log("Temperature: " + str(temperature) + "°C")
				else:
					if temperature != headers['CCD-TEMP']:
						warning("Temperature mismatch: " + i + " (" + str(headers['CCD-TEMP']) + "°C)")
				exptime = headers['EXPTIME']
				if flatfilter == False:
					flatfilter = headers['FILTER'].strip()
				else:
					if flatfilter != headers['FILTER'].strip():
						warning("Filter mismatch: " + i + " (" + headers['FILTER'].strip() + " filter)")
				log("Subtracting dark and bias...")
				flats.append(CCDData.read(i, unit='adu'))
				flats[flatcnt] = ccd_process(flats[flatcnt], master_bias=bias, dark_frame=dark, dark_exposure=darkexp * units.s, data_exposure=exptime * units.s, dark_scale=True)
				avg = np.mean(flats[flatcnt])
				log("Average ADU: " + str(avg))

				flatcnt = flatcnt + 1
			except OSError:
				warning("Not proper FITS format: " + i)
				flatlist_real.remove(i)

	if flatcnt == 0:
		error("No proper flat file loaded.")

	flatindex = 0
	mflat = 'masterflat_' + flatfilter + '_' + str(temperature) + '.fits'

	while True:
		if os.path.isfile(mflat) == False:
			break
		mflat = 'masterflat_' + flatfilter + '_' + str(temperature) + '_' + str(flatindex) + '.fits'
		flatindex = flatindex + 1

	log("Combining " + str(flatcnt) + " flat frame(s) to " + mflat + ", 3-sigma clipping")

	if args.flat_sigmaclip == 1:
		flat_sigmaclip = True
	else:
		flat_sigmaclip = False

	flat = combine(flats, method=args.flat_method, unit='adu', sigma_clip=flat_sigmaclip)

	flat.write(mflat)

elif args.masterflat != None:
	flatcal = True

	mflat = args.masterflat

	if os.path.isfile(mflat) == False:
		error("Master flat file not found: " + mflat)

	try:
		hdulist = fits.open(mflat)
	except OSError:
		error("Not proper FITS format: " + mflat)

	log("Using master flat file: " + mflat)
	headers = dict(hdulist[0].header)
	log("Master flat temperature: " + str(headers['CCD-TEMP']) + "°C")
	log("Master flat filter: " + headers['FILTER'].strip())


	flat = CCDData.read(mflat, unit='adu')
	flatfilter = headers['FILTER'].strip()





if args.light != None:
	try:
		lightlist_f = open(args.light, 'r')
	except:
		error("Light file list not found: " + args.light)

	lightlist = lightlist_f.read()
	lightlist = lightlist.replace('\r\n', '\n')
	lightlist = lightlist.replace('\r', '\n')
	lightlist = lightlist.split('\n')

	log("Loading light file(s)...")

	lightcnt = 0
	temperature = False
	lightfilter = False
	exptime = False
	exptimesum = 0
	lights = []

	lightlist_real = copy.copy(lightlist)

	for i in lightlist:
		if os.path.isfile(i) == False:
			warning("Light file not found: " + i)
			lightlist_real.remove(i)
		else:
			try:
				hdulist = fits.open(i)
				
				log("Using light file: " + i)
				headers = dict(hdulist[0].header)
				if temperature == False:
					temperature = headers['CCD-TEMP']
					log("Temperature: " + str(temperature) + "°C")
				else:
					log("Temperature: " + str(temperature) + "°C")
					if temperature != headers['CCD-TEMP']:
						warning("Temperature mismatch: " + i + " (" + str(headers['CCD-TEMP']) + "°C)")
				if exptime == False:
					exptime = headers['EXPTIME']
				elif exptime != headers['EXPTIME']:
					warning("Exposure time mismatch: " + i + " (" + str(headers['EXPTIME']) + "s)")
					exptime = headers['EXPTIME']
				exptimesum += exptime
				if lightfilter == False:
					lightfilter = headers['FILTER'].strip()
				else:
					if lightfilter != headers['FILTER'].strip():
						warning("Filter mismatch: " + i + " (" + headers['FILTER'].strip() + " filter)")
				
				lights.append(CCDData.read(i, unit='adu'))

				if biascal == True:
					log("Calibrating bias...")
					lights[lightcnt] = subtract_bias(lights[lightcnt], bias)
				if darkcal == True:
					log("Calibrating dark...")
					lights[lightcnt] = subtract_dark(lights[lightcnt], dark, dark_exposure=darkexp * units.s, data_exposure=exptime * units.s, scale=True)
				if flatcal == True:
					log("Calibrating flat...")
					if lightfilter != flatfilter:
						warning("Filter mismatch with flat: " + i + " (" + headers['FILTER'].strip() + " filter)")
					lights[lightcnt] = flat_correct(lights[lightcnt], flat)
				lightcnt = lightcnt + 1
			except OSError:
				warning("Not proper FITS format: " + i)
				lightlist_real.remove(i)

	if lightcnt == 0:
		error("No proper light file loaded.")

	lightindex = 0
	mlight = args.output + '_' + lightfilter + '_' + str(temperature) + '_' + str(exptimesum) + 's.fits'

	while True:
		if os.path.isfile(mlight) == False:
			break
		mlight = args.output + '_' + lightfilter + '_' + str(temperature) + '_' + str(exptimesum) + 's_' + str(lightindex) + '.fits'
		lightindex = lightindex + 1

	log("Combining " + str(lightcnt) + " light frame(s) to " + mlight + ", 3-sigma clipping")

	if args.light_sigmaclip == 1:
		light_sigmaclip = True
	else:
		light_sigmaclip = False

	light = combine(lights, method=args.light_method, unit='adu', sigma_clip=light_sigmaclip)

	light.write(mlight)
	log("Processing completed.")


#if args.crrejection == 1:

#cosmic ray rejection


	#bias = combine(biaslist, output_file='')
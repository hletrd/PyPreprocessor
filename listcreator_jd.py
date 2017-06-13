import astropy.io.fits as fits
import argparse, os, re, copy

parser = argparse.ArgumentParser()
parser.add_argument('--list', default='list.list')
parser.add_argument('--fits_header_juliandate', default='JD')
parser.add_argument('--output_prefix', default='')
parser.add_argument('--time_interval', default=3600, type=float)
parser.add_argument('--time_start', default=None, type=float)


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

JDs = []

for i in lst:
	try:
	#if True:
		hdulist = fits.open(i)
		hdulist.verify('fix')
		log("Loading file: " + i)
		headers = dict(hdulist[0].header)
		JD = headers[args.fits_header_juliandate]
		JDs.append((i, JD))
	except:
		log("Error while reading file " + i)

JDs = sorted(JDs, key=lambda x: x[1])

if args.time_start == None:
	time_start = JDs[0][1]
else:
	time_start = args.time_start

time_interval = args.time_interval / 86400.

time_now = time_start
cnt = 0
groups = []
while time_now <= JDs[-1][1]:
	groups.append([])
	time_now += time_interval
	while cnt < len(JDs) and JDs[cnt][1] < time_now:
		groups[-1].append(JDs[cnt])
		cnt += 1
	if len(groups[-1]) > 0:
		dirname = args.output_prefix + 'grouped_' + str(time_now - time_interval) + '_' + str(time_now)
		log('Groupping ' + str(len(groups[-1])) + ' objects into ' + dirname)
		try:
			os.mkdir(dirname)
		except:
			pass
		for i in groups[-1]:
			os.rename(i[0], dirname + '/' + i[0])


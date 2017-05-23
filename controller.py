import serial
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--device')

args = parser.parse_args()

def log(description):
	print(description)

ser = serial.Serial(args.device)
log("Opening device " + args.device)
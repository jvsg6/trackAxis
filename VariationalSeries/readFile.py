#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import sys
import os

from math import cos,sin,radians,sqrt,fabs,acos,pi,degrees,floor

import xml.etree.ElementTree
from geographiclib.geodesic import Geodesic
from geopy.distance import VincentyDistance
geod = Geodesic.WGS84
point = []
dphi = 0
axeRadius = [0.0,0.2,0.4,0.6,0.8,1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0,12.0,14.0,16.0,18.0,20.0,
            22.0,24.0,26.0,28.0,30.0,32.0,34.0,36.0,38.0,40.0,42.0,44.0,46.0,48.0,50.0,
	    52.0,54.0,56.0,58.0,60.0,62.0,64.0,66.0,68.0,70.0,72.0,74.0,76.0,78.0,80.0,
            82.0,84.0,86.0,88.0,90.0,92.0,94.0,96.0,98.0,100.0]

axePoints = []
srcPosLon = 33.5403694792
srcPosLat = 36.1449943051
def findOrCreate(curDir):
	lst = []*len(os.listdir(curDir))
	for filename in os.listdir(curDir):
		lst.append(filename)
	if lst.index("dphi.dat") > 0:
		f=open("dphi.dat", 'r')
		string = f.read() 
		lst = string.split("\n")
		point = [[0.0, 0.0]]*len(lst)
		for i in range(len(lst)-1):		
			point[i][0] = float(lst[i].split(" ")[0])
			point[i][1] = float(lst[i].split(" ")[1])
			print point[i]
	else:
		print "Write dphi"
		input(dphi)
	



	return
	
def main():
	curDir = str(sys.argv[1])
	findOrCreate(curDir)
	return



if __name__ == "__main__":
	sys.exit(main())

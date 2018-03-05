#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import sys
import os

from math import cos,sin,radians,sqrt,fabs,acos,pi,degrees,floor

import xml.etree.ElementTree
from geographiclib.geodesic import Geodesic
from geopy.distance import VincentyDistance
geod = Geodesic.WGS84


axeRadius = [0.0,0.2,0.4,0.6,0.8,1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0,12.0,14.0,16.0,18.0,20.0,
            22.0,24.0,26.0,28.0,30.0,32.0,34.0,36.0,38.0,40.0,42.0,44.0,46.0,48.0,50.0,
	    52.0,54.0,56.0,58.0,60.0,62.0,64.0,66.0,68.0,70.0,72.0,74.0,76.0,78.0,80.0,
            82.0,84.0,86.0,88.0,90.0,92.0,94.0,96.0,98.0,100.0]

axePoints = []
directory = 'res'

srcPosLon = 33.5403694792
srcPosLat = 36.1449943051
dphi = 0.5
axePoints = []
def findOrCreate(curDir):
	phiMin = 0.0
	phiMax = 360.0
	length = int((phiMax-phiMin)/dphi+1)
	lst = []*len(os.listdir(curDir))
	for filename in os.listdir(curDir):
		lst.append(filename)
	find = False
	for namefile in lst:
		if namefile == 'dphi.dat':
			find = True
	if find:
		f=open("dphi.dat", 'r')
		string = f.read() 
		lst = string.split("\n")
		axePoints= [[[0.0 , 0.0]]*length for i in range(len(axeRadius))]
		k = 0
		for i, r in enumerate(axeRadius):
			for j in range(len(axePoints[i])):
				print k
				axePoints[i][j][0] = float(lst[k].split(" ")[0])
				axePoints[i][j][1] = float(lst[k].split(" ")[1])
				k = k + 1
				print axePoints[i][j]
	else:
		phiMin = 0.0
		phiMax = 360.0
		length = int((phiMax-phiMin)/dphi+1)
		axePoints= [[[0.0 , 0.0]]*length for i in range(len(axeRadius))]
		a = open("dphi.dat", 'wt')
		for i, r in enumerate(axeRadius):
			r1 = r*1000.0
			phi = phiMin
			j = 0
			while phi <= phiMax:
				dx = r1*cos(radians(phi))
				dy = -r1*sin(radians(phi))
				azimut = angleOf(dx,dy)
				g = geod.Direct(srcPosLat, srcPosLon, 360.0-(degrees(azimut)-90.0), r1) 
				axePoints[i][j][0] = g['lon2']
				axePoints[i][j][1] = g['lat2']
				#print str(axePoints[i][j])
				a.write(str(axePoints[i][j][0]))
				a.write(' ')
				a.write(str(axePoints[i][j][1]))
				a.write('\n')
				phi = phi+dphi
				j = j + 1
		a.close()
		return
	return
def angleOf(dX,dY):
		dFi = 0.0
		dR = sqrt(fabs(dX*dX+dY*dY));
		if (fabs(dR) > 0):
			dFi  = acos(dX/dR);
		if (dX <= 0 and dY < 0):
			dFi  = 2.0*pi - dFi;
		if (dX >  0 and dY < 0):
			dFi  = 2.0*pi - dFi;
		return dFi;
def readLineF(line):
	lst = line.rstrip()
	vals = filter(None,lst.split(" "))
	return [float(x) for x in vals]

def cleanBlock(block):
	for i in range (len(block)-1, -1, -1):
		if(block[i].strip().strip("\t") == ""):
			del block[i]
	return block
def cleanTab(tab):
	for i in range (len(tab)-1, -1, -1):
		tab[i] = tab[i].replace('\t',' ')
	return tab
		

def main():
	if(len(sys.argv)==1):
		return
	curDir = str(sys.argv[1])
	findOrCreate(curDir)
	return




















if __name__ == "__main__":
	sys.exit(main())

#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import sys
import os

from math import cos,sin,radians,sqrt,fabs,acos,pi,degrees,floor,log10
from datetime import datetime

import xml.etree.ElementTree
import matplotlib.image as mpimg
import struct
from PIL import Image
import matplotlib as mpl

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import matplotlib.ticker as ticker
from matplotlib import cm
import numpy as np
#pathToFIdir="/home/egor/Programs/Result/FI"
pathToFIdir="/home/egor/work"
pathToOut="/home/egor/Programs/stat/VVER_TOI_scenario_3/results/7200 s/"
def find_element_in_list(element,list_element):
        try:
		index_element=list_element.index(element)
		return index_element
	except ValueError:
		return -1 

def find_substr_in_list(element,list_element):
	index_element = []
	for i, item in enumerate(list_element):
		if item.find(element) >= 0:
			index_element.append(i)
	return index_element

def readLineF(line,splitter = " "):
	lst = line.rstrip()
	vals = filter(None,lst.split(splitter))
	return [float(x) for x in vals]

def readLineI(line,splitter = " "):
	lst = line.rstrip()
	vals = filter(None,lst.split(splitter))
	return [int(x) for x in vals]

def cleanBlock(block):
	for i in range (len(block)-1, -1, -1):
		if(block[i].strip().strip("\t") == ""):
			del block[i]
	return block

def make_sure_path_exists(path):
	try: 
		os.makedirs(path)
	except OSError:
		if not os.path.isdir(path):
			raise

class GeoGrid:
	def __init__(self,countx,county,lonmin,latmin,dlon,dlat,lonmax,latmax):
		self.lonmin = lonmin
		self.lonmax = lonmax
		self.latmin = latmin
		self.latmax = latmax
		self.countx = countx
		self.county = county
		self.fmin   = 0.0
		self.fmax   = 0.0		
		self.dlon = dlon
		self.dlat = dlat
		self.data   = [0.0 for o in range(countx*county)]
	
	def findMin(self):
		if(len(self.data) == 0):
			return -1
		ret = self.data[0]
		for v in self.data:
			if(ret > v):
				ret = v
		return ret
		
	def findMax(self):
		if(len(self.data) == 0):
			return -1
		ret = self.data[0]
		for v in self.data:
			if(ret < v):
				ret = v
		return ret			

	def printASCIIGRDFile(self,filename):
		f = open(filename, 'wt')
		f.write("DSAA" + '\r\n')
		f.write(str(self.countx)+"\t"+str(self.county) + '\r\n')
		f.write('%0.12f' % (self.lonmin)+"\t"+'%0.12f' % (self.lonmax) + '\r\n')
		f.write('%0.12f' % (self.latmin)+"\t"+'%0.12f' % (self.latmax) + '\r\n')
		f.write('%0.12e' % self.findMin()+"\t"+'%0.12e' % self.findMax() + '\r\n')
		for j in range(0,self.county):
			for i in range(0,self.countx):
				f.write('%0.12e' % self.data[i*self.county+j]+'\t')
			f.write('\r\n')
		
		f.close()
		return

	def getValue(self,lon,lat):
		if(lon<self.lonmin or lon>self.lonmax):
			return 0.
		if(lat<self.latmin or lat>self.latmax):
			return 0.
		ci = int(floor((lon-self.lonmin)/self.dlon))
		cj = int(floor((lat-self.latmin)/self.dlat))
		ci1 = 0
		ci2 = 0
                cj1 = 0
		cj2 = 0
		
		if ci == self.countx-1:
			ci2 = ci
			ci1 = ci-1
		else:
			ci1 = ci
			ci2 = ci+1
	    
		if cj == self.county-1:
			cj2 = cj
			cj1 = cj-1
		else:
			cj1 = cj
			cj2 = cj+1
		
		f11 = self.data[ci1*self.county+cj1] #+ -
		f21 = self.data[ci2*self.county+cj1] #+ -

		f12 = self.data[ci1*self.county+cj2] #- +
		f22 = self.data[ci2*self.county+cj2] #- +
		
		
		x1 = self.lonmin+self.dlon*ci1
		x2 = self.lonmin+self.dlon*ci2
		y1 = self.latmin+self.dlat*cj1
		y2 = self.latmin+self.dlat*cj2
		
		fy1=(f21-f11)/(x2-x1)*lon+(f11-(f21-f11)/(x2-x1)*x1)

		fy2=(f22-f12)/(x2-x1)*lon+(f12-(f22-f12)/(x2-x1)*x1)

		v = (fy2-fy1)/(y2-y1)*lat+(fy1-(fy2-fy1)/(y2-y1)*y1)
		return  v
	
	def angleOf(self,dX,dY):
		dFi = 0.0
		dR = sqrt(fabs(dX*dX+dY*dY));
		if (fabs(dR) > 0):
			dFi  = acos(dX/dR);
		if (dX <= 0 and dY < 0):
			dFi  = 2.0*pi - dFi;
		if (dX >  0 and dY < 0):
			dFi  = 2.0*pi - dFi;
		return dFi
	
	def findMin(self):
		if(len(self.data) == 0):
			return -1
		ret = self.data[0]
		for v in self.data:
			if(ret > v):
				ret = v
		return ret
		
	def findMax(self):
		if(len(self.data) == 0):
			return -1
		ret = self.data[0]
		for v in self.data:
			if(ret < v):
				ret = v
		return ret			

	def printASCIIGRDFile(self,filename):
		f = open(filename, 'wt')
		f.write("DSAA" + '\r\n')
		f.write(str(self.countx)+"\t"+str(self.county) + '\r\n')
		f.write('%0.12f' % self.lonmin+"\t"+'%0.12f' % self.lonmax + '\r\n')
		f.write('%0.12f' % self.latmin+"\t"+'%0.12f' % self.latmax + '\r\n')
		f.write('%0.12e' % self.findMin()+"\t"+'%0.12e' % self.findMax() + '\r\n')
		for j in range(0,self.county):
			for i in range(0,self.countx):
				f.write('%0.12e' % self.data[i*self.county+j]+'\t')
			f.write('\r\n')
		
		f.close()
		return

	def getValue(self,lon,lat):
		if(lon<self.lonmin or lon>self.lonmax):
			return 0.
		if(lat<self.latmin or lat>self.latmax):
			return 0.
		ci = int(floor((lon-self.lonmin)/self.dlon))
		cj = int(floor((lat-self.latmin)/self.dlat))
		ci1 = 0
		ci2 = 0
                cj1 = 0
		cj2 = 0
		
		if ci == self.countx-1:
			ci2 = ci
			ci1 = ci-1
		else:
			ci1 = ci
			ci2 = ci+1
	    
		if cj == self.county-1:
			cj2 = cj
			cj1 = cj-1
		else:
			cj1 = cj
			cj2 = cj+1
		
		f11 = self.data[ci1*self.county+cj1] #+ -
		f21 = self.data[ci2*self.county+cj1] #+ -

		f12 = self.data[ci1*self.county+cj2] #- +
		f22 = self.data[ci2*self.county+cj2] #- +
		
		
		x1 = self.lonmin+self.dlon*ci1
		x2 = self.lonmin+self.dlon*ci2
		y1 = self.latmin+self.dlat*cj1
		y2 = self.latmin+self.dlat*cj2
		
		fy1=(f21-f11)/(x2-x1)*lon+(f11-(f21-f11)/(x2-x1)*x1)

		fy2=(f22-f12)/(x2-x1)*lon+(f12-(f22-f12)/(x2-x1)*x1)

		v = (fy2-fy1)/(y2-y1)*lat+(fy1-(fy2-fy1)/(y2-y1)*y1)
		return  v
	
	def angleOf(self,dX,dY):
		dFi = 0.0
		dR = sqrt(fabs(dX*dX+dY*dY));
		if (fabs(dR) > 0):
			dFi  = acos(dX/dR);
		if (dX <= 0 and dY < 0):
			dFi  = 2.0*pi - dFi;
		if (dX >  0 and dY < 0):
			dFi  = 2.0*pi - dFi;
		return dFi;
def save(name='', fmt='png'):
    pwd = os.getcwd()
    plt.title(name)

    pathToFolder=pwd+"/pictures/"

    if os.path.isdir(pathToFolder)==False:
		os.mkdir(pathToFolder)
    iPath = './pictures/{}'.format(fmt)
    if not os.path.exists(iPath):
        os.mkdir(iPath)
    os.chdir(iPath)
    plt.savefig('{}.{}'.format(name, fmt), fmt='png')
    os.chdir(pwd)
    plt.close()
    return
def prepareArrayForGraph():
	f=1
	fileName = pathToFIdir+str("/f"+str(f)+".bin")
	inp = open(fileName, 'rb')
	datastr = inp.read(64)
	offsetStart = 64
	headerStr = list(struct.unpack('<%dd' % (len(datastr)/8), datastr))
	grid = GeoGrid(int(headerStr[0]),int(headerStr[1]),headerStr[2],headerStr[3],headerStr[4],headerStr[5],headerStr[6],headerStr[7])
	countx = int(grid.countx)
	county = int(grid.county)
	del grid.data
	offsetForNextGrid = countx*county*4
	gridsCount = (os.stat(fileName).st_size-offsetStart)/offsetForNextGrid-1
	print gridsCount
	for gridId in range(gridsCount):
		if gridId != 1:
			continue
		offset = offsetStart + gridId*offsetForNextGrid
		inp.seek(offset)
		grid.data = struct.unpack('<%df' % (countx*county), inp.read(offsetForNextGrid))
		resultArray=np.array([[0.0]*countx]*county)
		k=0
		for i in range(101):
			for j in range(101):
				resultArray[county - j-1][i]=grid.data[k]
				k=k+1
		plt.imshow(resultArray, cmap='Spectral', alpha = 0.8)
		plt.colorbar()
		
		save(str(gridId*7200))
		plt.clf()
		plt.cla()
		plt.close()
		del grid.data
		#del grid.data

	inp.close()

	#if k == 3:
	#	break
	#print "done", str(float(k)/len(listOfFiles)*100.0)+" %"
	return resultArray



def main():

	
			#fil.printASCIIGRDFile(myWorkPath+"/TIC/"+subDir.split(ident)[1].split("_")[1]+".grd")

			#img = mpimg.imread('./ground.png')
			#img.thumbnail((101, 101))
			#imgplot = plt.imshow(img)
	prepareArrayForGraph()

	
	return 



if __name__ == "__main__":
	sys.exit(main())
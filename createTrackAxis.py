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
#Вводим точность для углов:
dphi = 0.01
axeMaxPoints = []
pathToGRD="/home/egor/work/GRD/" #папка с с готовыми для обработки grd файлами
pathToAxis="/home/egor/work/Axis/" #папка куда будут сохраняться оси следа
#
pathToDphi="/home/egor/work/dphi_{}.dat".format(str(dphi).replace('.', ''))
srcPosLon = 33.5403694792
srcPosLat = 36.1449943051


axePoints = []
def rename(lst):
	
	for i in range(len(lst)):
		num=int(lst[i].replace('f','').split(".")[0])
		if num<10:
			lst[i]=str("f00"+str(num)+".grd")
		if num<100 and num>9:
			lst[i]=str("f0"+str(num)+".grd")
		
	print lst
	return
def findOrCreate(curDir):
	nameDphi = str("dphi_%s.dat" % (str(dphi).replace('.','')))
	print "voshel"
	global axePoints
	phiMin = 0.0
	phiMax = 360.0
	length = int((phiMax-phiMin)/dphi+1)

	if os.path.isfile(pathToDphi) or os.path.isfile(str(curDir+"/"+nameDphi)) :
		
		try:
			f = open(pathToDphi, 'rt')
			print "find "+str(pathToDphi)
		except IOError:
			try:
				f = open(nameDphi, 'rt')
				print "find "+str(nameDphi)
			except IOError :
				print("Error")
		string = f.read()
		f.close()
		lst2 = string.split("\n")
		axePoints= [[] for i in range(len(axeRadius))]
		for i in range(len(axeRadius)):
			axePoints[i].extend([[0.0,0.0] for i in range(length)])
		k = 0
		for i, r in enumerate(axeRadius):
			for j in range(len(axePoints[i])):
				#print float(lst2[k].split(" ")[0]),float(lst2[k].split(" ")[1]),i ,j,len(axeRadius),len(axePoints[i])
				axePoints[i][j][0] = float(lst2[k].split(" ")[0])
				axePoints[i][j][1] = float(lst2[k].split(" ")[1])
				#axePoints[i][j] = [i,j]
				#axePoints[i][j][1] = j
				#print axePoints[i][j][0], axePoints[i][j][1]
				
				#print axePoints[i][j][0]
				#print axePoints[i][j][1]
				k = k + 1

		#print axePoints[2]
			
			
	else:
		print "not find"
		phiMin = 0.0
		phiMax = 360.0
		length = int((phiMax-phiMin)/dphi+1)
		axePoints= [[] for i in range(len(axeRadius))]
		for i in range(len(axeRadius)):
			axePoints[i].extend([[0.0,0.0] for i in range(length)])
		a = open(nameDphi, 'wt')
		for i, r in enumerate(axeRadius):
			
			r1 = r*1000.0
			phi = phiMin
			for j in range(len(axePoints[i])):
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
				
		a.close()
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

def readLineI(line):
	lst = line.rstrip()
	vals = filter(None,lst.split(" "))
	return [int(x) for x in vals]

def cleanBlock(block):
	for i in range (len(block)-1, -1, -1):
		if(block[i].strip().strip("\t") == ""):
			del block[i]
	return block
def cleanTab(tab):
	for i in range (len(tab)-1, -1, -1):
		tab[i] = tab[i].replace('\t',' ')
	return tab

class GeoGrid:
	def __init__(self, f):
		self.lonmin = 0.0
		self.lonmax = 0.0
		self.latmin = 0.0
		self.latmax = 0.0
		self.countx = 0.0
		self.county = 0.0
		self.fmin   = 0.0
		self.fmax   = 0.0
		
		self.data   = []
		
		string = f.read() 
		lst = string.split("\n")
		#print lst[1]  #gridFunction.text.split("\n")
		lst = cleanBlock(lst)
		lst = cleanTab(lst)
		#print lst[1]
		#lst[1] = lst[1].replace('101','202')
		#print lst[1]

		self.countx = int(lst[1].split(" ")[0])
		self.county = int(lst[1].split(" ")[1])
		self.lonmin = float(lst[2].split(" ")[0])
		self.latmin = float(lst[3].split(" ")[0])
		self.lonmax = float(lst[2].split(" ")[1])
		self.latmax = float(lst[3].split(" ")[1])
		self.dlon  =  (self.lonmax-self.lonmin)/(self.countx-1)
		self.dlat  =  (self.latmax-self.latmin)/(self.county -1)
		self.fmin   = float(lst[4].split(" ")[0])
		self.fmax   = float(lst[4].split(" ")[1])


		lst = lst[5:]
		self.data   = [0.0]*self.countx*self.county
		for j in range (len(lst)): #количество строк
			
			lin = readLineF(lst[j])
			for i in range(len(lin)):
				self.data[i*self.county+((j))] = lin[i]
				
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
		dR = sqrt(fabs(dX*dX+dY*dY))
		if (fabs(dR) > 0):
			dFi  = acos(dX/dR)
		if (dX <= 0 and dY < 0):
			dFi  = 2.0*pi - dFi
		if (dX >  0 and dY < 0):
			dFi  = 2.0*pi - dFi
		return dFi
		
	def getPlumeAxisPoints(self, rVals):
		global axePoints
		res = []
		phiMin = 0.0
		phiMax = 360.0
		#print self.getValue(srcPosLon,srcPosLat)
		#r = 1000.0
		for i, r in enumerate(rVals):
			point = [0.0,0.0]
			r1 = r*1000.0
			fv = 0. 
			phi = phiMin
			j = 0
			while phi <= phiMax:
				#print i
				#print j
				
				tmp = self.getValue(axePoints[i][j][0],axePoints[i][j][1])
				if(fv<tmp):
					fv = tmp
					point[0] = axePoints[i][j][0]
					point[1] = axePoints[i][j][1]
				phi = phi+dphi
				
				j = j + 1
			res.append(point)
			
		return res

	def getPlumeAxisValsForPoints(self, rPoints):
		res = []
		for r in rPoints:
			tmp = self.getValue(r[0],r[1])
			res.append(tmp)
		return res

def main():
	global axePoints
	mypath = os.path.dirname(os.path.realpath(__file__))
	os.chdir(mypath)
	curDir = str(mypath)
	if os.path.isdir(pathToAxis)==False:
		os.mkdir(pathToAxis)
	findOrCreate(curDir)
	#print axePoints
	global axeMaxPoints
	lst = []
	lst.sort()
	n=0.0
	for filename in os.listdir(str(pathToGRD)):
		lst.append(filename)
		try:
			et = open(str(pathToGRD)+str(filename), 'r')
		except IOError:
			print ("No such file")
		fil = GeoGrid(et)
		
		axeMaxPoints = fil.getPlumeAxisPoints(axeRadius)
		try:
			filename.split(".")[0].split("_")[1]=="max"
			continue
		except:
			f = open(str(pathToAxis)+"/"+"maxPoint_%s.dat" % (filename.split(".")[0]), 'wt')
		for i in range(len(axeRadius)-4):	
			f.write(str(axeMaxPoints[i]).replace('[','').replace(']',''))
			f.write(str(", "+str(axeRadius[i])+", "+str(fil.getValue(axeMaxPoints[i][0],axeMaxPoints[i][1]))))
			f.write('\r\n')
		f.close()
		print filename
		n=n+1.0
		print str(n/206.0*100.0)+" % done"

	print "dphi_%s.dat" % (str(dphi).replace('.',''))
	return

if __name__ == "__main__":
	sys.exit(main())

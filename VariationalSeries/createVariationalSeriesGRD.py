#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#Модуль для подготовки таблиц с дозами на сетка.
#Реализует сложение сгруппированных модулем createVariationalSeriesFI бинарных сеток, отражающих 
#преобразование выходных данных ПС НОСТРА в более удобный для программной обработки формат. Строятся сетки, отражающие значения целевых функций,
#полученных с заданным уровнем доверия (по умолчанию - 95 процентный доверительный интервал). модуль в том числе используется как модуль препроцессинга для 
# модуля createVariationalSeriesNP
#запуск: 1. запускается модуль createVariationalSeriesFI 3. запускается данный модуль.
#!!!!!важен порядок следования  функционалов!!!!!
#Разработан: 01.06.2017 
#Автор: Киселев А.А.
#Последняя модификация: 05.10.2017 
import sys
import os

from math import cos,sin,radians,sqrt,fabs,acos,pi,degrees,floor,ceil

import struct

patToFIdir = "/home/egor/Programs/Result/FI/"
pathToSIdir = "/home/egor/Programs/Result/1.00/SI/"

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
		return dFi;
	
def main():
	mypath=os.path.dirname(os.path.realpath( __file__ ))
	os.chdir(mypath)
	
	d = patToFIdir
	listOfFiles = [os.path.join(d,o) for o in os.listdir(d) if (os.path.isfile(os.path.join(d,o)) and os.path.join(d,o).find(".bin")>=0)]
	
	for fileName in listOfFiles:
		print fileName
		fileBaseName = os.path.basename(fileName).split(".")[0]
		#if fileBaseName.find("f0")<0:
		#	continue
		myWorkPath = pathToSIdir
		make_sure_path_exists(myWorkPath)

		inp = open(fileName,"rb")
		datastr = inp.read(64)
		offsetStart = 64
		#float(fil.countx),float(fil.county),fil.lonmin,fil.latmin,fil.dlon,fil.dlat,fil.lonmax,fil.latmax
		headerStr = list(struct.unpack('<%dd' % (len(datastr)/8), datastr))
		print headerStr
		grid95 = GeoGrid(int(headerStr[0]),int(headerStr[1]),headerStr[2],headerStr[3],headerStr[4],headerStr[5],headerStr[6],headerStr[7])
		gridMax = GeoGrid(int(headerStr[0]),int(headerStr[1]),headerStr[2],headerStr[3],headerStr[4],headerStr[5],headerStr[6],headerStr[7])
		countx = int(headerStr[0])
		county = int(headerStr[1])
		print grid95.lonmin, grid95.latmin
		count = countx*county
		offsetForNextGrid = countx*county*4
		gridsCount = (os.stat(fileName).st_size-offsetStart)/offsetForNextGrid-1
		posOf95Pbase = int(ceil(float(gridsCount)*1.00))-1 #номер сетки превращаем в позицию сетки т.е. -1
		print gridsCount,offsetForNextGrid,posOf95Pbase
		#отличие от реализации Асфандиярова - работаем с данными точности float, чтобы ограничивать объемы дискового пространства
		for pp in range(count):
			arr = []
			for grid in range(gridsCount):
				offset = offsetStart + grid*offsetForNextGrid+4*pp
				inp.seek(offset)
				binDat = inp.read(4)
				arr.append(struct.unpack('<f', binDat)[0])
			arr.sort()
			grid95.data[pp] = arr[posOf95Pbase]
	
		for pp in range(count):
			offset = offsetStart + gridsCount*offsetForNextGrid+4*pp
			inp.seek(offset)
			binDat = inp.read(4)
			gridMax.data[pp] = struct.unpack('<f', binDat)[0]
		
		inp.close()
		grid95.printASCIIGRDFile(myWorkPath+"/"+fileBaseName+".grd")
		gridMax.printASCIIGRDFile(myWorkPath+"/"+fileBaseName+"_max.grd")
		print "ok!"
	return
	
if __name__ == "__main__":
	sys.exit(main())

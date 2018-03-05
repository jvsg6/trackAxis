#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#Модуль для преобразования результатов расчета ПС Ностра сценариев аварий в удобный (бинарный) для быстрой обработки формат - является модулем препроцессинга для дальнейшей обработки.
#Разработан: 01.06.2017 
#Автор: Киселев А.А.
#Последняя модификация: 05.10.2017 
import sys
import os

from math import cos,sin,radians,sqrt,fabs,acos,pi,degrees,floor

import xml.etree.ElementTree
from geographiclib.geodesic import Geodesic
from geopy.distance import VincentyDistance
geod = Geodesic.WGS84

import struct
from struct import calcsize

patToFolderWithResults = "/home/egor/Programs/stat/delete/result"
patToFIdir = "/home/egor/Programs/stat/delete/FI/"

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

def make_sure_path_exists(path):
	try: 
		os.makedirs(path)
	except OSError:
		if not os.path.isdir(path):
			raise

class GeoGrid:
	def __init__(self,gridFunction):
		self.lonmin = 0.0
		self.lonmax = 0.0
		self.latmin = 0.0
		self.latmax = 0.0
		self.countx = 0.0
		self.county = 0.0
		self.fmin   = 0.0
		self.fmax   = 0.0
		
		self.calcFunctionId = -1
		self.tipObl = -1
		self.isotop = ""
		self.phchForm = ""
		self.organ = ""
		self.age = ""
		self.timeEnd = 0.0
		
		self.data   = []

		if "calcFunctionId" not in gridFunction.attrib:
			self.calcFunctionId = -1
		else:
			self.calcFunctionId = int(gridFunction.get("calcFunctionId").strip())
		
		if "tipObl" not in gridFunction.attrib:
			self.tipObl = -1
		else:
			self.tipObl = int(gridFunction.get("tipObl").strip())
		
		if "isotop" not in gridFunction.attrib:
			self.isotop = ""
		else:
			self.isotop = gridFunction.get("isotop").strip()
			
		if "phchForm" not in gridFunction.attrib:
			self.phchForm = ""
		else:
			self.phchForm = gridFunction.get("phchForm").strip()
			
		if "organ" not in gridFunction.attrib:
			self.organ = ""
		else:
			self.organ = gridFunction.get("organ").strip()
			
		if "age" not in gridFunction.attrib:
			self.age = ""
		else:
			self.age = gridFunction.get("age").strip()
			
		if "timeEnd" not in gridFunction.attrib:
			self.timeEnd = 0.0
		else:
			self.timeEnd = float(gridFunction.get("timeEnd").strip())
				
		lst = gridFunction.text.split("\n")
		lst = cleanBlock(lst)

		self.countx = int(lst[0].split(" ")[1])
		self.county = int(lst[1].split(" ")[1])
		self.lonmin = float(lst[2].split(" ")[1])
		self.latmin = float(lst[3].split(" ")[1])
		self.dlon = float(lst[4].split(" ")[1])
		self.dlat  =  float(lst[5].split(" ")[1])
		self.lonmax = self.lonmin+self.dlon*(self.countx-1)
		self.latmax = self.latmin+self.dlat*(self.county-1)

		lst = lst[7:]
		self.data   = [0.0]*self.countx*self.county
		for j in range(len(lst)): #количество строк
			lin = readLineF(lst[j])
			for i in range(len(lin)):
				self.data[i*self.county+(self.county-j-1)] = lin[i]
		
		self.fmin   = self.findMin()
		self.fmax   = self.findMax()

		#self.printASCIIGRDFile("test.grd")
	
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
		dR = sqrt(fabs(dX*dX+dY*dY))
		if (fabs(dR) > 0):
			dFi  = acos(dX/dR)
		if (dX <= 0 and dY < 0):
			dFi  = 2.0*pi - dFi
		if (dX >  0 and dY < 0):
			dFi  = 2.0*pi - dFi
		return dFi

def main():
	mypath=os.path.dirname(os.path.realpath( __file__ ))
	os.chdir(mypath)
	#if(len(sys.argv)==1):
	#	print("ERROR: Put the path to results dir: /home/user/documents/calculation1/results/")
	#	return
	
	resultsPath = patToFolderWithResults #str(sys.argv[1])
	if(not os.path.isdir(resultsPath)):
		print("ERROR: No such directory",resultsPath)
		return
	d = resultsPath
	subDirs = [os.path.join(d,o) for o in os.listdir(d) if (os.path.isdir(os.path.join(d,o)) and os.path.join(d,o).find(" s")>=0)]
	firstElem = find_substr_in_list("/0 s",subDirs)
	if(len(firstElem) == 1):
		str1 = subDirs[firstElem[0]]
		subDirs.pop(firstElem[0])
		subDirs.insert(0,str1)
	
	#print subDirs
	myWorkPath = patToFIdir
	make_sure_path_exists(myWorkPath)
	
	lst = ["calcFunctionId","tipObl","isotop","phchForm","organ","age","timeEnd"]
	headers = []
	gridsWithMaxValues = []
	for subDirPos, subDir in enumerate(subDirs):
		path = subDir+"/"+"out.xml"
		
		source = open(path, 'rb')
		et = xml.etree.ElementTree.parse(path)
		root = et.getroot()
		grid = root.find('grid')
		positionInXml = -1
		for gridFunction in grid.findall('gridFunction'):
			positionInXml = positionInXml + 1
			fil = GeoGrid(gridFunction)
				
			if subDirPos == 0:
				headers.append([fil.calcFunctionId,fil.tipObl,fil.isotop,fil.phchForm,fil.organ,fil.age,fil.timeEnd/3600.0/24.0])
				gridsWithMaxValues.append(GeoGrid(gridFunction))
				handle = open(myWorkPath+str("/f"+str(positionInXml)+".bin"), 'wb')
				grid = [float(fil.countx),float(fil.county),fil.lonmin,fil.latmin,fil.dlon,fil.dlat,fil.lonmax,fil.latmax]
				handle.write(struct.pack('<%dd' % len(grid), *grid))
				print str(len(grid)), calcsize('<%dd' % len(grid))
				#offset 8*8 = 64 bytes (float is too small) for 101x101 40804 for each grid
				#grid with max values at the and of file
				handle.write(struct.pack('<%df' % len(fil.data), *fil.data))
				print str(len(fil.data)), calcsize('<%df' % len(fil.data))
				handle.close()
			else:
				for c in range(len(fil.data)):
					if(gridsWithMaxValues[positionInXml].data[c]<fil.data[c]):
						gridsWithMaxValues[positionInXml].data[c] = fil.data[c]
				handle = open(myWorkPath+str("/f"+str(positionInXml)+".bin"), 'ab')
				#handle = openedFiles[positionInXml]
				handle.write(struct.pack('<%df' % len(fil.data), *fil.data))
				print str(len(fil.data)), calcsize('<%df' % len(fil.data))
				handle.close()
			del fil
		
	
		if(subDirPos == 0):
			headerFile = open(myWorkPath+"/headerFile.dat", 'wt')
			for j in range(len(headers)):
				headerFile.write(str("f"+str(j)+".bin") + ';')
				for k in range(len(lst)):
					print str(headers[j][k])
					headerFile.write(str(headers[j][k]) + ';')
				headerFile.write('\r\n')
			headerFile.close()
		source.close()
		print "done", str(float(subDirPos)/len(subDirs)*100.0)+" %"
		#break;
	
	for k in range(len(gridsWithMaxValues)):
		handle = open(myWorkPath+str("/f"+str(k)+".bin"), 'ab')
		handle.write(struct.pack('<%df' % len(gridsWithMaxValues[k].data), *gridsWithMaxValues[k].data))
		handle.close()
	
	print("Ok!")
	return

if __name__ == "__main__":
	sys.exit(main())
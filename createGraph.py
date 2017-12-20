#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import sys
import os
from openpyxl import Workbook
from math import cos,sin,radians,sqrt,fabs,acos,pi,degrees,floor,log10
from PIL import Image
import xml.etree.ElementTree
import matplotlib as mpl
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import pylab
from mpl_toolkits.mplot3d import Axes3D
import datetime
from geographiclib.geodesic import Geodesic
from geopy.distance import VincentyDistance
geod = Geodesic.WGS84
from matplotlib import rcParams
mpl.rcParams['font.family'] = 'fantasy'
mpl.rcParams['font.fantasy'] = 'Times New Roman', 'Ubuntu','Arial','Tahoma','Calibri'
srcPosLon = 33.5403694792
srcPosLat = 36.1449943051
#1451606400
import time


number=0
import numpy as np

pathToOut="/home/egor/Programs/stat/VVER_TOI_scenario_3/results"
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
		self.dlon  =  float(lst[4].split(" ")[1])
		self.dlat  =  float(lst[5].split(" ")[1])
		self.lonmax = self.lonmin+self.dlon*(self.countx-1)
		self.latmax = self.latmin+self.dlat*(self.county-1)
		self.grap=np.array([[0.0]*self.county]*self.countx)
		lst = lst[7:]
		self.data   = [0.0]*self.countx*self.county
		for j in range(len(lst)): #количество строк
			lin = readLineF(lst[j])
			for i in range(len(lin)):
				self.data[i*self.county+(self.county-j-1)] = lin[i]
				self.grap[i][self.county-j-1]=lin[i]
		
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
		dR = sqrt(fabs(dX*dX+dY*dY));
		if (fabs(dR) > 0):
			dFi  = acos(dX/dR);
		if (dX <= 0 and dY < 0):
			dFi  = 2.0*pi - dFi;
		if (dX >  0 and dY < 0):
			dFi  = 2.0*pi - dFi;
		return dFi;
def save(name='', fmt='png'):
	global ii
	global number
	pwd = os.getcwd()
	pathToFolder=pwd+"/picture_new/"
	if os.path.isdir(pathToFolder)==False:
		os.makedirs(pathToFolder)
	iPath = './picture_new/{}'.format(fmt)
	if not os.path.exists(iPath):
		os.mkdir(iPath)
	os.chdir(iPath)
	nul = 8-len(name)
	plt.savefig('{:0>8s}.{}'.format(str(number), fmt), fmt='png', pad_inches=0.1, dpi=300)
	number+=1
	os.chdir(pwd)
	plt.close()
	return



def main():
	#"f134","f135","f141"
	alltime = 366*24*3600/7200
	for ii in range(0, alltime+1, 12):
		maxx=0.0
		print ii*7200
		a=True
		#path="/home/egor/quest/Ru_106/A/out.xml"
		path = pathToOut+"/"+str(ii*7200)+" s/"+"out.xml"
		source = open(path, 'rb')
		et = xml.etree.ElementTree.parse(path)
		root = et.getroot()
		grid = root.find('grid')
		for gridFunctionID, gridFunction in enumerate(grid.findall('gridFunction')):
			fil = GeoGrid(gridFunction)
			if a==True:
				sumArray=np.array([[0.0]*fil.countx]*fil.county)
				resArray=np.array([[0.0]*fil.countx]*fil.county)
				a==False
			#if (gridFunctionID == 134) or (gridFunctionID == 135) or (gridFunctionID == 141):
			if gridFunctionID == gridFunctionID:
				resArray = np.array(fil.grap)
				resArray = np.transpose(resArray)
				sumArray=sumArray + resArray
			del fil
		fil = GeoGrid(gridFunction)
		
		# g = geod.Inverse(lat1, lon1, lat2, lon2) distance between lat1;lon1 and lat2, lon2
		g = geod.Inverse(fil.latmin, fil.lonmin, fil.latmax, fil.lonmin)#расстояние между ними
		#print
		length= g['s12']/1000.0
		width1 = geod.Inverse(fil.latmin, fil.lonmin, fil.latmin, fil.lonmax)
		width2 = geod.Inverse(fil.latmax,  fil.lonmin, fil.latmax, fil.lonmax)
		width=(width1['s12']+width2['s12'])/2.0/1000.0
		#print int(length), int(width), int(geod.Inverse(fil.latmin,  fil.lonmin, fil.latmin, fil.lonmax)['s12']/1000.0)
		oxToSrc=int(geod.Inverse(fil.latmin,  fil.lonmin, fil.latmin, srcPosLon)['s12']/1000.0) #Похиция источника по х
		oyToSrc=int(geod.Inverse(fil.latmin,  fil.lonmin, srcPosLat, fil.lonmin)['s12']/1000.0) #Позиция источника по у
		#print oxToSrc, oyToSrc
		
		fig = plt.figure()
		ax1 = fig.add_subplot(111)
		img = Image.open('123.png')
		ax1.imshow(img, extent=[0, fil.countx-1, 0, fil.county-1])
		x = np.arange (0,fil.countx, 1)
		y = np.arange (0,fil.county, 1)
		xgrid, ygrid = np.meshgrid(x, y)
		levels = [0.00001, 0.0001, 0.001, 0.01, 0.1, 1.0, 10.0, 100.0, 1000.0] #Уровни изолиний
		c = ('#000000', '#5342f4', '#41a0f4', '#41f48b', '#d9f441', '#f47f41', '#f44341','#f90200', '#000000') #Цвета для этих уровней
		contour = plt.contour(xgrid, ygrid, sumArray, levels, colors=c)
		#plt.clabel(contour, colors = 'k', fmt = '%2.4f', fontsize=12) #Для подписей значений на изолиниях
		contour_filled = plt.contourf(xgrid, ygrid, sumArray, levels, colors=c, alpha=0.5) #Закрашивает области внутри изолиний цветом самих изолиний
		#plt.colorbar(contour_filled) # Показывает соответствие цвета и значения
		plt.xlabel(u'x (км)')
		plt.ylabel(u'y (км)')
		ss=(u"Год ")+(time.strftime('%Y ', time.localtime(1451595600+int(ii)*7200)))+ (u"Месяц ")+(time.strftime('%m ', time.localtime(1451595600+int(ii)*7200)))+(u"День ")+(time.strftime('%d ', time.localtime(1451595600+int(ii)*7200)))+(u"Час ")+(time.strftime('%H ', time.localtime(1451595600+int(ii)*7200)))
		plt.title(ss)
		xlabels = []
		ylabels = []
		aa = np.arange(-(oxToSrc//10)*10, ((width-oxToSrc)//10)*10+1, 20)  #Подписи осей +1 для того, чтобы учесть границу
		print aa
		xx=np.append([-oxToSrc], aa)
		xx=np.append(xx, int(width-oxToSrc))
		print xx
		yy = np.arange(-oyToSrc, length-oyToSrc, 20)  #Подписи осей
		txx = np.arange(0, fil.countx-1, 10) #Значения осей
		tyy = np.arange(0, fil.county-1, 16.6) #Значения осей
		ax1.set_xticks(txx) #Устанавливаем значения по х
		ax1.set_yticks(tyy) #Устанавливаем значения по у
		#print xx
		for i in xx:
			xlabels.append('%d' % i)
		for i in yy:
			ylabels.append('%d' % i) 
		#print xlabels
		ax1.set_xticklabels(xlabels)	#Ставим подписи по х
		ax1.set_yticklabels(ylabels)	#Ставим подписи по у


		save(str(ii))
		break
		
			
		

	return 



if __name__ == "__main__":
	sys.exit(main())
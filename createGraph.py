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
from matplotlib import rcParams
mpl.rcParams['font.family'] = 'fantasy'
mpl.rcParams['font.fantasy'] = 'Times New Roman', 'Ubuntu','Arial','Tahoma','Calibri'

#1451606400
import time
print(time.gmtime(0))


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
    pwd = os.getcwd()
   # print datetime.fromtimestamp(int(ii*7200))
    global ii
    #plt.title(str("day "+str(int(float(name)*2.0/24.0))+"  time  "+str(int(name)*7200)+"  s"))
    pathToFolder=pwd+"/pictures/"
    #plt.title("u\'"+str(time.strftime('Day %d Month %m Year %Y  %H hours', time.localtime(1451595600+int(name)*7200)))+"\'")
    if os.path.isdir(pathToFolder)==False:
		os.mkdir(pathToFolder)
    iPath = './pictures/{}'.format(fmt)
    if not os.path.exists(iPath):
        os.mkdir(iPath)
    os.chdir(iPath)
    nul = 8-len(name)
    plt.savefig('{:0>8s}.{}'.format(name, fmt), fmt='png', pad_inches=0.1, dpi=300)
    os.chdir(pwd)
    plt.close()
    return



def main():
	#"f134","f135","f141"
	alltime = 366*24*3600/7200
	for ii in range(alltime+1):
		
		maxx=0.0
		print ii*7200
		sumArray=np.array([[0.0]*101]*101)
		resArray=np.array([[0.0]*101]*101)
		path = pathToOut+"/"+str(ii*7200)+" s/"+"out.xml"
		source = open(path, 'rb')
		et = xml.etree.ElementTree.parse(path)
		root = et.getroot()
		grid = root.find('grid')
		for gridFunctionID, gridFunction in enumerate(grid.findall('gridFunction')):
			fil = GeoGrid(gridFunction)
			#print gridFunctionID
			if (gridFunctionID == 134) or (gridFunctionID == 135) or (gridFunctionID == 141):
				#print gridFunctionID
				#fil.printASCIIGRDFile(myWorkPath+"/TIC/"+subDir.split(ident)[1].split("_")[1]+".grd")
				
				resArray = np.array(fil.grap)
				#print len(fil.grap), len(resArray), len(resArray[0])
				resArray = np.transpose(resArray)
				sumArray=sumArray + resArray

			del fil
		#maxx=np.max(sumArray)
		#newmaxx=maxx*0.1
		#for i in range(len(sumArray)):
		#	for j in range(len(sumArray[i])):
		#		if float(sumArray[i][j])>newmaxx:
		#			sumArray[i][j]=newmaxx
		if ii==ii:
			fig = plt.figure()
			ax1 = fig.add_subplot(111)
			img = Image.open('123.png')

			ax1.imshow(img, extent=[0, 100, 0, 100])
			x = np.arange (0,101, 1)
			y = np.arange (0,101, 1)
			xgrid, ygrid = np.meshgrid(x, y)

			levels = [0.0001, 0.001, 0.01, 0.1, 1.0, 10.0, 100.0, 1000.0]
			c = ('#5342f4', '#41a0f4', '#41f48b', '#d9f441', '#f47f41', '#f44341','#f90200', '#000000')
			contour = plt.contour(xgrid, ygrid, sumArray, levels, colors=c)
			#plt.clabel(contour, colors = 'k', fmt = '%2.4f', fontsize=12)
			#plt.clabel(contour, colors = 'k')
			contour_filled = plt.contourf(xgrid, ygrid, sumArray, levels, colors=c, alpha=0.5)
			#plt.colorbar(contour_filled)
			plt.xlabel(u'x (км)')
			plt.ylabel(u'y (км)')
			ss=(u"Год ")+(time.strftime('%Y ', time.localtime(1451595600+int(ii)*7200)))+ (u"Месяц ")+(time.strftime('%m ', time.localtime(1451595600+int(ii)*7200)))+(u"День ")+(time.strftime('%d ', time.localtime(1451595600+int(ii)*7200)))+(u"Час ")+(time.strftime('%H ', time.localtime(1451595600+int(ii)*7200)))
			plt.title(ss)
    
			xlabels = []
			ylabels = []
			xx = np.arange(-60, 80, 20)
			txx = np.arange(0, 100, 16.6)
			ax1.set_xticks(txx)
			ax1.set_yticks(txx)
			#print xx
			for i in xx:
				xlabels.append('%d' % i)
				ylabels.append('%d' % i)
			#print xlabels
			ax1.set_xticklabels(xlabels)
			ax1.set_yticklabels(ylabels)
			

		save(str(ii))

			
		

	return 



if __name__ == "__main__":
	sys.exit(main())
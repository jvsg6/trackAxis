#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import sys
import os

from math import cos,sin,radians,sqrt,fabs,acos,pi,degrees,floor

import xml.etree.ElementTree
from geographiclib.geodesic import Geodesic
from geopy.distance import VincentyDistance
geod = Geodesic.WGS84
import numpy as np
import openpyxl
axeRadius = [0.0,0.2,0.4,0.6,0.8,1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0,12.0,14.0,16.0,18.0,20.0,
			22.0,24.0,26.0,28.0,30.0,32.0,34.0,36.0,38.0,40.0,42.0,44.0,46.0,48.0,50.0,
		52.0,54.0,56.0,58.0,60.0,62.0,64.0,66.0,68.0,70.0,72.0,74.0,76.0,78.0,80.0,
			82.0,84.0,86.0,88.0,90.0,92.0,94.0,96.0,98.0,100.0]
tab=2 #ключ заполнения таблицы. Если 1, то заполняется процентами, если другое число, то ноликами и единичками
distance=10 #Расстояние при котором точки можно считать совпадающими
percent=95 #Процент совпадения точек, при котором можносчитать совпадающими оси следа
pathToAxis="/home/egor/work/Axis/"
axePoints=[]


def main():
	global axePoints
	length=float(len(axeRadius)-4)
	axePoints2=[]
	mypath = os.path.dirname(os.path.realpath(__file__))
	os.chdir(mypath)
	lst=[]
	wb = openpyxl.Workbook()
	ws = wb.worksheets[0]
	ws.title = u'Сравнение осей следа'
	for filename in os.listdir(str(pathToAxis)):
		lst.append(filename)
	lst.sort()
	for j in range(len(lst)): #перебираем все функционалы(1ый функц. для сравнения)(что сравниваем)
		axePoints = []
		print lst[j]
		#ws['A'+str(j+2)] = format(str(lst[j].split('_')[1].split('.')[0]))
		ws.cell(row=1, column=j + 2, value=str(lst[j].split('_')[1].split('.')[0]))
		ws.cell(row=j+2, column=1, value=str(lst[j].split('_')[1].split('.')[0]))
		f  = open(str(pathToAxis + str(lst[j])))
		string = f.read()
		f.close()
		for i in range(len(axeRadius)-4): #перебираем все точки оси следа в функционале, заполняем массив для сравнения
			point=[]
			lst2 = string.split("\n")
			point = [float(lst2[i].split(" ")[0].replace('\r','').replace(',', '')), float(lst2[i].split(" ")[1].replace('\r','').replace(',', '')) ]
			axePoints.append(point)
		k=j #чтобы не пересчитывать все по 2 раза
		for k in range(j, len(lst)): #перебира по всем функц. (2ой функционал для сравнения)(с чем сравниваем) от jтого функционал и до конца, чтобы 2 раза не пересчитывать

			if k==j:
				ws.cell(row=k+2, column=k+2, value=str("//////////////"))
				continue
			#print lst[k]
			f2 = open(str(pathToAxis + str(lst[k])))
			string2 = f2.read()
			f2.close()
			n=0
			axePoints2 = []
			for i in range(len(axeRadius) - 4):  #во 2ом функционале сравниваем все точки с первым
				point=[]
				lst2 = string2.split("\n")
				point = [float(lst2[i].split(" ")[0].replace(',', '').replace('\r', '')), float(lst2[i].split(" ")[1].replace(',', '').replace('\r', ''))]
				axePoints2.append(point)
				# g = geod.Inverse(lat1, lon1, lat2, lon2) distance between lat1;lon1 and lat2, lon2
				g = geod.Inverse(float(axePoints[i][1]), float(axePoints[i][0]), float(axePoints2[i][1]), float(axePoints2[i][0]))#расстояние между ними
				#print "The distance is {:.3f} m.".format(g['s12'])
				if g['s12'] < distance:
					n=n+1
					#print "The distance is {:.3f} m.".format(g['s12'])
			#print str("compare {0} vs {1}".format(str(lst[j]), str(lst[k])))
			if tab == 1:
				var="per"
				ws.cell(row=j + 2, column=k + 2, value="{:.1f}".format(float(n / 56.0 * 100.0)))
				ws.cell(row=k + 2, column=j + 2, value="{:.1f}".format(float(n / 56.0 * 100.0)))
			else:
				var="01"
				if float(n/length*100.0)>float(percent): #симметрично заполняем таблицу относительно диагонали
					ws.cell(row=j + 2, column=k + 2, value=str("1"))
					ws.cell(row=k+2, column=j+2, value=str("1"))   #симметрично заполняем таблицу относительно диагонали
				else:
					ws.cell(row=j + 2, column=k + 2, value=str("0"))
					ws.cell(row=k + 2, column=j + 2, value=str("0"))   #симметрично заполняем таблицу относительно диагонали
	wb.save(mypath + "/Compare_{0}_{1}_{2}.xlsx".format(str(var), str(distance), str(percent)))
	return


if __name__ == "__main__":
	sys.exit(main())

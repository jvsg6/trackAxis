#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import sys
import os
import xml.etree.ElementTree as etree
from math import cos,sin,radians,sqrt,fabs,acos,pi,degrees,floor,log10
import xml.etree.ElementTree
import matplotlib.pyplot as plt
import openpyxl
from openpyxl import load_workbook
import numpy as np
path="/home/egor/work/CompareAll"



def main():
	lst=[]
	for i in range(207):
		lst.append([])
	wb_new = openpyxl.Workbook()
	ws_new = wb_new.worksheets[0]
	ws_new.title = u'Сравнение осей следа'
	numAxis=np.array([0.0]*207)
	alltime = 366*24*3600/7200
	for ii in range(alltime+1):
		name=str(path + "/Axis_"+str(ii*7200)+".xlsx")
		wb = load_workbook(name)
		ws = wb.active
		numAxis[int(ws.cell(row=2, column=2).value)+1]+=1
		lst[int(ws.cell(row=2, column=2).value)+1].append(ii*7200)
		#ws_new.cell(row=2, column=2, value=ii*7200)
		print ii*7200
		#print lst
		if ii*7200==24897600:
			break
	#print numAxis, len(lst), len(lst[4])
	summ=0.0
	ws_new.cell(row=1, column=1, value=u'Количество Осей Следа')
	ws_new.cell(row=2, column=1, value=u'процент такого же количества от всех')
	for i in range(len(numAxis)):
		summ+=numAxis[i]
	for i in range(len(lst)):
		ws_new.cell(row=1, column=2+i, value=i)
		if i>=1:
			ws_new.cell(row=2, column=i+1, value=numAxis[i]/summ*100.0)
		for j in range(len(lst[i])):
			
			ws_new.cell(row=3+j, column=1+i, value=lst[i][j])
			
	wb_new.save('end.xlsx')
		
		



	return 



if __name__ == "__main__":
	sys.exit(main())
#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#Для работы использует файл ".cfg"
#Для создания видео с помощью fmpeg ввести в консоли: "ffmpeg -r 3 -f image2 -i %08d.png -f mp4 -q:v 0 -vcodec mpeg4 -r 24 myVideo.flv" 
#Где 3 - Количество кадров в секунду; %08d.png - формат названия файлов(в названии 8 символов, все нули, кроме номера фото); myVideo.flv - название видео с его форматом
import sys
import os
import time
import datetime
import numpy as np
from openpyxl import Workbook
from math import cos,sin,radians,sqrt,fabs,acos,pi,degrees,floor,log10
from PIL import Image
import xml.etree.ElementTree
import matplotlib as mpl
import matplotlib.pyplot as plt
import ConfigParser

from geographiclib.geodesic import Geodesic
from geopy.distance import VincentyDistance
geod = Geodesic.WGS84


from netCDF4 import Dataset

from grids.GNR2D import *
from grids.gridResults import *

import argparse, arghelper
from additionalfunctions import *


from matplotlib import rcParams
mpl.rcParams['font.family'] = 'fantasy'
mpl.rcParams['font.fantasy'] = 'Times New Roman', 'Ubuntu','Arial','Tahoma','Calibri'

#Позиция источника
conf = ConfigParser.RawConfigParser()
conf.read("akkuyu.cfg")
srcPosLon = float(conf.get("npp", "lon"))
srcPosLat = float(conf.get("npp", "lat"))





	
def labelsAxis(gridfil, dist, toSrc, axisCount, delta):
	labels = []
	aa = np.arange(-(toSrc//delta)*delta, ((dist-toSrc)//delta)*delta+1, delta)  #Подписи осей +1 для того, чтобы учесть границу
	axisArr=np.append([-toSrc], aa)
	axisArr=np.append(axisArr, int(dist-toSrc))
	#print axisArr, len(axisArr)
	left=(toSrc%delta)/dist
	right=((dist-toSrc)%delta)/dist
	valLeft=(axisCount-1)*left
	valRight=(axisCount-1)*right
	delx=delta/((toSrc//delta)*delta+((dist-toSrc)//delta)*delta+1)*(axisCount-1-valLeft-valRight)
	#print left, valLeft, right,valRight, delx
	val=np.array([])
	val = np.append([0.0], np.arange(valLeft, axisCount, delx)) #Значения осей
	val = np.append( val, val[len(val)-1]+valRight)
	val[len(val)-1]=axisCount-1
	#print np.arange(left, axisCount, delx)
	#print val, len(val)
	#print axisArr
	for n, i in enumerate(axisArr):
		if n==0 or n==len(axisArr)-1:
			labels.append('') #Убираем подписи на границах
			continue			
		labels.append('%d' % i)
	return labels, val
def create2D(obj):
	result = [[0.0]*obj.county]*obj.countx
	for j in range(obj.countx): #количество строк
		result[j] = obj.data[j*obj.county:(j+1)*obj.county]
	
	result = np.array(result)#fil.grap)
	result = np.transpose(result)

	return result
def sortByLength(inputStr):
	try:
		return int(inputStr.split(" ")[0]) #Если папки с названиями вида "0 s"; "7200 s"....
	except ValueError:
		try:
			return int(inputStr.split("_")[3]) #Если папки с названиями вида Mayak_local_100_0_10_0; Mayak_local_100_7200_10_1....
		except ValueError:
			print "Определите в имени папок позицию для сортировки."
	
def createGraph(fil, oFileFolder, oFileType, funcId, directotyId):
	global oxToSrc, oyToSrc
	resArray = create2D(fil)
	# g = geod.Inverse(lat1, lon1, lat2, lon2) distance between lat1;lon1 and lat2, lon2
	g = geod.Inverse(fil.latmin, fil.lonmin, fil.latmax, fil.lonmin)#расстояние между ними
	length= g['s12']/1000.0
	gwidth = geod.Inverse(srcPosLat, fil.lonmin, srcPosLat, fil.lonmax)
	width=(gwidth['s12'])/1000.0

	oxToSrc=int(geod.Inverse(srcPosLat,  fil.lonmin, srcPosLat, srcPosLon)['s12']/1000.0) #Позиция источника по х в километрах
	oyToSrc=int(geod.Inverse(fil.latmin,  srcPosLon, srcPosLat, srcPosLon)['s12']/1000.0) #Позиция источника по у в километрах

	fig = plt.figure()
	ax1 = fig.add_subplot(111)
	img = Image.open('./bg/ijevsk.png')  #Фон
	ax1.imshow(img, extent=[0, fil.countx-1, 0, fil.county-1]) #Разбиваем фон на нужное число точек
	x = np.arange (0,fil.countx, 1)
	y = np.arange (0,fil.county, 1)
	xgrid, ygrid = np.meshgrid(x, y)
	levels = [ 0.00001, 0.0001, 0.001, 0.01, 0.1, 1.0, 10.0, 100.0, 1000.0, 10000.0] #Уровни изолиний
	c = ('#5342f4', '#41a0f4', '#41f48b', '#d9f441', '#f47f41', '#f44341','#f90200', '#8f1400', '#6b0f00') #Цвета для этих уровней
	contour = plt.contour(xgrid, ygrid, resArray, levels, colors=c) #Строит изолинии
	#plt.clabel(contour, colors = 'k', fmt = '%2.4f', fontsize=12) #Для подписей значений на изолиниях
	contour_filled = plt.contourf(xgrid, ygrid, resArray, levels, colors=c, alpha=0.5) #Закрашивает области внутри изолиний цветом самих изолиний
	plt.colorbar(contour_filled, alpha= 0, format = '%2.5f')  # Показывает соответствие цвета и значения
	plt.xlabel(u'x (км)')
	plt.ylabel(u'y (км)')
	#ss=(u"Год ")+(time.strftime('%Y ', time.localtime(1451595600+int(directotyId)*7200)))+ (u"Месяц ")+(time.strftime('%m ', time.localtime(1451595600+int(directotyId)*7200)))+(u"День ")+(time.strftime('%d ', time.localtime(1451595600+int(directotyId)*7200)))+(u"Час ")+(time.strftime('%H ', time.localtime(1451595600+int(directotyId)*7200)))

	#plt.title(ss)

	label, val = labelsAxis(fil, width, oxToSrc, fil.countx, int(delta))
	ax1.set_xticks(val) #Устанавливаем значения по х
	ax1.set_xticklabels(label)	#Ставим подписи по х

	label, val = labelsAxis(fil, length, oyToSrc, fil.county, int(delta))
	ax1.set_yticks(val) #Устанавливаем значения по у
	ax1.set_yticklabels(label)	#Ставим подписи по у
	print  "Save in: ", oFileFolder, str(funcId)
	try: 
		os.makedirs(oFileFolder+"/Func_"+str(funcId))
	except OSError:
		if not os.path.isdir(oFileFolder+"/Func_"+str(funcId)):
			raise
	pathToSave = str(oFileFolder+"/Func_"+str(funcId)+'/{:0>8s}.{}'.format(str(directotyId), oFileType))
	plt.savefig(pathToSave, format = oFileType, pad_inches=0.1, dpi=300)
	plt.close()
	
	return
	
def main(iFilePath, iFileType,  oFileFolder, oFileType, funcNum, delta):
	global oxToSrc, oyToSrc
	if iFileType == "grd":
		for funcId in funcNum:
			fil = readFromSurferGRD(iFilePath+"/f"+funcId+".grd")
			createGraph(fil, oFileFolder, oFileType, funcId, funcId)
			
	elif iFileType == "nc" or iFileType == "xml":
		dirs = os.listdir(iFilePath) #Считываем файлы в директории
		dirs.sort(key=sortByLength)	#Сортируем по возрастанию, НАДО ЗАДАТЬ МЕСТО ДЛЯ СОРТИРОВКИ В ФУНКЦИИ sortByLength
		for directotyId, directory in enumerate(dirs): #Сделать цикл по директориям
			fil = None
			dataset = None
			path = iFilePath+"/"+dirs[directotyId]+"/"+"out.{}".format(iFileType)
			if iFileType == "nc":
				dataset = Dataset(path) #Открываем netcdf4 файл
				num = GNR_Netcdf4.getGridsCount(dataset)
			elif iFileType == "xml":
				et = xml.etree.ElementTree.parse(path)
				root = et.getroot()
				grid = root.find('grid')
				dataset = grid.findall('gridFunction')
				num = GNR_XML.getGridsCount(dataset)

			print directotyId*7200, directotyId, path
			for funcId in funcNum:
				if iFileType == "nc":
					fil = GNR_Netcdf4()
				elif iFileType == "xml":
					fil = GNR_XML()
				if int(funcId) > num:
					print "Warning: There is no function with number {}".format(str(funcId))
					continue
				fil.initById(dataset, int(funcId))
				prop=fil.properties
				createGraph(fil, oFileFolder, oFileType, funcId, directotyId)

	return 

if __name__ == "__main__":
	try:
		mypath = os.path.dirname(os.path.abspath(__file__))
	except NameError:
		mypath = os.path.dirname(os.path.abspath(sys.argv[0]))
	os.chdir(mypath)
	if len(sys.argv) == 1: sys.argv[1:] = ["-h"]
	parser = argparse.ArgumentParser()
	parser._action_groups.pop()
	required = parser.add_argument_group('required arguments')
	optional = parser.add_argument_group('optional arguments')
	
	required.add_argument('--iff', action = 'store', dest='iFileFolder',  type=str, help='path to the input folder with results in nostra output format', required=True)
	required.add_argument('--iftype', choices=['xml', 'nc', 'grd'], dest='iFileType',  type=str, help='type of the input file with nostra results', required=True)
	required.add_argument ('-fn', nargs='+', dest='funcNum',help='Write space separated numbers of functions for output', required=True)
	
	optional.add_argument('--off', action = 'store', dest='oFileFolder',metavar='OUTPUT_FOLDER', type=lambda x: arghelper.is_valid_directory(parser, x), help='path to the output folder for output files', required=False, default=mypath)
	optional.add_argument('--ofnf', action = 'store', dest='oFileNewFolder',metavar='NEW_FOLDER', type=str, help='path to the new output folder for output files', required=False, default="")
	optional.add_argument('--oftype', choices=['png', 'jpg'], dest='oFileType',  type=str, help='type of the output file with nostra results (default is png format)', required=False, default='png')
	optional.add_argument('--delta', action = 'store', dest='delta',  type=str, help='Interval of division of axes (in kilometers, default 30).', default=30)
	
	args_new = parser.parse_args()
	
	oFileFolder = args_new.oFileFolder
	if args_new.oFileNewFolder != '':
		if os.path.exists(args_new.oFileNewFolder) == False:
			make_sure_path_exists(args_new.oFileNewFolder)
		oFileFolder = args_new.oFileNewFolder.strip()

	iFilePath = args_new.iFileFolder.strip()
	iFileType = args_new.iFileType.strip()
	oFileType = args_new.oFileType.strip()
	errFuncNum = False
	errDelta = False
	
	delta = args_new.delta
	try:
		int(delta)
	except ValueError:
		print "Delta must be int, not {}".format(delta)
		errDelta = True
		
		
	funcNum = args_new.funcNum
	for i in funcNum:   #Проверка на правильность ввода номеров Функционалов
		try:
			int(i)
		except ValueError:
			print "Function number must be int, not {}".format(i)
			errFuncNum = True
	if errFuncNum == False:
		if errDelta == False:
			sys.exit(main(iFilePath, iFileType,  oFileFolder, oFileType, funcNum, int(delta)))
		else:
			print "Error with delta"
	else:
		print "Error with function number"
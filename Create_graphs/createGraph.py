#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#Для работы использует файл ".cfg" и картинку с названием bg.png(в качестве фона при построении графиков). Они должны лежать в одной папке с модулем
#Для создания видео с помощью fmpeg ввести в консоли: "ffmpeg -r 3 -f image2 -i %08d.png -f mp4 -q:v 0 -vcodec mpeg4 -r 24 myVideo.flv" 
#Где 3 - Количество кадров в секунду; %08d.png - формат названия файлов(в названии 8 символов, все нули, кроме номера фото); myVideo.flv - название видео с его форматом
#Нужно двшить белый фон в exe файл
import sys
import os
import time
import datetime

import ConfigParser
from math import cos,sin,radians,sqrt,fabs,acos,pi,degrees,floor,log10
from grids.GNR2D import *
from grids.gridResults import *

import argparse, arghelper
from additionalfunctions import *
user = False
try:
	import xml.etree.ElementTree
	xmlFlag = True
except ImportError:
	print "Warning: The module xml is not installed."
	xmlFlag = False

try:
	import numpy as np
	npFlag = True
except ImportError:
	print "Warning: The module numpy is not installed. To support numpy install the module (pip install numpy)"
	npFlag = False

try:
	from PIL import Image
	pilFlag = True
except ImportError:
	print "Warning: The module pillow is not installed. To support pillow install the module (pip install pillow)"
	pilFlag = False

try:
	import matplotlib as mpl
	import matplotlib.pyplot as plt
	from matplotlib import rcParams
	from matplotlib import gridspec
	import matplotlib.patches as patches
	import pylab
	mpl.rcParams['font.family'] = 'fantasy'
	mpl.rcParams['font.fantasy'] = 'Times New Roman', 'Ubuntu','Arial','Tahoma','Calibri'
	mplFlag = True
except ImportError:
	print "Warning: The module matplotlib is not installed. To support matplotlib install the module (pip install matplotlib)"
	mplFlag = False

try:
	from geographiclib.geodesic import Geodesic
	geod = Geodesic.WGS84
	geographiclibFlag = True
except ImportError:
	print "Warning: The module geographiclib is not installed. To support geographiclib install the module (pip install geographiclib)"
	geographiclibFlag = False
	
try:
	import geopy
	from geopy.distance import vincenty
	geopyFlag = True
except ImportError:
	print "Warning: The module geopy is not installed. To support geopy install the module (pip install geopy)"
	geopyFlag = False

try:
	from netCDF4 import Dataset
	netcdf4Flag = True
except ImportError:
	netcdf4Flag = False
	print "Warning: The module is not installed. To support netcdf4 install the module (pip install netcdf4)"



srcPosLon = 0.0
srcPosLat = 0.0

axeRadius = [0.0,0.2,0.4,0.6,0.8,1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0,12.0,14.0,16.0,18.0,20.0,
			22.0,24.0,26.0,28.0,30.0,32.0,34.0,36.0,38.0,40.0,42.0,44.0,46.0,48.0,50.0,
		52.0,54.0,56.0,58.0,60.0,62.0,64.0,66.0,68.0,70.0,72.0,74.0,76.0,78.0,80.0,
			82.0,84.0,86.0,88.0,90.0,92.0,94.0,96.0,98.0,100.0]

legendFig = []
legendLab = []
	
def labelsAxis(gridfil, dist, toSrc, axisCount, delta): #gridfil - экземпляр класса GRN_2D, dist - ширина или длина области, toSrc - расстояние от начала оси до источника в километрах, delta - цена деления оси
	
	#Строим массив значений подписей осей, которые укладываются в целое число delta, +1 для того, чтобы учесть границу
	aa = np.arange(-(toSrc//delta)*delta, ((dist-toSrc)//delta)*delta+1, delta)  

	
	#Добавляем границы справа и слева, которые не попали
	axisArr=np.append([-toSrc], aa)
	axisArr=np.append(axisArr, (dist-toSrc))
	#Добавили
	

	#Вычисляем остатки справа и слева, тк у нас не целое число delta умещается, делим на dist, чтобы получить относительные остатки
	left=(toSrc%delta)/dist
	right=((dist-toSrc)%delta)/dist
	#Вычислили

	#Вычисляем длину остатков, относительно количества интервалов по осям
	valLeft=(axisCount-1)*left
	valRight=(axisCount-1)*right
	#Вычислили
	
	#Вычисляем дельту, только уже не в километрах, а в интервалах
	cutlength = (axisCount-1-valLeft-valRight) #Обрезаем длину по интервалам(минусуем остатки)
	delx=delta/((toSrc//delta)*delta+((dist-toSrc)//delta)*delta)*cutlength
	#Вычислили
	
	#Строим массив значений, на который потом накладываем подписи
	val=np.array([])
	val = np.append([0.0], np.arange(valLeft, axisCount, delx)) #Записываем значения осей в интервалах
	val = np.append( val, val[len(val)-1]+valRight) #Добавляем границу справа
	val[len(val)-1]=axisCount-1 #На всякий случай меняем вычисленную границу справа на всю длину интервалов
	#Построили
	
	#Строим список подписей
	labels = []
	for n, i in enumerate(axisArr):
		if n==0 or n==len(axisArr)-1:
			labels.append('') #Убираем подписи на границах
			continue			
		labels.append('%d' % i)
	#Построили
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
def readTrackAxis(plt, fil, pathToAxis, funcId, maxValAxis, notAddAxisPoints):
	global axeRadius
	f = None
	try:
		f = open(pathToAxis+"/maxPoint_f{0}.dat".format(funcId), 'r')
	except:
		print "Error with trackAxis"
		return
	string = f.read()
	f.close()
	lst2 = string.split("\n")
	del lst2[-1]
	axeMaxPoints = []
	tmpVal = 0.0
	tmpDist = 0.0
	oldVal = 0.0
	first = True
	for lineId, line in enumerate(lst2):
		if float(axeRadius[lineId])>=37.0:
			continue
		if maxValAxis == 0.0:
			tmpDist = 0.0
			break
		
		lon, lat, dist, val = float(line.split(";")[0]), float(line.split(";")[1]), float(line.split(";")[2]), float(line.split(";")[3])

		#print (lon-fil.lonmin)/(fil.lonmax-fil.lonmin)*(fil.countx), (lat-fil.latmin)/(fil.latmax-fil.latmin)*(fil.county), "x", fil.countx, "y", fil.county
		if oldVal > maxValAxis:#val>tmpVal:
			tmpVal = val
			tmpDist = dist	
		oldVal = val
		
		if notAddAxisPoints == True:
			pass
		else:	
			axeMaxPoints.append([(lon-fil.lonmin)/(fil.lonmax-fil.lonmin)*(fil.countx), (lat-fil.latmin)/(fil.latmax-fil.latmin)*(fil.county)])
			if first:
				point = plt.scatter((lon-fil.lonmin)/(fil.lonmax-fil.lonmin)*(fil.countx-1), (lat-fil.latmin)/(fil.latmax-fil.latmin)*(fil.county-1))
				legendFig.append(point)
				legendLab.append('Track axis points')
				first = False
				
			else:
				plt.scatter((lon-fil.lonmin)/(fil.lonmax-fil.lonmin)*(fil.countx-1), (lat-fil.latmin)/(fil.latmax-fil.latmin)*(fil.county-1))
	
	del axeMaxPoints [:]
	if oldVal == 0.0:
		tmpVal, tmpDist = 0.0, 0.0
	return tmpVal, tmpDist
	
def createGraph(fil, oFileFolder, oFileType, funcId, directotyId, Scale, pathToAxis, radii, maxValAxis, notAddAxisPoints, addSrcPoint, addColorbar, addLegend, bg, dimension, title, addCaptionCont):
	global oxToSrc, oyToSrc, legendFig, legendLab
	
	#Устанавливаем параметры, нужные для легенды
	if addLegend == True:
		rborder = 0.75
		rcParams['figure.subplot.right'] = rborder
		# Общая высота (вертикаль), выделенная для свободного пространства между subplots
		rcParams['figure.subplot.hspace'] = 0.15
		rcParams['figure.subplot.wspace'] = 0.15
		
	#Создаем 2Д массив
	resArray = create2D(fil)
	
	#Устанавливаем позицию источника
	# g = geod.Inverse(lat1, lon1, lat2, lon2) distance between lat1;lon1 and lat2, lon2
	glength = geod.Inverse(fil.latmin, fil.lonmin, fil.latmax, fil.lonmin)#расстояние между ними
	length= glength['s12']/1000.0
	gwidth = geod.Inverse(srcPosLat, fil.lonmin, srcPosLat, fil.lonmax)
	width=(gwidth['s12'])/1000.0
	oxToSrc=geod.Inverse(srcPosLat,  fil.lonmin, srcPosLat, srcPosLon)['s12']/1000.0 #Позиция источника по х в километрах
	oyToSrc=geod.Inverse(fil.latmin,  srcPosLon, srcPosLat, srcPosLon)['s12']/1000.0 #Позиция источника по у в километрах

	fig = plt.figure(figsize=(8, 6))
	ax1 = fig.add_subplot(111)
	#gs = gridspec.GridSpec(1, 2, width_ratios=[0., 1]) 
	#ax1 = plt.subplot(gs[0, 0])
	img = Image.open(bg)  #Фон
	ax1.imshow(img, extent=[0, fil.countx-1, 0, fil.county-1]) #Разбиваем фон на нужное число точек
	x = np.arange (0,fil.countx, 1)
	y = np.arange (0,fil.county, 1)
	xgrid, ygrid = np.meshgrid(x, y)

	levels, labels = calcLevelsAndLabels(Scale, fil, dimension) #Уровни изолиний

	c = ('darkgreen','g',"greenyellow", '#d9f441', '#f47f41', '#f44341','#f90200', '#8f1400', '#6b0f00', "indigo", "darkblue", '#5342f4', '#41a0f4') #Цвета для этих уровней
	contour = ax1.contour(xgrid, ygrid, resArray, levels,  colors=c) #Строит изолинии
	#Добавляем на график подписи к контуру
	if addCaptionCont == True:
		plt.clabel(contour, colors = 'k', fmt = '%2.4f', fontsize=12) #Для подписей значений на изолиниях
	
	
	contour_filled = ax1.contourf(xgrid, ygrid, resArray, levels, colors=c, alpha=0.5) #Закрашивает области внутри изолиний цветом самих изолиний
	legendFig = [plt.Rectangle((0,0),1,1,fc = pc.get_facecolor()[0]) for pc in contour_filled.collections]
	legendLab = labels#[str(label) for labelId, label in enumerate(levels) if labelId<=len(levels)-2]

	#Добавляем на рисунок цветовую палитру
	if addColorbar == True:
		plt.colorbar(contour_filled, alpha= 0, format = '%2.5f')  # Показывает соответствие цвета и значения
		
	#Добавляем название осей
	plt.xlabel(u'x (км)') #Подпись оси х
	plt.ylabel(u'y (км)') #Подпись оси у
	
	#Ограничиваем область графика
	pylab.xlim (0, fil.countx-1) #Ограничение области рисования x
	pylab.ylim (0, fil.county-1) #Ограничение области рисования y
	
	colour = [ "purple", "brown", "black", "pink","white", "green"]

	
	#Добавляем на график круги 
	if radii != []:
		for rId, r in enumerate(radii):
			dist = float(r)
			el = ax1.add_patch(patches.Ellipse((oxToSrc/width*(fil.countx-1),oyToSrc/length*(fil.county-1)),dist/width*(fil.countx-1)*2 ,dist/length*(fil.county-1)*2, hatch='/', fill=False,  edgecolor=colour[rId]))
			legendFig.append(el)
			legendLab.append("Circle with radius {} km".format(r))
			print "Circle done with r = ", dist
			
	#Добавляем на график ось слда
	if pathToAxis != '':
		val, dist = readTrackAxis(ax1, fil, pathToAxis, funcId, maxValAxis, notAddAxisPoints)
		el = ax1.add_patch(patches.Ellipse((oxToSrc/width*(fil.countx-1),oyToSrc/length*(fil.county-1)),dist/width*(fil.countx-1)*2 ,dist/length*(fil.county-1)*2, hatch='\\', fill=False,  edgecolor='red', label="Circle with radius {} km".format(dist)))
		legendFig.append(el)
		legendLab.append("Circle with radius {} km".format(dist))
		print dist
		
	#Добавляем на рисунок заголовок
	if title != "":
		plt.title(title)
	
	# Добавляем на график позицию источника
	if addSrcPoint:
		point = plt.scatter(oxToSrc/width*(fil.countx-1),oyToSrc/length*(fil.county-1), label="Source position", marker=(5, 1), c='red', s=100)
		legendFig.append(point)
		legendLab.append("Source position")
		
	#Добавляем на рисунок легенду
	if addLegend == True:
		#print proxy
		plt.legend(legendFig, legendLab, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0., fontsize=8)
		#plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0., fontsize=8)

		
	#Устанавливаем подписи осей
	#Ось Х
	label, val = labelsAxis(fil, width, oxToSrc, fil.countx, int(delta))
	ax1.set_xticks(val) #Устанавливаем значения по х
	ax1.set_xticklabels(label)	#Ставим подписи по х
	#Ось У
	label, val = labelsAxis(fil, length, oyToSrc, fil.county, int(delta))
	ax1.set_yticks(val) #Устанавливаем значения по у
	ax1.set_yticklabels(label)	#Ставим подписи по у
	
	#Сохраняем рисунки
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
def calcLevelsAndLabels(Scale, fil, dimension):
	labels = []

	if user == False:
		MIN = float(Scale[0])
		MAX = float(Scale[1])
		tmpLevels = []
		num = 1
		while MIN<MAX:
			tmpLevels.append(MIN)
			MIN = MIN*10
			num = num+1
		tmpLevels.append(MAX)
		for valId, val in enumerate(tmpLevels[:-1]):
			labels.append("Value, more than {0} {2}\nless than {1} {2}".format(tmpLevels[valId], tmpLevels[valId+1], dimension))
	else:
		if len(Scale) == 1:
			labels.append("Value, more than {0} {1}".format(Scale[0], dimension))
			Scale.append(fil.fmax)
			Scale = [float(n) for n in Scale]
			return Scale, labels
		else:
			
			Scale = [float(n) for n in Scale]
			Scale.sort()
			tmpLevels = Scale
			for valId, val in enumerate(tmpLevels[:-1]):
				labels.append("Value, more than {0} {2}\nless than {1} {2}".format(tmpLevels[valId], tmpLevels[valId+1], dimension))
	return tmpLevels, labels
	
def main(iFilePath, iFileType,  oFileFolder, oFileType, funcNum, delta, Scale, pathToConfigure, pathToAxis, radii, maxValAxis, notAddAxisPoints, addSrcPoint, addColorbar, addLegend, bg, dimension, title, addCaptionCont):
	global oxToSrc, oyToSrc, srcPosLon, srcPosLat
	#Позиция источника
	conf = ConfigParser.RawConfigParser()
	conf.read(pathToConfigure)
	srcPosLon = float(conf.get("npp", "lon"))
	srcPosLat = float(conf.get("npp", "lat"))
	if iFileType == "grd":
		for funcId in funcNum:
			fil = readFromSurferGRD(iFilePath+"/f"+funcId+".grd")
			createGraph(fil, oFileFolder, oFileType, funcId, funcId, Scale, pathToAxis, radii, maxValAxis, notAddAxisPoints, addSrcPoint, addColorbar, addLegend, bg, dimension, title, addCaptionCont)
			
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
				createGraph(fil, oFileFolder, oFileType, funcId, directotyId, Scale, pathToAxis, radii, maxValAxis, notAddAxisPoints, addSrcPoint, addColorbar, addLegend, bg, dimension, title, addCaptionCont)
	return 

if __name__ == "__main__":
	if geographiclibFlag == False:
		print "\nError: The module geographiclib must be installed(pip install geographiclib)."
		sys.exit()
	if geopyFlag==False:
		print "\nError: The module geopy must be installed(pip install geopy)."
		sys.exit()
	if netcdf4Flag==False and xmlFlag==False:
		print "One of the modules must be installed(xml or netcdf)"
		sys.exit()
	if npFlag==False:
		print "\nError: The module numpy be installed(pip install numpy)."
		sys.exit()
	if pilFlag==False:
		print "\nError: The module pillow must be installed(pip install pillow)."
		sys.exit()
	if mplFlag==False:
		print "\nError: The module matplotlib must be installed(pip install matplotlib)."
		sys.exit()
		
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
	
	required.add_argument('--iff', action = 'store', dest='iFileFolder',  type=str, help='Path to the input folder with results in nostra output format', required=True)
	required.add_argument('--iftype', choices=['xml', 'nc', 'grd'], dest='iFileType',  type=str, help='Type of the input file with nostra results', required=True)
	required.add_argument('-fn', nargs='+', dest='funcNum',help='Write space separated numbers of functions for output', required=True)
	required.add_argument('--configureFile', action=arghelper.checkAndPrepareF({'cfg'}), dest='pathToConfigure', metavar='FILE', type=lambda x: arghelper.is_valid_file(parser, x), help='Path to file with settings', required=True)
	
	
	optional.add_argument('--off', action = 'store', dest='oFileFolder',metavar='OUTPUT_FOLDER', type=lambda x: arghelper.is_valid_directory(parser, x), help='Path to the output folder for output files', required=False, default=mypath)
	optional.add_argument('--ofnf', action = 'store', dest='oFileNewFolder',metavar='NEW_FOLDER', type=str, help='Path to the new output folder for output files', required=False, default="")
	optional.add_argument('--bg', action = 'store', dest='bg',  type=str, help='Path to the bachground for picture(default = ./bg.png)', required=False, default="bg.png")
	optional.add_argument('--pathToAxis', action = 'store', dest='pathToAxis',  type=str, help='Path to the folder with Track Axis', required=False, default="")
	optional.add_argument('--oftype', choices=['png', 'jpg'], dest='oFileType',  type=str, help='Type of the output file with nostra results (default is png format)', required=False, default='png')
	optional.add_argument('--delta', action = 'store', dest='delta',  type=str, help='Interval of division of axes (in kilometers, default 30).', default=30)
	optional.add_argument('-logscale', nargs='+', dest='logScale',help='Write space separated min and max value of log scale(for example 0.000001 10000)', required=False, default=[0.00001, 10000.0])
	optional.add_argument('-usrscale', nargs='+', dest='usrScale',help='Write space separated value of functional(for example 10 100 150 200)\nIf you want to display values that are greater than a certain number, write this value.', required=False, default=None)
	optional.add_argument('-radii', nargs='+', dest='radii',help='Write space separated value of circle in km (max 6 values)', required=False, default=[])
	optional.add_argument('--maxValAxis', action = 'store', dest='maxValAxis',  type=float, help='The value of the functional for drawing a circle along the track axis', default=0)
	optional.add_argument('--dimension', action = 'store', dest='dimension',  type=str, help='Dimension of function value (default = \"\")', required=False, default="")
	optional.add_argument('--title', action = 'store', dest='title',  type=str, help='Drawing header', required=False, default="")
	optional.add_argument('-notAddAxisPoints', action='store_const', dest='notAddAxisPoints',help='Use this flag to remove Axis points from graph', const=True)
	optional.add_argument('-addSrcPoint', action='store_const', dest='addSrcPoint',help='Use this flag to draw a source point on graph', const=True)
	optional.add_argument('-addColorbar', action='store_const', dest='addColorbar',help='Use this flag to add colorbar on picture', const=True)
	optional.add_argument('-addLegend', action='store_const', dest='addLegend',help='Use this flag to add legend on picture', const=True)
	optional.add_argument('-fillContour', action='store_const', dest='fillContour',help='Use this flag to fill contour', const=True)
	optional.add_argument('-addCaptionCont', action='store_const', dest='addCaptionCont',help='Use this flag to add captions to the contour', const=True)

	args_new = parser.parse_args()
	
	oFileFolder = args_new.oFileFolder
	if args_new.oFileNewFolder != '':
		if os.path.exists(args_new.oFileNewFolder) == False:
			make_sure_path_exists(args_new.oFileNewFolder)
		oFileFolder = args_new.oFileNewFolder.strip()

	pathToConfigure = args_new.pathToConfigure
	iFilePath = args_new.iFileFolder.strip()
	iFileType = args_new.iFileType.strip()
	oFileType = args_new.oFileType.strip()
	pathToAxis = args_new.pathToAxis.strip()
	maxValAxis = args_new.maxValAxis
	notAddAxisPoints = args_new.notAddAxisPoints
	addSrcPoint = args_new.addSrcPoint
	addColorbar = args_new.addColorbar
	addLegend = args_new.addLegend
	bg = args_new.bg
	dimension = args_new.dimension
	title = args_new.title
	fillContour = args_new.fillContour
	addCaptionCont = args_new.addCaptionCont
	
	errFuncNum = errDelta = errLogScale = errUsrScale = errRadii = False
	
	delta = args_new.delta
	try:	#Проверка на правильность ввода дельты
		int(delta)
	except ValueError:
		print "Delta must be int, not {}".format(delta)
		errDelta = True

		
	logScale = args_new.logScale
	for i in logScale:   #Проверка на правильность ввода номеров Функционалов
		try:
			float(i)
		except ValueError:
			print "Log scale  must be float, not {}".format(i)
			errLogScale = True		

	radii = args_new.radii
	for i in radii:   #Проверка на правильность ввода радиусов
		try:
			float(i)
		except ValueError:
			print "Radius  must be float, not {}".format(i)
			errRadii = True
	if len(radii)>6:
		errRadii = True
		print "Max 6 values for radius"

	usrScale = args_new.usrScale
	if usrScale != None:
		for i in usrScale:
			try:
				float(i)
			except ValueError:
				print "User scale  must be float, not {}".format(i)
				errUsrScale = True
	Scale = []
	if usrScale != None and errUsrScale == False:
		Scale = usrScale
		user = True
	elif errLogScale == False:
		Scale = logScale
	else:
		print "Error with scale"
		sys.exit()

	funcNum = args_new.funcNum
	for i in funcNum:   #Проверка на правильность ввода номеров Функционалов
		try:
			int(i)
		except ValueError:
			print "Function number must be int, not {}".format(i)
			errFuncNum = True
	if errFuncNum == False:	
		if errDelta == False:
			if errLogScale == False:
				if errRadii == False:
					
					sys.exit(main(iFilePath, iFileType,  oFileFolder, oFileType, funcNum, int(delta), Scale, pathToConfigure, pathToAxis, radii, maxValAxis, notAddAxisPoints, addSrcPoint, addColorbar, addLegend, bg, dimension, title, addCaptionCont))
				else:
					print "Error with radius"
			else:
				print "Error with Log Scale"
		else:
			print "Error with delta"
	else:
		print "Error with function number"
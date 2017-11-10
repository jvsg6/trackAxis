#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import sys


import os
import matplotlib.pyplot as plt
import numpy as np
axeRadius = [0.0,0.2,0.4,0.6,0.8,1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0,12.0,14.0,16.0,18.0,20.0,
			22.0,24.0,26.0,28.0,30.0,32.0,34.0,36.0,38.0,40.0,42.0,44.0,46.0,48.0,50.0,
		52.0,54.0,56.0,58.0,60.0,62.0,64.0,66.0,68.0,70.0,72.0,74.0,76.0,78.0,80.0,
			82.0,84.0,86.0,88.0,90.0,92.0,94.0,96.0,98.0,100.0, 120.0, 140.0, 160.0, 180.0, 200.0,
			220.0, 240.0, 260.0, 280.0, 300.0, 320.0, 340.0, 360.0, 380.0, 400.0, 420.0, 440.0,
			460.0, 480.0, 500.0]
aver=0.0
pathToPointsA="/home/egor/quest/Ru_106/G/Axis/maxPoint_f0.dat"
pathToPointsB="/home/egor/quest/Ru_106/B/Axis/maxPoint_f0.dat"
pathToPointsC="/home/egor/quest/Ru_106/C/Axis/maxPoint_f0.dat"
pathToPointsD="/home/egor/quest/Ru_106/D/Axis/maxPoint_f0.dat"
pathToPointsE="/home/egor/quest/Ru_106/E/Axis/maxPoint_f0.dat"
pathToPointsF="/home/egor/quest/Ru_106/F/Axis/maxPoint_f0.dat"
pathToPointsG="/home/egor/quest/Ru_106/G/Axis/maxPoint_f0.dat"
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
    #plt.close()

def graph (path):
	global x
	global y
	global fig
	global aver
	lst=[]
	x=np.array(axeRadius)
	#print(x)
	f=open(path, 'rt')
	string = f.read()
	f.close()
	lst = string.split("\n")
	lst2 = [0.0]*len(axeRadius)
	for i in range(len(lst)-1):   #Заполнение списка со значениями
		#print lst[i].split(" ")[2]
		#print float(lst[i].split(" ")[3])
		lst2[i] = float(lst[i].split(" ")[3])
		aver = aver + float(lst[i].split(" ")[3])
	y=np.array(lst2)
	#print lst2
	aver = aver/len(axeRadius)
	
	return x, y

def main():
	global x
	global y
	global fig
	global aver
	#graph(pathToPointsA)
	#print lst2
	#print y
	fig = plt.figure()   # Создание объекта Figure
	#plt.title('1a TITLE')
	plt.ylabel('Lg(TIC)')
	plt.xlabel('Distance(km)')
	#print np.max(y)    #Максимальное значение в массиве
	print (fig.axes)   # Список текущих областей рисования пуст
	print (type(fig))   # тип объекта Figure
	plt.grid(True)     #Добавление сетки
	a=np.max(graph(pathToPointsA)[1])
	b=np.array([a]*len(graph(pathToPointsA)[1]))
	c=np.array([aver]*len(graph(pathToPointsA)[1]))
	print a
	
	plt.plot(graph(pathToPointsA)[0], np.log(graph(pathToPointsA)[1]),
		 graph(pathToPointsA)[0], np.log(b),
		 graph(pathToPointsA)[0], np.log(c)) 
	plt.text(100.0, np.log(a), 'Max Value = {}'.format(a), fontsize=12)
	plt.text(100.0, np.log(aver), 'Average Value = {}'.format(aver), fontsize=12)
	print (fig.axes)

	# смотри преамбулу
	save(name='pic_G', fmt='jpg')
	save(name='pic_G', fmt='png')

	#plt.show()
	return
	

if __name__ == "__main__":
	sys.exit(main())
#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#Модуль для парсинга xml файла
# Выводит расшифровку функционала по его номеру
import sys
import os
import xml.etree.ElementTree as etree

pathToXlsxForParse="/home/egor/Programs/stat/VVER_TOI_scenario_3/results/0 s/out.xml"

def main():
	loop = True
	while loop == True:
		print "Type number func"
		num = input("            ")
		num = num+7
		lst = []
		et = etree.parse(pathToXlsxForParse)
		root = et.getroot()
		for i, child_of_root in enumerate(root.iter()):
			if i == num:
				print 'Tag: %s' % ( child_of_root.attrib)
				print "New func? Y/n"
				a = raw_input()
				if a=="y" or a =="Y" or a=="д" or a=="Д" or (int(a)<206 and int(a)>=0):
					loop = True
				else:
					loop = False
	return

if __name__ == "__main__":
	sys.exit(main())
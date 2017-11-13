#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import sys
import os

from math import cos,sin,radians,sqrt,fabs,acos,pi,degrees,floor

import xml.etree.ElementTree as etree
from geographiclib.geodesic import Geodesic
from geopy.distance import VincentyDistance
geod = Geodesic.WGS84


def main():
	loop = True
	while loop == True:
		print "Type number func"
		num = input("            ")
		num = num+7
		lst = []
		et = etree.parse('out.xml')
		root = et.getroot()
		for i, child_of_root in enumerate(root.iter()):
			if i == num:
				print 'Tag: %s' % ( child_of_root.attrib)
				print "New func? Y/n"
				a = raw_input()
				if a=="y" or a =="Y" or a=="д" or a=="Д":
					loop = True
				else:
					loop = False
					
				



	
	
	
	
	
	
	return

if __name__ == "__main__":
	sys.exit(main())
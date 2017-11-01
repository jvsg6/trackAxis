#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import sys
import os
import shutil

import xml.etree.ElementTree

import subprocess

#idx = [x+1 for x in range(32)]
idx = 0

class WorkThread:
	def __init__(self,idt,count,mypath):
		self.daemon = True
		self.idt = idt
		self.folder1 = "/calculation/calculation_"+str(int(idt))
		self.count = count
		self.mypath = mypath

	def iter(self, element, tag=None):
		if tag == "*":
			tag = None
		if tag is None or element.tag == tag:
			yield element
		for e in element._children:
			for e in e.iter(tag):
				yield e
		
	def make_sure_path_exists(self,path):
		try: 
			os.makedirs(path)
		except OSError:
			if not os.path.isdir(path):
				raise
	
	def makeInputXML(self,time,basePath):
		print "timeH:",time/3600.0," h, ","timeD:",time/3600.0/24.0," d"
		et = xml.etree.ElementTree.parse(basePath+'/AAK_VVER_TOI_S3.xml')
		root = et.getroot()
		path1 = self.folder1
	
		for source in root.findall('source'):
			sourcePhases = source.find('sourcePhases')
			for sourcePhase in sourcePhases.findall('sourcePhase'):
				sourcePhaseStart = sourcePhase.find('sourcePhaseStart')
				val = float(sourcePhase.find('sourcePhaseStart').text)
				sourcePhaseStart.text = str(val+time)
	

		gridFunction = root.find('gridFunctions')
		for grd in gridFunction.findall('gridFunction'):
			timeEnd = grd.find('timeEnd')
			val = float(grd.find('timeEnd').text)
			timeEnd.text = str(val+time+3600.0*39.5)
	
	
		path = basePath+"/"+path1
		if not os.path.exists(basePath+"/"+path1):
			os.makedirs(basePath+"/"+path1)
		self.make_sure_path_exists(path)
		et.write(path+'/in.xml',encoding="UTF-8")
		return path
	
	def run(self):
		time = 3600.0*2.0*(self.idt-1.0)
		while time <= 31622400:#31622400:#2656800#7862400
			path = self.makeInputXML(time,self.mypath)
			#print self.mypath+"/landuse.asc", path+"/landuse.asc"
			shutil.copyfile(self.mypath+"/landuse.asc", path+"/landuse.asc")
			arguments = ["/home/egor/Programs/release/nostra_build/nostraconsole",path]
			p = subprocess.Popen(["/home/egor/Programs/release/nostra_build/nostraconsole", path], stdout=subprocess.PIPE)
			(output, err) = p.communicate()
			p_status = p.wait()
			print path, "Command output: " + str(p.returncode)
			if p.returncode!= 0:
				print p.returncode, path
				sys.exit()
			os.makedirs(self.mypath+"/results/"+str(int(time))+" s")
			#shutil.copyfile(path+"/in.xml", self.mypath  + "/results/"+str(int(time))+" s/in.xml")
			shutil.copyfile(path+"/out.xml", self.mypath + "/results/"+str(int(time))+" s/out.xml")
			os.remove(path+"/out.xml")
			time = time + 3600.0*2.0*self.count

def main():
	print idx
	mypath=os.path.dirname(os.path.realpath( __file__ ))
	os.chdir(mypath)
	t = WorkThread(idx,64,mypath)
	t.run()
	print "finish!"
	return

if __name__ == "__main__":
	try:
		idx = int(3)
		sys.exit(main())
	except Exception:
		raise
	
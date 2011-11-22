#!/usr/bin/python
#coding:utf-8
#python2.6

import json
import sys
import re
import os
import shutil
import platform
import commands
import time
from compile_config import *

jsKeyP = re.compile('([^"\s]\S+[^"])\s*:')
revFieldP = re.compile('Revision\:\s*(\d+)\s*')
dateFieldP = re.compile('Last Changed Date\:\s*(.+)\n*')

def pickMode(args):
	for name in args:
		Compile(rules[name], name)

class Compile(object):
	def __init__(self, rule, name):
		print 'Compile', name, 60*'+'
		self.target = rule["target"]
		self.source = rule["source"]
		self.name = name
		self.sourcename = os.path.basename(self.source)
		if not self.sourcename:
			self.ext = None
		else:
			self.ext = os.path.splitext(self.sourcename)[1][1:]
		if self.ext == "qzmin":
			self.loadQzmin()
		elif self.ext is None:
			self.recursive = rule.get("recursive")
			self.allowext = rule.get("ext")
			self.moveFiles()
		else:
			self.moveFile(self.source, self.target)
			
	def moveFiles(self):
		if not self.recursive:
			for f in os.listdir(self.source):
				ext = os.path.splitext(f)[1][1:]
				if not self.allowext or self.allowext and ext in self.allowext:
					sourcefile = os.path.join(self.source, f)
					if os.path.isfile(sourcefile):
						self.moveFile(sourcefile, os.path.join(self.target, f))
		else:
			lists = []
			for root, dirs, files in os.walk(self.source, True):
				for f in files:
					ext = os.path.splitext(f)[1][1:]
					if not self.allowext or self.allowext and ext in self.allowext:
						spath = os.path.join(root, f)
						tpath = os.path.join(self.target, os.path.relpath(root, self.source), f)
						lists.append([spath, tpath])
			makeDirs([l[1] for l in lists])
			for l in lists:
				self.moveFile(l[0], l[1])
		
	def moveFile(self, source, target):
		print 'copyfile %s  to %s ' % (source, target)
		filename = os.path.basename(source)
		if filename in revisionUpdatefiles:
			print 'replace', filename
			if os.path.isdir(target):
				target = os.path.join(target, filename)
			open(target, "w").write("".join([line for line in open(source).xreadlines()]).replace(revisionMark, REV))
		else:
			shutil.copy(source, target)
		self.compressor([target])
		
	def loadQzmin(self, format=True):
		print 'load qzmin start', self.name
		f = open(self.source)
		ll = [];
		for l in f.xreadlines():
			if format:
				ll.append(js2json(l))
			else:
				ll.append(l)
		print 'load qzmin finish', self.name
		self.combine(json.loads("".join(ll)))
		
	def combine(self, j):
		print 'combine start', self.name
		projects = j["projects"]
		results = []
		for p in projects:
			target = p["target"]
			files =  p["include"]
			t = []
			combineContent = []
			for f in files:
				fileName = os.path.basename(f)
				filepath = os.path.join(os.path.dirname(self.source), f)
				for line in open(filepath).xreadlines():
					t.append(line);
				if fileName in revisionUpdatefiles:
					print 'replace', fileName
					combineContent.append("".join(t).replace(revisionMark, REV))
				else:
					combineContent.append("".join(t))
				del t[:]
			results.append("".join(combineContent))
		print 'combine finish', self.name
		self.createFiles(results)
		
	def createFiles(self, contents):
		print 'createFiles start', self.name
		results = []
		for c in contents:
			print 'createFiles...'
			open(self.target, "w").write(c)
			results.append(self.target);
		print 'createFiles finish', self.name
		self.compressor(results)
		
	def compressor(self, files):
		if ifCompress:
			for f in files:
				filetype = os.path.splitext(f)[1][1:]
				if filetype in ["js", "css"]:
					print 'compressor start', self.name, "-"*40
					if filetype == "js":
						cmd = 'java -jar %s --%s %s --%s_output_file %s.min' % (googleclosurePath, filetype, f, filetype, f)
					elif filetype == "css":
						cmd = 'java -jar %s %s -o %s.min --charset utf-8' % (yuicompiressorPath, f, f)
					print cmd
					os.system(cmd)
					t = [prefix % DATE]
					for line in open(f+".min").xreadlines():
						t.append(line);
					open(f,"w").write("".join(t))
					os.remove(f+".min")
					print 'compressor finish', self.name, "-"*40
	
def makeDirs(items):
	isCheck = {}
	for v in items:
		path = os.path.dirname(v)
		if not isCheck.get(path):
			mkdir(path)
			isCheck[path] = True
	isCheck.clear()

def js2json(fileline):
	l = jsKeyP.sub(lambda l:'"%s" : ' % l.group(1), fileline)
	return '"'.join(l.split('\''))

def mkdir(path):
	if os.path.exists(path):
		print "Path", path, "exists"
	else:
		os.makedirs(path)
		print "Craete path", path

if __name__ == "__main__":
	print platform.platform()
	if len(sys.argv) > 1:
		argS = (" ").join(sys.argv[1:])
	else:
		argS = ""
	argS = argS.lower()
	
	if "-h" in argS or "-help" in argS or argS is "":
		print '''Options and arguments:
-h             : Help
-produce       : For produce enviroment
-debug         : For debug enviroment
-noup          : Publish without svn up
-nocompress    : Publish without google closure
-norevision    : Publish without version string replacement
For example:
	python compile.py -produce
	python compile.py -debug
	python compile.py -debug -noup -nocompress 
		'''
		sys.exit()

	if "-noup" in argS:
		pass
	else:
		if "Windows" not in platform.platform():
			os.system("svn up")
	
	if "-norevision" in argS:
		REV = DATE = str(time.time())
	else:
		if "Windows" not in platform.platform():
			output = commands.getoutput("svn info")
			REV = revFieldP.search(output).group(1)
			DATE = dateFieldP.search(output).group(1)[:19]
		else:
			REV = DATE = str(time.time())
		
	if "-nocompress" in argS:
		ifCompress = False
	else:
		ifCompress = True
	
	for cmd in sys.argv[1:]:
		if modes.get(cmd):
			print cmd, "mode on ", "-"*60
			items = [v["target"] for k, v in rules.items() if k in modes.get(cmd)]
			makeDirs(items)
			pickMode(modes.get(cmd))
			print 'All done.'
			sys.exit()
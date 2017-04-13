# -*- coding:utf-8 -*-
'''
Created on 2016.12.30

@author: davidpower
'''
import json
import os, sys
from shutil import copyfile
from subprocess import PIPE, Popen

import maya.OpenMaya as om

if not __name__ == '__main__':
	from pymel.core import *


def _load_json(jsonPath):
	""" docstring """
	with open(jsonPath) as jsonFile:
		return json.load(jsonFile)


def _save_json(jsonPath, dictData):
	""" docstring """
	with open(jsonPath, 'w') as jsonFile:
		json.dump(dictData, jsonFile, indent=4)


def _getTextureRes(imgPath):
	""" docstring """
	# make var
	utilWidth = om.MScriptUtil()
	utilWidth.createFromInt(0)
	ptrWidth = utilWidth.asUintPtr()
	utilHeight = om.MScriptUtil()
	utilHeight.createFromInt(0)
	ptrHeight = utilHeight.asUintPtr()
	# get res
	textureFile = om.MImage()
	textureFile.readFromFile ( imgPath )
	textureFile.getSize(ptrWidth, ptrHeight)
	width = om.MScriptUtil.getUint(ptrWidth)
	height = om.MScriptUtil.getUint(ptrHeight)
	return width, height


def _resizeTexture(imgPath, newPath, imgSize, preserveAspectRatio= True):
	""" docstring """
	try:
		textureFile = om.MImage()
		textureFile.readFromFile(imgPath)
		textureFile.resize(imgSize[0], imgSize[1], preserveAspectRatio)
		textureFile.writeToFile(newPath, newPath.split('.')[-1])
	except Exception, e:
		warning('image file resize error: ' + imgPath)
		print e
		error('Failed resize image to: ' + newPath)


def xeroxOutputs(xeroxPath, outputDir, outputSize):
	""" docstring """
	xeroxDict = {}
	for xerox in xeroxPath:
		src_normalMap = xeroxPath[xerox]
		dst_normalMap = outputDir + os.sep + os.path.basename(src_normalMap)
		if outputSize:
			outputSize = int(outputSize)
			_resizeTexture(src_normalMap, dst_normalMap, [outputSize, outputSize])
		else:
			copyfile(src_normalMap, dst_normalMap)
		xeroxDict[xerox] = dst_normalMap.replace('\\', '/')
	print xeroxDict


def taskPackage(textureName, sbsrenderCMD, sbsrenderOutNum, xeroxCMD):
	""" docstring """
	stdDict = {
		'taskName': textureName,
		'sbsrender': {
			'result': {},
			'stdout': '',
			'stderr': ''
		},
		'xerox': {
			'result': {},
			'stdout': '',
			'stderr': ''
		}
	}

	sbsrenderProc = Popen(sbsrenderCMD, shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE)
	sbsrenderStdout, sbsrenderStderr = sbsrenderProc.communicate()
	stdDict['sbsrender']['stdout'] = sbsrenderStdout
	stdDict['sbsrender']['stderr'] = sbsrenderStderr
	if sbsrenderStdout:
		pathCount = 0
		optPathDict = {}
		sbsrenderOutNum = eval(sbsrenderOutNum)
		for line in sbsrenderStdout.split('\r\n'):
			for key in sbsrenderOutNum:
				if line.startswith('* Output "%s" saved to:' % key):
					optPathDict[key] = line.split('"')[-2]
					break
		if len(optPathDict) == len(sbsrenderOutNum):
			stdDict['sbsrender']['result'] = optPathDict
	
	if sbsrenderStderr:
		print stdDict
		return None
	
	xeroxCMD = eval(xeroxCMD)
	xeroxProc = Popen(xeroxCMD, shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE)
	xeroxStdout, xeroxStderr = xeroxProc.communicate()
	stdDict['xerox']['stdout'] = xeroxStdout
	stdDict['xerox']['stderr'] = xeroxStderr
	if xeroxStdout:
		try:
			xeroxDict = eval(xeroxStdout)
		except:
			stdDict['xerox']['stderr'] += '\nxeroxStdout evaluation failed: ' + xeroxStdout
		if isinstance(xeroxDict, dict):
			stdDict['xerox']['result'] = xeroxDict
		else:
			stdDict['xerox']['stderr'] += '\nxeroxStdout is not dict type: ' + xeroxStdout
	print stdDict


class Sbsrender():
	"""
	"""
	def __init__(self):
		""" docstring """
		# static default
		self.settingsRoot = os.environ.get('MAYA_APP_DIR')
		self.configFile = '/'.join([self.settingsRoot, 'sbs2maya_workConfigs.json'])
		self.statusFile = '/'.join([self.settingsRoot, 'sbs2maya_lastStatus.json'])
		self.mayapyexe = os.environ['MAYA_LOCATION'] + '/bin/mayapy.exe'
		## configFile default content
		self.init_workConfig = {
			'sbsrender': 'C:/Program Files/Allegorithmic/Substance Designer 6/sbsrender.exe',
			'sbsarLib': os.path.dirname(__file__).replace('\\', '/') + '/sbsarLib',
			'saveLast': 0,
			}
		## statusFile default content
		self.init_lastStatus = {
			'inputPath': '',
			'outputPath': '',
			'walkSub': 0,
			'udim_uv': 0,
			'sep_name': '',
			'sep_udim': '',
			'img_type': '. ***',
			'hide_udim': 0,
			'selected': 0,
			'buildShd': 1,
			'outFormat': '{ As is }',
			'outSize': '{ As is }'
			}
		# dynamic
		self.workConfig = {}
		self.lastStatus = {}
		self.sbsArgsFile = ''
		self.sbsArgs = {}
		self.imgInputSet = {}
		self.isUDIM = False
		self.sepUDIM = ''
		self.sepTYPE = ''
		# init
		## init configFile
		if not os.path.exists(self.configFile):
			_save_json(self.configFile, self.init_workConfig)
		self.workConfig = _load_json(self.configFile)
		## init statusFile
		if not os.path.exists(self.statusFile):
			_save_json(self.statusFile, self.init_lastStatus)
		self.lastStatus = _load_json(self.statusFile)
	
	def set_sbsWorkConfigs(self, workConfig):
		""" docstring """
		self.workConfig = workConfig
		_save_json(self.configFile, workConfig)

	def set_lastStatus(self, lastStatus):
		""" docstring """
		self.lastStatus = lastStatus
		_save_json(self.statusFile, lastStatus)
	
	def get_sbsArgs(self):
		""" docstring """
		self.sbsArgsFile = self.workConfig['sbsarLib'] + self.sbsArgsFile
		self.sbsArgs = _load_json(self.sbsArgsFile)
		return self.sbsArgs

	def sbsrender_cmd(self, outputDir, textureName, inputDir, inputPath, outputFormat, outputSize):
		""" docstring """
		if outputSize:
			outputSize = str(len(bin(int(outputSize))[3:]))
		else:
			sampleImg = inputPath[self.sbsArgs['input'].keys()[0]]
			outputSize = str(len(bin(int(_getTextureRes(sampleImg)[0]))[3:]))

		graphInput = '' if not self.sbsArgs['graph'] else ('--input-graph "%s" ' % self.sbsArgs['graph'])
		entryInput = ''
		for p in inputPath:
			entryInput += '--set-entry ' + self.sbsArgs['input'][p] + '@"' + inputPath[p] + '" '
		valueInput = ''
		for v in self.sbsArgs['value']:
			if self.sbsArgs['value'][v]:
				valueInput += '--' + v + '@' + self.sbsArgs['value'][v] + ' '
		guideInput = ''
		for g in self.sbsArgs['guide']:
			if self.sbsArgs['guide'][g]:
				guideInput += '--' + g + ' ' + self.sbsArgs['guide'][g] + ' '

		cmd = '"%s" render ' % self.workConfig['sbsrender'] \
			+ '--inputs "%s" ' % self.sbsArgsFile \
			+ graphInput \
			+ entryInput \
			+ valueInput \
			+ '--output-path "%s" ' % outputDir \
			+ '--output-name "%s" ' % (textureName + self.sepTYPE + '{outputNodeName}') \
			+ '--output-format "%s" ' % outputFormat \
			+ guideInput \
			+ '--set-value $outputsize@' + outputSize + ',' + outputSize
		
		if not os.path.exists(outputDir):
			os.mkdir(outputDir)
		return cmd
	

	def xeroxOutputs_cmd(self, xeroxPath, outputDir, outputSize):
		""" docstring """
		return [self.mayapyexe, __file__, 'do_sub_xerox', str(xeroxPath), outputDir, outputSize]


	def task_cmd(self, outputDir, textureName, inputDir, inputPath, xeroxPath, outputFormat, outputSize):
		""" docstring """
		outputDir = (inputDir + os.sep + 'converted') if not outputDir else outputDir
		sbsYieldList = str(self.sbsArgs['yield'].keys())
		sbsrenderCMD = self.sbsrender_cmd(outputDir, textureName, inputDir, inputPath, outputFormat, outputSize)
		xeroxCMD = str(self.xeroxOutputs_cmd(xeroxPath, outputDir, outputSize))
		taskCMD = [self.mayapyexe, __file__, 'do_main_proc', textureName, sbsrenderCMD, sbsYieldList, xeroxCMD]
		return taskCMD


	def buildShadingNetwork(self, optPathDict, itemName):
		""" docstring """
		sbsArgs = self.sbsArgs
		isUDIM = self.isUDIM
		# need use namespace if import ma file ########################
		shadingFile = ''
		importFile(shadingFile, namespace= '__MS_SBS2MAYA_WIP__')

		for channel in optPathDict:
			i = optPathDict[channel][0]
			tex = [difTex, refTex, gloTex, iorTex, norTex][i]
			tex.fileTextureName.set(optPathDict[channel][1])


	def dist(self, outputFormat, outputSize, buildShad, outputDir):
		""" docstring """
		tick = timerX()
		shadedItem = []

		sbsrenderPath = self.workConfig['sbsrender']
		if not os.path.exists(sbsrenderPath):
			error('sbsrender was not found in this path: ' + sbsrenderPath)
			return None
		self.sbsArgsFile = os.path.dirname(self.sbsArgsFile) + os.sep + self.sbsArgs['sbsar']
		if not os.path.exists(self.sbsArgsFile):
			error('sbsar file was not found in this path: ' + self.sbsArgsFile)
			return None
		# build job
		jobPackage = []
		for textureName in self.imgInputSet:
			inputDir = self.imgInputSet[textureName]['root']
			# texturePath
			inputPath = self.imgInputSet[textureName]['input']
			xeroxPath = self.imgInputSet[textureName]['xerox']
			outputFormat = self.imgInputSet[textureName]['ext'] if not outputFormat else outputFormat
			taskCMD = self.task_cmd(outputDir, textureName, inputDir, inputPath, xeroxPath, outputFormat, outputSize)
			jobPackage.append(taskCMD)
		# do job
		parallelLimit = 8
		jobStduot = []
		jobProc = []
		for taskCMD in jobPackage:
			jobProc.append(Popen(taskCMD, shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE))
			if len(jobProc) == parallelLimit:
				while jobProc:
					for task in jobProc:
						if task.poll() is not None:
							taskStdout, taskStderr = task.communicate()
							jobStduot.append(taskStdout)
							jobProc.remove(task)
				jobProc = []
		for result in jobStduot:
			result = eval(result)
			textureName = result['taskName']
			optPathDict = result['sbsrender']['result']
			xeroxDict = result['xerox']['result']
			optPathDict.update(xeroxDict)
			# build shad
			itemName = textureName[:-5] if self.isUDIM else textureName
			if not itemName in shadedItem and buildShad and optPathDict is not None:
				self.buildShadingNetwork(optPathDict, itemName)
			shadedItem.append(itemName)
			
		print 'Job Time: ' + str(timerX(st= tick))


if __name__ == '__main__':
	intent = sys.argv[1]
	if intent == 'do_sub_xerox':
		xeroxOutputs(eval(sys.argv[2]), sys.argv[3], sys.argv[4])
	if intent == 'do_main_proc':
		taskPackage(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])

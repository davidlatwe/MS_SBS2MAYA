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
	utilWidth = om.MScriptUtil()
	utilWidth.createFromInt(0)
	ptrWidth = utilWidth.asUintPtr()
	utilHeight = om.MScriptUtil()
	utilHeight.createFromInt(0)
	ptrHeight = utilHeight.asUintPtr()
	try:
		textureFile = om.MImage()
		textureFile.readFromFile ( imgPath )
		textureFile.getSize(ptrWidth, ptrHeight)
		width = om.MScriptUtil.getUint(ptrWidth)
		height = om.MScriptUtil.getUint(ptrHeight)
		return width, height
	except:
		warning( 'Texture Res error: ' + imgPath )
		return None


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


def xeroxInputs(xeroxPath, outputDir, outputSize):
	""" docstring """
	optPathDict = {}
	for xerox in xeroxPath:
		src_normalMap = xeroxPath[xerox]
		dst_normalMap = outputDir + os.sep + os.path.basename(src_normalMap)
		if outputSize:
			outputSize = int(outputSize)
			_resizeTexture(src_normalMap, dst_normalMap, [outputSize, outputSize])
		else:
			copyfile(src_normalMap, dst_normalMap)
		optPathDict[xerox] = dst_normalMap.replace('\\', '/')
	print optPathDict


class Sbsrender():
	"""
	"""
	def __init__(self):
		""" docstring """
		# static default
		self.settingsRoot = os.environ.get('MAYA_APP_DIR')
		self.configFile = '/'.join([self.settingsRoot, 'sbs2maya_workConfigs.json'])
		self.statusFile = '/'.join([self.settingsRoot, 'sbs2maya_lastStatus.json'])
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
		workConfig = self.workConfig
		sbsrenderPath = workConfig['sbsrender']
		sbsarGraph = self.sbsArgs['graph']
		sbsarFile = os.path.dirname(self.sbsArgsFile) + os.sep + self.sbsArgs['sbsar']
		outputName = textureName + '{outputNodeName}'

		if not os.path.exists(sbsrenderPath):
			error('sbsrender was not found in this path: ' + sbsrenderPath)
			return None
		if not os.path.exists(sbsarFile):
			error('sbsar file was not found in this path: ' + sbsarFile)
			return None

		if outputSize:
			outputSize = str(len(bin(int(outputSize))[3:]))
		else:
			sampleImg = inputPath[self.sbsArgs['input'].keys()[0]]
			inputsize = _getTextureRes(sampleImg)
			if inputsize is None:
				error('Can not query texture file resolution: ' + sampleImg)
				return None
			else:
				outputSize = str(len(bin(int(inputsize[0]))[3:]))

		graphInput = '' if not sbsarGraph else ('--input-graph "%s" ' % sbsarGraph)
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

		cmd = '"%s" render ' % sbsrenderPath \
			+ '--inputs "%s" ' % sbsarFile \
			+ graphInput \
			+ entryInput \
			+ valueInput \
			+ '--output-path "%s" ' % outputDir \
			+ '--output-name "%s" ' % outputName \
			+ '--output-format "%s" ' % outputFormat \
			+ guideInput \
			+ '--set-value $outputsize@' + outputSize + ',' + outputSize
		
		if not os.path.exists(outputDir):
			os.mkdir(outputDir)

		return cmd


	def sbsrender_exec(self, cmd):
		"""
		[var] optPathDict : sbsrender output name and output file path
		"""
		#print cmd
		process = Popen(cmd, shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE)
		convertResult, convertError = process.communicate()
		hasError = None
		print convertResult
		print convertError

		def sbsrender_error(msg):
			"""
			sbsrender.exe output msg Example:

			1) Sucess
			---	* convertResult:
			Results from graph "pkg://Converter" into package "P:/Temp/AK/PBR_SBS2VRay.sbsar":
			* Output "diffuse" saved to: "P:/Temp/AK/converted/aaa_diffuse.png"
			* Output "reflection" saved to: "P:/Temp/AK/converted/aaa_reflection.png"
			* Output "glossiness" saved to: "P:/Temp/AK/converted/aaa_glossiness.png"
			* Output "ior" saved to: "P:/Temp/AK/converted/aaa_ior.png"
			---	* convertError: (None)
			
			2) Failed
			--- * convertResult:
			Results from graph "pkg://Converter" into package "P:/Temp/AK/PBR_SBS2VRay.sbsar":
			---	* convertError:
			Error: Result cannot be saved into: P:/Temp/AK/converted/aaa_diffuse.png
			Error: Result cannot be saved into: P:/Temp/AK/converted/aaa_reflection.png
			Error: Result cannot be saved into: P:/Temp/AK/converted/aaa_glossiness.png
			Error: Result cannot be saved into: P:/Temp/AK/converted/aaa_ior.png

			"""
			print '\n+++'
			print convertResult
			print '---'
			print convertError
			print '+++'
			error(msg)

		if convertResult:
			pathCount = 0
			optPathDict = {}
			for line in convertResult.split('\r\n'):
				for key in self.sbsArgs['yield']:
					if line.startswith('* Output "%s" saved to:' % key):
						optPathDict[key] = line.split('"')[-2]
						break
			if len(optPathDict) == len(self.sbsArgs['yield']):
				return optPathDict
			else:
				# ERROR
				sbsrender_error('Strange error, the number of exported channels was not matched. See scriptEditor for more info')
				return None
		else:
			# ERROR
			sbsrender_error('Fatal Error, sbsrender not working. See scriptEditor for more info')
			return None


	def sbs2maya_convert(self, outputDir, textureName, inputDir, inputPath, xeroxPath, outputFormat, outputSize):
		""" docstring """
		outputDir = (inputDir + os.sep + 'converted') if not outputDir else outputDir
		# Input
		cmd = self.sbsrender_cmd(outputDir, textureName, inputDir, inputPath, outputFormat, outputSize)
		optPathDict = self.sbsrender_exec(cmd)

		# Xerox
		mayapyEXE = os.environ['MAYA_LOCATION'] + '/bin/mayapy.exe'
		process = Popen([mayapyEXE, __file__, str(xeroxPath), outputDir, outputSize], shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE)
		convertResult, convertError = process.communicate()
		hasError = None
		#print convertResult
		#print convertError
		
		optPathDict.update(eval(convertResult))

		return optPathDict


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
		for texture in self.imgInputSet:
			inputDir = self.imgInputSet[texture]['root']
			textureName = texture + self.sepTYPE
			# texturePath
			inputPath = self.imgInputSet[texture]['input']
			xeroxPath = self.imgInputSet[texture]['xerox']
			outputFormat = self.imgInputSet[texture]['ext'] if not outputFormat else outputFormat
			optPathDict = self.sbs2maya_convert(outputDir, textureName, inputDir,
				inputPath, xeroxPath, outputFormat, outputSize)
			itemName = texture[:-5] if self.isUDIM else texture
			
			# check V-Ray is loaded or not
			# if buildShad and not pluginInfo('vrayformaya', q= 1, l= 1):
			# 	try:
			# 		loadPlugin('vrayformaya', qt= 1)
			# 	except Exception, e:
			# 		warning('---------------------')
			# 		print e
			# 		error('Failed to load V-Ray.')
			# 		buildShad = False
			
			# build shad
			if not itemName in shadedItem and buildShad and optPathDict is not None:
				self.buildShadingNetwork(optPathDict, itemName)
			shadedItem.append(itemName)
		print 'Job Time: ' + str(timerX(st= tick))


if __name__ == '__main__':
	xeroxPath = eval(sys.argv[1])
	outputDir = sys.argv[2]
	outputSize = sys.argv[3]
	xeroxInputs(xeroxPath, outputDir, outputSize)

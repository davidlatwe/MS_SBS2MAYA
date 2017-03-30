# -*- coding:utf-8 -*-
'''
Created on 2016.12.30

@author: davidpower
'''
from pymel.core import *
from subprocess import Popen, PIPE
from shutil import copyfile
import mMaya; reload(mMaya)
import mMaya.mShading as mShading; reload(mShading)
import mMaya.mTexture as mTexture; reload(mTexture)
import mMaya.mVRay as mVRay; reload(mVRay)
import json
import os


def load_json(jsonPath):
	"""
	"""
	with open(jsonPath) as jsonFile:
		return json.load(jsonFile)


def save_json(jsonPath, dictData):
	"""
	"""
	with open(jsonPath, 'w') as jsonFile:
		json.dump(dictData, jsonFile, indent=4)


def form_sbsWorkConfigs():
	"""
	"""
	return {
		'sbsrender': 'C:/Program Files/Allegorithmic/Substance Designer 5/sbsrender.exe',
		'sbsarLib': os.path.dirname(__file__).replace('\\', '/') + '/sbsarLib',
		'saveLast': 0,
		}


def form_lastStatus():
	"""
	"""
	return {
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


def get_sbsWorkConfigs():
	"""
	"""
	configFile = 'sbs2maya_workConfigs.json'
	filePath = '/'.join([os.environ.get('MAYA_APP_DIR'), configFile])
	if not os.path.exists(filePath):
		save_json(filePath, form_sbsWorkConfigs())
	return filePath


def get_lastStatus():
	"""
	"""
	settings = 'sbs2maya_lastStatus.json'
	filePath = '/'.join([os.environ.get('MAYA_APP_DIR'), settings])
	if not os.path.exists(filePath):
		save_json(filePath, form_lastStatus())
	return filePath


def sbsrender_cmd(sbsArgsFiles, outputDir, textureName, inputDir, inputPath, outputFormat, outputSize):
	"""
	"""
	configFile = load_json(get_sbsWorkConfigs())
	sbsrenderPath = configFile['sbsrender']
	sbsArgsFiles = configFile['sbsarLib'] + sbsArgsFiles
	sbsArgs = load_json(sbsArgsFiles)
	sbsarGraph = sbsArgs['graph']
	sbsarFile = os.path.dirname(sbsArgsFiles) + os.sep + sbsArgs['sbsar']

	outputDir = (inputDir + os.sep + 'converted') if not outputDir else outputDir
	outputName = textureName + '{outputNodeName}'

	if not os.path.exists(sbsrenderPath):
		warning('sbsrender was not found in this path: ' + sbsrenderPath)
		sbsrenderPath = sbsrenderPath.replace('5', '6')
		if not os.path.exists(sbsrenderPath):
			error('sbsrender was not found in this path: ' + sbsrenderPath)
			return None
	if not os.path.exists(sbsarFile):
		error('sbsar file was not found in this path: ' + sbsarFile)
		return None

	if outputSize:
		outputSize = str(len(bin(int(outputSize))[3:]))
	else:
		sampleImg = inputPath[sbsArgs['input'].keys()[0]]
		inputsize = mTexture.getTextureRes(sampleImg)
		if inputsize is None:
			error('Can not query texture file resolution: ' + sampleImg)
			return None
		else:
			outputSize = str(len(bin(int(inputsize[0]))[3:]))

	graphInput = '' if not sbsarGraph else ('--input-graph "%s" ' % sbsarGraph)
	entryInput = ''
	for p in inputPath:
		entryInput += '--set-entry ' + sbsArgs['input'][p] + '@"' + inputPath[p] + '" '
	valueInput = ''
	for v in sbsArgs['value']:
		if sbsArgs['value'][v]:
			valueInput += '--' + v + '@' + sbsArgs['value'][v] + ' '
	guideInput = ''
	for g in sbsArgs['guide']:
		if sbsArgs['guide'][g]:
			guideInput += '--' + g + ' ' + sbsArgs['guide'][g] + ' '

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

	return cmd, outputDir, sbsArgs


def sbsrender_exec(cmd, outputDir, sbsArgs):
	"""
	"""
	if not os.path.exists(outputDir):
		os.mkdir(outputDir)
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
			for key in sbsArgs['yield']:
				if line.startswith('* Output "%s" saved to:' % key):
					optPathDict[key] = line.split('"')[-2]
					break
		if len(optPathDict) == len(sbsArgs['yield']):
			return optPathDict
		else:
			# ERROR
			sbsrender_error('Strange error, the number of exported channels was not matched. See scriptEditor for more info')
			return None
	else:
		# ERROR
		sbsrender_error('Fatal Error, sbsrender not working. See scriptEditor for more info')
		return None


def sbs2maya_convert(sbsArgsFiles, outputDir, textureName, inputDir, inputPath, xeroxPath, outputFormat, outputSize):
	"""
	"""
	# Input
	cmd, outputDir, sbsArgs = sbsrender_cmd(sbsArgsFiles, outputDir, textureName, inputDir, inputPath, outputFormat, outputSize)
	if cmd and outputDir and sbsArgs:
		optPathDict = sbsrender_exec(cmd, outputDir, sbsArgs)
	else:
		return None

	# Xerox
	for xerox in xeroxPath:
		src_normalMap = xeroxPath[xerox]
		dst_normalMap = outputDir + os.sep + os.path.basename(src_normalMap)
		if outputSize:
			outputSize = int(outputSize)
			mTexture.resizeTexture(src_normalMap, dst_normalMap, [outputSize, outputSize])
		else:
			copyfile(src_normalMap, dst_normalMap)
		optPathDict[xerox] = dst_normalMap.replace('\\', '/')

	return optPathDict, sbsArgs


def buildShadingNetwork(optPathDict, sbsArgs, itemName, isUDIM):
	"""
	"""
	# need use namespace if import ma file ########################
	# need return fileNodes if using python script ################

	# ##############################
	# make indpendent script input: (itemName, isUDIM)
	shadingNodesList = []
	sbsvmtlNodesList = []

	# Build and setup shading network
	mainShd, mainShdSG = mShading.createShader('VRayBlendMtl', itemName + '_SBSvmtl')
	baseShd, noneShdSG = mShading.createShader('VRayMtl', itemName + '_baseMtl', noSG= True)
	specShd, noneShdSG = mShading.createShader('VRayMtl', itemName + '_specMtl', noSG= True)

	sbsvmtlNodesList.extend([mainShd, mainShdSG])
	shadingNodesList.extend([baseShd, specShd])

	baseShd.outColor.connect(mainShd.base_material)
	specShd.outColor.connect(mainShd.coat_material_0)

	mainShd.additive_mode.set(1)
	mainShd.blend_amount_0.set([1, 1, 1])
	baseShd.bumpMapType.set(1)
	specShd.color.set([0, 0, 0])
	specShd.diffuseColorAmount.set(0)
	specShd.brdfType.set(3)
	specShd.lockFresnelIORToRefractionIOR.set(0)
	specShd.bumpMapType.set(1)

	# Create and setup textures nodes
	difTex, difPlc = mShading.createFileTexture(itemName + '_diffuse_file', itemName + '_diffuse_p2d')
	refTex, refPlc = mShading.createFileTexture(itemName + '_reflection_file', itemName + '_reflection_p2d')
	gloTex, gloPlc = mShading.createFileTexture(itemName + '_glossiness_file', itemName + '_glossiness_p2d')
	iorTex, iorPlc = mShading.createFileTexture(itemName + '_ior_file', itemName + '_ior_p2d')
	norTex, norPlc = mShading.createFileTexture(itemName + '_normal_file', itemName + '_normal_p2d')

	for tex in [difTex, refTex, gloTex, iorTex, norTex]:
		tex.filterType.set(0)
		tex.uvTilingMode.set(3 if isUDIM else 0)
		mVRay.setVrayTextureFilter(tex, 1)
		mVRay.setVrayTextureGamma(tex, 2 if tex in [difTex, refTex] else 0)

	difTex.outColor.connect(baseShd.diffuseColor)
	refTex.outColor.connect(specShd.reflectionColor)
	gloTex.outAlpha.connect(specShd.reflectionGlossiness)
	iorTex.outAlpha.connect(specShd.fresnelIOR)
	norTex.outColor.connect(baseShd.bumpMap)
	norTex.outColor.connect(specShd.bumpMap)

	shadingNodesList.extend(
		[difTex, difPlc, refTex, refPlc, gloTex, gloPlc, iorTex, iorPlc, norTex, norPlc])

	mShading.dumpToBin(sbsvmtlNodesList, 'SBS_main')
	mShading.dumpToBin(shadingNodesList, 'SBS_element')
	# make indpendent script output: (fileNodes)
	# ##############################

	for channel in optPathDict:
		i = optPathDict[channel][0]
		tex = [difTex, refTex, gloTex, iorTex, norTex][i]
		tex.fileTextureName.set(optPathDict[channel][1])


def dist(sbsArgsFiles, textureInputSet, outputFormat, outputSize, sepTYPE, isUDIM, buildShad, outputDir):
	"""
	"""
	tick = timerX()
	shadedItem = []
	for texture in textureInputSet:
		inputDir = textureInputSet[texture]['root']
		textureName = texture + sepTYPE
		# texturePath
		inputPath = textureInputSet[texture]['input']
		xeroxPath = textureInputSet[texture]['xerox']
		outputFormat = textureInputSet[texture]['ext'] if not outputFormat else outputFormat
		optPathDict, sbsArgs = sbs2maya_convert(sbsArgsFiles, outputDir, textureName, inputDir,
			inputPath, xeroxPath, outputFormat, outputSize)
		itemName = texture[:-5] if isUDIM else texture
		
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
			buildShadingNetwork(optPathDict, sbsArgs, itemName, isUDIM)
		shadedItem.append(itemName)
	print 'Job Time: ' + str(timerX(st= tick))

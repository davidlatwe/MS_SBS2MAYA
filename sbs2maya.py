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


def sbsrender_cmd(sbsArgsFiles, outputDir, textureName, texturePath, outputFormat, outputSize):
	"""
	"""
	configFile = load_json(get_sbsWorkConfigs())
	sbsrenderPath = configFile['sbsrender']
	sbsarFile = configFile['sbsarLib'] + sbsArgsFiles
	sbsrenderArgs = load_json(sbsarFile)
	sbsarGraph = sbsrenderArgs['graph']

	outputDir = (os.path.dirname(texturePath[0]) + os.sep + 'converted') if not outputDir else outputDir
	outputName = textureName + '{outputNodeName}'
	input_baseColor = texturePath[0]
	input_roughness = texturePath[3]
	input_metallic = texturePath[1]

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
		inputsize = mTexture.getTextureRes(input_baseColor)
		if inputsize is None:
			error('Can not query texture file resolution: ' + input_baseColor)
			return None
		else:
			outputSize = str(len(bin(int(inputsize[0]))[3:]))

	cmd = '"%s" render ' % sbsrenderPath \
		+ '--inputs "%s" ' % sbsarFile \
		+ '--input-graph "%s" ' % sbsarGraph \
		+ '--set-entry input_baseColor@"%s" ' % input_baseColor \
		+ '--set-entry input_roughness@"%s" ' % input_roughness \
		+ '--set-entry input_metallic@"%s" ' % input_metallic \
		+ '--output-path "%s" ' % outputDir \
		+ '--output-name "%s" ' % outputName \
		+ '--output-format "%s" ' % outputFormat \
		+ '--engine "d3d10pc" ' \
		+ '--memory-budget 2048 ' \
		+ '--set-value $outputsize@' + outputSize + ',' + outputSize

	return cmd, outputDir


def sbsrender_exec(cmd, outputDir):
	"""
	"""
	if not os.path.exists(outputDir):
		os.mkdir(outputDir)

	process = Popen(cmd, shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE)
	convertResult, convertError = process.communicate()
	hasError = None

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
		optPathDict = {
			'diffuse' : [0, ''],
			'reflection' : [1, ''],
			'glossiness' : [2, ''],
			'ior' : [3, '']
			}
		optMsgList = convertResult.split('\r\n')
		if len(optMsgList) == 6:
			for channel in optPathDict:
				i = optPathDict[channel][0]
				if optMsgList[i + 1].startswith('* Output "%s" saved to:' % channel):
					optPathDict[channel][1] = optMsgList[i + 1].split('"')[-2]
					pathCount += 1
		else:
			# ERROR
			sbsrender_error('Strange error, sbsrender result message\'s length was not matched. See scriptEditor for more info')
			return None
	else:
		# ERROR
		sbsrender_error('Fatal Error, sbsrender not working. See scriptEditor for more info')
		return None

	if pathCount == 4:
		return optPathDict
	else:
		# ERROR
		sbsrender_error('Strange error, the number of exported channels was not 4. See scriptEditor for more info')
		return None


def sbs2maya_convert(sbsArgsFiles, outputDir, textureName, texturePath, outputFormat, outputSize):
	"""
	"""
	# Convert SBS map
	cmd, outputDir = sbsrender_cmd(sbsArgsFiles, outputDir, textureName, texturePath, outputFormat, outputSize)
	if cmd and outputDir:
		optPathDict = sbsrender_exec(cmd, outputDir)
	else:
		return None

	# Copy normal map
	index = 0
	for i, tp in enumerate(texturePath):
		if 'normal' in os.path.basename(tp).lower():
			index = i
	src_normalMap = texturePath[index]
	dst_normalMap = outputDir + os.sep + os.path.basename(texturePath[index])
	if outputSize:
		outputSize = int(outputSize)
		mTexture.resizeTexture(src_normalMap, dst_normalMap, [outputSize, outputSize])
	else:
		copyfile(src_normalMap, dst_normalMap)
	optPathDict['normal'] = [4, dst_normalMap]

	return optPathDict


def buildShadingNetwork(optPathDict, itemName, isUDIM):
	"""
	"""
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
	
	shadingNodesList.extend(
		[difTex, difPlc, refTex, refPlc, gloTex, gloPlc, iorTex, iorPlc, norTex, norPlc])

	difTex.outColor.connect(baseShd.diffuseColor)
	refTex.outColor.connect(specShd.reflectionColor)
	gloTex.outAlpha.connect(specShd.reflectionGlossiness)
	iorTex.outAlpha.connect(specShd.fresnelIOR)
	norTex.outColor.connect(baseShd.bumpMap)
	norTex.outColor.connect(specShd.bumpMap)

	for channel in optPathDict:
		i = optPathDict[channel][0]
		tex = [difTex, refTex, gloTex, iorTex, norTex][i]
		tex.fileTextureName.set(optPathDict[channel][1])
		tex.filterType.set(0)
		tex.uvTilingMode.set(3 if isUDIM else 0)
		mVRay.setVrayTextureFilter(tex, 1)
		mVRay.setVrayTextureGamma(tex, 2 if tex in [difTex, refTex] else 0)

	mShading.dumpToBin(sbsvmtlNodesList, 'SBS_main')
	mShading.dumpToBin(shadingNodesList, 'SBS_element')


def dist(sbsArgsFiles, textureInputSet, outputFormat, outputSize, sepTYPE, isUDIM, buildShad, outputDir):
	"""
	"""
	tick = timerX()
	shadedItem = []
	for texture in textureInputSet:
		inputDir = textureInputSet[texture][0]
		textureName = texture + sepTYPE
		texturePath = textureInputSet[texture][2:]
		outputFormat = textureInputSet[texture][1] if not outputFormat else outputFormat
		optPathDict = sbs2maya_convert(sbsArgsFiles, outputDir, textureName, texturePath, outputFormat, outputSize)
		itemName = texture[:-5] if isUDIM else texture
		# check V-Ray is loaded or not
		if buildShad and not pluginInfo('vrayformaya', q= 1, l= 1):
			try:
				loadPlugin('vrayformaya', qt= 1)
			except Exception, e:
				warning('---------------------')
				print e
				error('Failed to load V-Ray.')
				buildShad = False
		# build shad
		if not itemName in shadedItem and buildShad and optPathDict is not None:
			buildShadingNetwork(optPathDict, itemName, isUDIM)
		shadedItem.append(itemName)
	print 'Job Time: ' + str(timerX(st= tick))

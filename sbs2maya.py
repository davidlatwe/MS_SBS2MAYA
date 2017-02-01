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
import mMaya.mVRay as mVRay; reload(mVRay)
import os


sbsrenderPath = 'C:\\Program Files\\Allegorithmic\\Substance Designer 5\\sbsrender.exe'
#sbsrenderPath = 'C:\\Program Files\\Allegorithmic\\Substance Designer\\5\\bin64\\sbsrender.exe'
sbsarFile = 'T:\\Script\\Maya\\tools\\MS_SBS2MAYA\\sbsarLib\\PBR_SBS2VRay.sbsar'
sbsarGraph = 'Converter'


def sbsrender_cmd(outputDir, textureName, texturePath, outputFormat):
	"""
	"""
	outputDir = '{inputPath}' + os.sep + 'converted' if not outputDir else outputDir
	outputName = textureName + '{outputNodeName}'
	input_baseColor = texturePath[0]
	input_roughness = texturePath[3]
	input_metallic = texturePath[1]

	if not os.path.exists(sbsrenderPath):
		error('sbsrender was not found in this path: ' + sbsrenderPath)
		return None
	if not os.path.exists(sbsarFile):
		error('sbsar file was not found in this path: ' + sbsarFile)
		return None

	cmd = '"%s" render ' % sbsrenderPath \
		+ '--inputs "%s" ' % sbsarFile \
		+ '--input-graph "%s" ' % sbsarGraph \
		+ '--set-entry input_baseColor@"%s" ' % input_baseColor \
		+ '--set-entry input_roughness@"%s" ' % input_roughness \
		+ '--set-entry input_metallic@"%s" ' % input_metallic \
		+ '--output-path "%s" ' % outputDir \
		+ '--output-name "%s" ' % outputName \
		+ '--output-format "%s" ' % outputFormat

	return cmd, outputDir


def sbsrender_exec(cmd, outputDir):
	"""
	"""
	if not os.path.exists(outputDir):
		os.mkdir(outputDir)

	process = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
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


def sbs2maya_convert(outputDir, textureName, texturePath, outputFormat):
	"""
	"""
	# Convert SBS map
	cmd, outputDir = sbsrender_cmd(outputDir, textureName, texturePath, outputFormat)
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


def dist(textureInputSet, outputFormat, sepTYPE, isUDIM, buildShad, outputDir):
	"""
	"""
	shadedItem = []
	for texture in textureInputSet:
		inputDir = textureInputSet[texture][0]
		textureName = texture + sepTYPE
		texturePath = textureInputSet[texture][2:]
		outputFormat = textureInputSet[texture][1] if not outputFormat else outputFormat
		optPathDict = sbs2maya_convert(outputDir, textureName, texturePath, outputFormat)
		itemName = texture[:-5] if isUDIM else texture
		if not itemName in shadedItem and buildShad:
			buildShadingNetwork(optPathDict, itemName, isUDIM)
		shadedItem.append(itemName)

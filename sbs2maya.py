
from pymel.core import *
from subprocess import Popen, PIPE
from shutil import copyfile
import os
import mQtGui.muiSwitchBox as mqsb; reload(mqsb)
import mQtGui.mGetQt as mqt; reload(mqt)

inputDir = 'P:\\Temp\\AK'
textureName = ''
outputFormat= 'png'


def sbsrender_cmd(inputDir, textureName, outputFormat):
	"""
	"""
	outputDir = inputDir + os.sep + 'converted'
	outputName = textureName + '_{outputNodeName}'
	input_baseColor = inputDir + os.sep + textureName + '.albedo.' + outputFormat
	input_roughness = inputDir + os.sep + textureName + '.roughness.' + outputFormat
	input_metallic = inputDir + os.sep + textureName + '.metalness.' + outputFormat

	sbsrenderPath = 'C:\\Program Files\\Allegorithmic\\Substance Designer\\5\\bin64\\sbsrender.exe'
	sbsarFile = 'P:\\Temp\\AK\\PBR_SBS2VRay.sbsar'
	sbsarGraph = 'Converter'

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


def sbs2maya_core(inputDir, textureName, outputFormat, isUDIM):
	"""
	"""
	# Convert SBS map
	cmd, outputDir = sbsrender_cmd(inputDir, textureName, outputFormat)
	if cmd and outputDir:
		optPathDict = sbsrender_exec(cmd, outputDir)
	else:
		return None

	# Copy normal map
	src_normalMap = inputDir + textureName + ''
	dst_normalMap = outputDir + os.sep + textureName + ''
	copyfile(src_normalMap, dst_normalMap)
	optPathDict['normal'] = [4, dst_normalMap]

	shadingNodesList = []
	sbsvmtlNodesList = []

	# Build and setup shading network
	mainShd, mainShdSG = createShader('VRayBlendMtl', textureName + '_SBSvmtl')
	baseShd, noneShdSG = createShader('VRayMtl', textureName + '_baseMtl', noSG= True)
	specShd, noneShdSG = createShader('VRayMtl', textureName + '_specMtl', noSG= True)

	sbsvmtlNodesList.append(mainShd, mainShdSG)
	shadingNodesList.append(baseShd, specShd)

	baseShd.outColor.connect(mainShd.base_material)
	specShd.outColor.connect(mainShd.coat_material_0)

	mainShd.additive_mode.set(1)
	mainShd.blend_amount_0.set([1, 1, 1])
	baseShd.color.set([0, 0, 0])
	baseShd.bumpMapType.set(1)
	specShd.brdfType.set(3)
	specShd.lockFresnelIORToRefractionIOR.set(0)
	specShd.bumpMapType.set(1)

	# Create and setup textures nodes
	difTex, difPlc = createFileTexture(textureNode_name, place2dNode_name)
	refTex, refPlc = createFileTexture(textureNode_name, place2dNode_name)
	gloTex, gloPlc = createFileTexture(textureNode_name, place2dNode_name)
	iorTex, iorPlc = createFileTexture(textureNode_name, place2dNode_name)
	norTex, norPlc = createFileTexture(textureNode_name, place2dNode_name)
	
	shadingNodesList.append(
		difTex, difPlc,	refTex, refPlc,	gloTex, gloPlc, iorTex, iorPlc, norTex, norPlc)

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
		setVrayTextureFilter(tex, 1)
		setVrayTextureGamma(tex, 2 if tex in [difTex, refTex] else 0)

	dumpToBin(sbsvmtlNodesList, 'SBS_main')
	dumpToBin(shadingNodesList, 'SBS_element')


def batch():
	pass


def sbs2maya_ui():
	
	windowName = 'ms_sbs2maya_mainUI'
	windowWidth = 250

	if window(windowName, q= 1, ex= 1):
		deleteUI(windowName)

	window(windowName, t= 'SBS 2 MAYA', s= 0, mxb= 0, mnb= 0)
	main_column = columnLayout(adj= 1, cal= 'left')
	
	#main_form = formLayout()

	bannerArea = columnLayout(adj= 1)
	bannerTxt = text(l= 'SBS2MAYA', w= windowWidth)
	QBannerTxt = mqt.convert(bannerTxt)
	QBannerTxt.setStyleSheet('QObject {font: bold 42px; color: #222222;}')
	setParent('..')

	text('  - Texture Folder Path')

	rowLayout(nc= 2, adj= 1)
	textField()
	icBtn_textF_choose = iconTextButton(i= 'fileOpen.png', w= 20, h= 20)
	setParent('..')
	
	rowLayout(nc= 3, adj= 1, cl2= ['left', 'left'])
	
	columnLayout()
	text(' + Walk Subfolders', h= 20)
	cmA= columnLayout()
	walk_mqsb = mqsb.SwitchBox(onl= 'WALK', ofl= 'NO', w= 120, h= 25, v= False, p= cmA)
	setParent('..')
	setParent('..')
	
	columnLayout()
	text(' + UDIM UV Tilling', h= 20)
	cmB= columnLayout()
	udim_mqsb = mqsb.SwitchBox(onl= 'UDIM', ofl= 'NO', w= 120, h= 25, v= False, p= cmB)
	setParent('..')
	setParent('..')
	text('', w= 10)
	setParent('..')
	
	text(' + Input Filename Pattern', h= 20)
	rowLayout(nc= 7)
	button('NAME', h= 20, w= 42)
	button('_', w= 16, h= 20)
	button('UDIM', h= 20, w= 42)
	button('.', w= 16, h= 20)
	button('TYPE', h= 20, w= 42)
	button('.', w= 16, h= 20)
	optionMenu(h= 20)
	menuItem('png')
	setParent('..')
	# file name format objName._udim._type.format
	# detected (good to go) obj list

	window(windowName, e= 1, w= windowWidth, h= 400)
	showWindow(windowName)
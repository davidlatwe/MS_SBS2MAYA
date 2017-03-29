# -*- coding:utf-8 -*-
'''
Created on 2016.12.30

@author: davidpower
'''
from pymel.core import *
from functools import partial
import os
import mQtGui; reload(mQtGui)
import mQtGui.muiSwitchBox as mqsb; reload(mqsb)
import mQtGui.mGetQt as mqt; reload(mqt)
import sbs2maya; reload(sbs2maya)


ext_list = ['.png', '.jpg', '.tif', '.tga', '.exr', '.bmp']
siz_list = ['64', '128', '256', '512', '1024', '2048', '4096', '8192']

windowTitle = 'SBS 2 MAYA - v1.2'
windowSettings = ' - Settings'
windowName = 'ms_sbs2maya_mainUI'
column_main = windowName + '_main_column'
column_workArea = windowName + '_workArea_column'
column_settings = windowName + '_settings_column'
windowWidth = 320
height_workArea = 615
height_settings = 226
if about(li= True):
	height_offset = 1
if about(win= True):
	height_offset = 3


def ui_settings():
	"""
	"""
	configFile = sbs2maya.load_json(sbs2maya.get_sbsWorkConfigs())
	if columnLayout(column_settings, q= 1, ex= 1):
		deleteUI(column_settings)
	columnLayout(column_settings, adj= 1, cal= 'left', p= column_main)

	text(l= '  - Sbsrender App Path')
	rowLayout(nc= 1, adj= 1)
	renP_text = textField(text= configFile['sbsrender'])
	setParent('..')

	text(l= '', h= 2)

	text(l= '  - Converter Lib Path')
	rowLayout(nc= 1, adj= 1)
	sLib_text = textField(text= configFile['sbsarLib'])
	setParent('..')

	text(l= '', h= 2)

	text(l= '  - Save Last UI Settings')
	text(l= '', h= 2)
	rowLayout(nc= 2, adj= 2)
	text(l= '', w= 1)
	stA= columnLayout()
	save_mqsb = mqsb.SwitchBox(onl= 'YES', ofl= 'NO', w= 130, h= 25, v= configFile['saveLast'], p= stA)
	setParent('..')
	setParent('..')

	text(l= '', h= 12)
	rowLayout(nc= 3, adj= 2)
	text(l= '', w= 1)
	sFig_btn = button(l= 'Save Configs', h= 40)
	text(l= '', w= 1)
	setParent('..')

	setParent('..')

	def saveConfigs(*args):
		configFile = sbs2maya.load_json(sbs2maya.get_sbsWorkConfigs())
		configFile['sbsrender'] = renP_text.getText()
		configFile['sbsarLib'] = sLib_text.getText()
		configFile['saveLast'] = save_mqsb.isChecked()
		sbs2maya.save_json(sbs2maya.get_sbsWorkConfigs(), configFile)

	sFig_btn.setCommand(saveConfigs)


def ui_main():
	"""
	"""
	if window(windowName, q= 1, ex= 1):
		deleteUI(windowName)

	window(windowName, t= windowTitle, s= 0, mxb= 0, mnb= 0)
	columnLayout(column_main, adj= 1)
	
	#main_form = formLayout()

	rowLayout(nc= 2, adj= 1, w= windowWidth)
	bannerArea = columnLayout(adj= 1, h= 40)
	bannerTxt = text(l= '  sbsrender 2 maya')
	QBannerTxt = mqt.convert(bannerTxt)
	QBannerTxt.setStyleSheet('QObject {font: bold 26px; color: #222222;}')
	setParent('..')
	configBtn = iconTextButton(i= 'gear.png', h= 40)
	setParent('..')
	
	text(l= '', h= 4)
	separator()
	text(l= '', h= 4)
	
	columnLayout(column_workArea, adj= 1, cal= 'left')

	text(l= ' - Select Converter', al= 'left', h= 20)

	rowLayout(nc= 2, adj= 1)
	sbsarFile_menu = optionMenu(h= 21)
	mcBtn_textF_choose = iconTextButton(i= 'editRenderPass.png', w= 20, h= 20)
	#text(l= '', w= 3)
	setParent('..')

	text(l= '', h= 2)

	text(l= '  - Texture Folder Path')

	rowLayout(nc= 2, adj= 1)
	inputDir_textF = textField(text= workspace(q= 1, rd= 1) + workspace('sourceImages', q= 1, fre= 1))
	icBtn_textF_choose = iconTextButton(i= 'fileOpen.png', w= 20, h= 20)
	setParent('..')

	text(l= '', h= 2)

	text(l= '  - Output Folder Path')

	rowLayout(nc= 2, adj= 1)
	outputDir_textF = textField(text= '')
	ocBtn_textF_choose = iconTextButton(i= 'fileOpen.png', w= 20, h= 20)
	setParent('..')

	rowLayout(nc= 3, adj= 1, cl2= ['left', 'left'])
	
	columnLayout()
	text(l= ' + Walk Subfolders', h= 20)
	cmA= columnLayout()
	walk_mqsb = mqsb.SwitchBox(onl= 'WALK', ofl= 'NO', w= 130, h= 25, v= False, p= cmA)
	setParent('..')
	setParent('..')
	
	columnLayout()
	text(l= ' + UDIM UV Tilling', h= 20)
	cmB= columnLayout()
	udim_mqsb = mqsb.SwitchBox(onl= 'UDIM', ofl= 'NO', w= 130, h= 25, v= False, p= cmB)
	setParent('..')
	setParent('..')
	text(l= '', w= 1)
	setParent('..')

	# file name format objName._udim._type.format
	text(l= ' + Input Filename Pattern ( Press to change separator. )', h= 20)
	row_Pattern = rowLayout(nc= 8, adj= 1, cw= [3, 1])
	text(l= '', w= 1)
	button(l= 'NAME', w= 50, h= 18, en= 0)
	rowLayout(nc= 5)
	text(l= '', w= 1)
	sepUDIM_btn = button(l= '_', w= 16, h= 18)
	text(l= '', w= 1)
	tagUDIM_txt = button(l= 'UDIM', h= 18, w= 50, en= 0)
	text(l= '', w= 1)
	setParent('..')
	sepTYPE_btn = button(l= '_', w= 16, h= 18)
	text(l= '', w= 1)
	button(l= 'TYPE', w= 44, h= 18, en= 0)
	rowLayout(nc= 1)
	inputExt_menu = optionMenu(h= 21)
	menuItem('. ***')
	for ext in ext_list:
		menuItem(ext)
	setParent('..')
	text(l= '', w= 10)
	setParent('..')
	
	text(l= '', h= 6)
	# detected (good to go) obj list
	hide_row = rowLayout(nc= 3, adj= 1)
	text(l= ' + Hide UDIM Texture', al= 'left', h= 20)
	columnLayout()
	cmC= columnLayout()
	hide_mqsb = mqsb.SwitchBox(onl= 'Yes, Hide', ofl= 'No, Show All', w= 160, h= 20, v= False, p= cmC)
	setParent('..')
	setParent('..')
	text(l= '', w= 1)
	setParent('..')

	text(l= '', h= 2)
	rowLayout(nc= 3, adj= 2)
	text(l= '', w= 1)
	checkTexture_btn = button(l= 'Resolve Input Image File Path', h= 30)
	text(l= '', w= 1)
	setParent('..')
	
	text(l= '', h= 2)
	
	rowLayout(nc= 3, adj= 2)
	text(l= '', w= 1)
	checkResult_txsc = textScrollList(ams= 1, h= 120)
	text(l= '', w= 1)
	setParent('..')
	
	# GO
	rowLayout(nc= 3, adj= 1, h= 28)
	text(l= '  - Convert Selected Only', al= 'left', h= 20)
	columnLayout()
	cmD= columnLayout()
	selt_mqsb = mqsb.SwitchBox(onl= 'Yes, Selected', ofl= 'No, All', w= 160, h= 22, v= False, p= cmD)
	setParent('..')
	setParent('..')
	text(l= '', w= 1)
	setParent('..')

	rowLayout(nc= 3, adj= 1, h= 28)
	text(l= '  - Build Shading Networks', al= 'left', h= 20)
	columnLayout()
	cmE= columnLayout()
	shad_mqsb = mqsb.SwitchBox(onl= 'Yes', ofl= 'No', w= 160, h= 22, v= True, p= cmE)
	setParent('..')
	setParent('..')
	text(l= '', w= 1)
	setParent('..')

	rowLayout(nc= 3, adj= 1, h= 28)
	text(l= ' + Output Texture File Format', al= 'left', h= 20)
	outputExt_menu = optionMenu(h= 21)
	menuItem('{ As is }')
	for ext in ext_list:
		menuItem(ext)
	text(l= '', w= 3)
	setParent('..')

	rowLayout(nc= 3, adj= 1, h= 28)
	text(l= ' + Output Texture Size', al= 'left', h= 20)
	outputSiz_menu = optionMenu(h= 21)
	menuItem('{ As is }')
	for siz in siz_list:
		menuItem(siz)
	text(l= '', w= 3)
	setParent('..')
	
	text(l= '', h= 6)
	rowLayout(nc= 3, adj= 2)
	text(l= '', w= 1)
	sendMission_btn = button(l= 'Start Process', h= 40)
	text(l= '', w= 1)
	setParent('..')
	text(l= '', h= 2)

	setParent('..')
	


	# #################################################################################################
	# ui commands
	#
	def switchSettingsUI():
		ui_settings()
		mainVis = columnLayout(column_workArea, q= 1, vis= True)
		columnLayout(column_workArea, e= 1, vis= not mainVis)
		columnLayout(column_settings, e= 1, vis= mainVis)
		window(windowName, e= 1,
			t= windowTitle + (windowSettings if mainVis else ''),
			h= height_settings if mainVis else (height_workArea + height_offset))

	configBtn.setCommand(switchSettingsUI)


	def listSbsrenderArgsFiles(*args):
		configFile = sbs2maya.load_json(sbs2maya.get_sbsWorkConfigs())
		sbsarFile_menu.clear()
		for root, dirs, files in os.walk(configFile['sbsarLib']):
			for f in files:
				if f.endswith(".json"):
					fileName = os.path.join(root, f).split(configFile['sbsarLib'])[-1]
					menuItem(fileName, p= sbsarFile_menu)

	sbsarFile_menu.beforeShowPopup(listSbsrenderArgsFiles)
	listSbsrenderArgsFiles()


	def openTextureFolder(*args):
		textureDir = inputDir_textF.getText()
		if not textureDir or not os.path.exists(textureDir):
			textureDir = workspace(q= 1, rd= 1) + workspace('sourceImages', q= 1, fre= 1)
		if os.path.exists(textureDir):
			result = fileDialog2(cap= 'Select Texture Folder', fm= 3, okc= 'Select', dir= textureDir)
			if result:
				inputDir_textF.setText(result[0])

	icBtn_textF_choose.setCommand(partial(openTextureFolder))


	def openOutputFolder(*args):
		textureDir = inputDir_textF.getText()
		if not textureDir or not os.path.exists(textureDir):
			textureDir = workspace(q= 1, rd= 1) + workspace('sourceImages', q= 1, fre= 1)
		if os.path.exists(textureDir):
			result = fileDialog2(cap= 'Select Output Folder', fm= 3, okc= 'Select', dir= textureDir)
			if result:
				outputDir_textF.setText(result[0])

	ocBtn_textF_choose.setCommand(partial(openOutputFolder))


	def udim_mqsb_switch(status, *args):
		if status:
			row_Pattern.columnWidth([3, 78])
			hide_row.setEnable(0)
		else:
			row_Pattern.columnWidth([3, 1])
			hide_row.setEnable(1)

	udim_mqsb.onCmd = partial(udim_mqsb_switch, 1)
	udim_mqsb.offCmd = partial(udim_mqsb_switch, 0)


	def sepBtn_Label(btn, *args):
		name_sep = ['.', '_']
		i = name_sep.index(btn.getLabel())
		btn.setLabel(name_sep[(i + 1) % 2])

	sepUDIM_btn.setCommand(partial(sepBtn_Label, sepUDIM_btn))
	sepTYPE_btn.setCommand(partial(sepBtn_Label, sepTYPE_btn))


	global textureInputSet
	textureInputSet = {}
	def checkTextureFile(*args):
		configFile = sbs2maya.load_json(sbs2maya.get_sbsWorkConfigs())
		sbsarPath = configFile['sbsarLib'] + sbsarFile_menu.getValue()
		sbaArgs = sbs2maya.load_json(sbsarPath)
		inputType = sbaArgs['input'].keys()
		xeroxType = sbaArgs['xerox'].keys()

		inputDir = os.path.abspath(inputDir_textF.getText())
		dirWalk = walk_mqsb.isChecked()
		isUDIM = udim_mqsb.isChecked()
		extType = inputExt_menu.getValue()
		extType = '' if extType == '. ***' else extType
		sepUDIM = sepUDIM_btn.getLabel()
		sepTYPE = sepTYPE_btn.getLabel()

		checkResult_txsc.removeAll()
		global textureInputSet
		textureInputSet = {}

		# grab all files
		fileList = []
		if dirWalk:
			for root, dirs, files in os.walk(inputDir):
				for f in files:
					if not extType or os.path.splitext(f)[-1] == extType:
						fileList.append(os.path.join(root, f))
		else:
			for f in os.listdir(inputDir):
				f = os.path.join(inputDir, f)
				if os.path.isfile(f):
					if not extType or os.path.splitext(f)[-1] == extType:
						fileList.append(f)

		# filter out wont be matched
		infoBox = {}
		infoBox_init = {
			'root': '',
			'ext': '',
			'input': {},
			'xerox': {}
			}
		itemName_currentMatch = ''
		for f in fileList:
			fileName = os.path.basename(os.path.splitext(f)[0])
			typeName = fileName.split(sepTYPE)[-1].lower()
			itemName = fileName[:-(len(typeName) + 1)]
			udimCode = itemName.split(sepUDIM)[-1] if isUDIM else ''
			if not isUDIM and hide_mqsb.isChecked() and len(itemName) > 5 and itemName[-5] in ['_', '.']:
				continue
			if infoBox and not itemName_currentMatch and not itemName == itemName_currentMatch:
				if len(infoBox['input']) < len(inputType) or len(infoBox['xerox']) < len(xeroxType):
					infoBox = {}
			if typeName in inputType or typeName in xeroxType:
				if udimCode.isdigit() if isUDIM else True:
					if not infoBox:
						infoBox = infoBox_init
						infoBox['root'] = os.path.dirname(f)
						infoBox['ext'] = os.path.splitext(f)[-1][1:]
						itemName_currentMatch = itemName
					if infoBox['root'] and infoBox['ext']:
						if typeName in inputType:
							infoBox['input'][typeName] = f
						if typeName in xeroxType:
							infoBox['xerox'][typeName] = f
						print infoBox
			if len(infoBox['input']) == len(inputType) and len(infoBox['xerox']) == len(xeroxType):
				textureInputSet[itemName] = infoBox
				infoBox = {}

		for item in textureInputSet:
			checkResult_txsc.append(item)

	checkTexture_btn.setCommand(partial(checkTextureFile))


	def scrollList_deselectAll(*args):
		checkResult_txsc.deselectAll()
	def scrollList_doubleClick(*args):
		global textureInputSet
		item = checkResult_txsc.getSelectItem()
		if item:
			print '-'*10
			print '***  ' + item[0]
			info = textureInputSet[item[0]]
			print 'root: 	' + info['root']
			print 'ext: 	' + info['ext']
			print 'input:'
			for i in info['input']:
				print '		[' + i + ']: ' + info['input'][i]
			print 'xerox:'
			for i in info['xerox']:
				print '		[' + i + ']: ' + info['xerox'][i]
			warning('SBS2MAYA : Info printed out, Please see scriptEditor.')

	checkResult_txsc.deleteKeyCommand(partial(scrollList_deselectAll))
	checkResult_txsc.doubleClickCommand(partial(scrollList_doubleClick))


	def sendMission(*args):
		sbsArgsFiles = sbsarFile_menu.getValue()
		outputFormat = outputExt_menu.getValue()
		outputFormat = '' if outputFormat == '{ As is }' else outputFormat
		outputSize = outputSiz_menu.getValue()
		outputSize = '' if outputSize == '{ As is }' else outputSize
		isUDIM = udim_mqsb.isChecked()
		sepTYPE = sepTYPE_btn.getLabel()
		buildShad = shad_mqsb.isChecked()
		outputDirTF = outputDir_textF.getText()
		outputDir = os.path.abspath(outputDirTF) if outputDirTF else ''
		if selt_mqsb.isChecked():
			selectedItem = checkResult_txsc.getSelectItem()
			allItems = checkResult_txsc.getAllItems()
			for item in allItems:
				if not item in selectedItem:
					textureInputSet.pop(item, None)
		if textureInputSet:
			sbs2maya.dist(sbsArgsFiles, textureInputSet, outputFormat, outputSize, sepTYPE, isUDIM,
				buildShad, outputDir)
		else:
			warning('SBS2MAYA : Empty input.')

	sendMission_btn.setCommand(partial(sendMission))

	def saveLastStatus(*args):
		configFile = sbs2maya.load_json(sbs2maya.get_sbsWorkConfigs())
		if configFile['saveLast']:
			settings = sbs2maya.load_json(sbs2maya.get_lastStatus())
			settings['inputPath'] = inputDir_textF.getText()
			settings['outputPath'] = outputDir_textF.getText()
			settings['walkSub'] = walk_mqsb.isChecked()
			settings['udim_uv'] = udim_mqsb.isChecked()
			settings['sep_name'] = sepUDIM_btn.getLabel()
			settings['sep_udim'] = sepTYPE_btn.getLabel()
			settings['img_type'] = inputExt_menu.getValue()
			settings['hide_udim'] = hide_mqsb.isChecked()
			settings['selected'] = selt_mqsb.isChecked()
			settings['buildShd'] = shad_mqsb.isChecked()
			settings['outFormat'] = outputExt_menu.getValue()
			settings['outSize'] = outputSiz_menu.getValue()
			sbs2maya.save_json(sbs2maya.get_lastStatus(), settings)

	window(windowName, e= 1, w= windowWidth, h= height_workArea, cc= saveLastStatus)

	def restoreLastStatus():
		configFile = sbs2maya.load_json(sbs2maya.get_sbsWorkConfigs())
		if configFile['saveLast']:
			settings = sbs2maya.load_json(sbs2maya.get_lastStatus())
			inputDir_textF.setText(settings['inputPath'])
			outputDir_textF.setText(settings['outputPath'])
			walk_mqsb.setChecked(settings['walkSub'])
			udim_mqsb.setChecked(settings['udim_uv'])
			sepUDIM_btn.setLabel(settings['sep_name'])
			sepTYPE_btn.setLabel(settings['sep_udim'])
			inputExt_menu.setValue(settings['img_type'])
			hide_mqsb.setChecked(settings['hide_udim'])
			selt_mqsb.setChecked(settings['selected'])
			shad_mqsb.setChecked(settings['buildShd'])
			outputExt_menu.setValue(settings['outFormat'])
			outputSiz_menu.setValue(settings['outSize'])
	
	restoreLastStatus()

	showWindow(windowName)
# -*- coding:utf-8 -*-
'''
Created on 2016.12.30

@author: davidpower
'''
import os
from functools import partial

from pymel.core import *

import mQtGui; reload(mQtGui)
import mQtGui.muiSwitchBox as mqsb; reload(mqsb)
import mQtGui.mGetQt as mqt; reload(mqt)
import sbs2maya; reload(sbs2maya)

sbsrender = sbs2maya.Sbsrender()


windowTitle = 'SBS 2 MAYA - v1.8b'
windowSettings = ' - Settings'
windowName = 'ms_sbs2maya_mainUI'
column_main = windowName + '_main_column'
column_workArea = windowName + '_workArea_column'
column_settings = windowName + '_settings_column'
windowWidth = 320
height_workArea = 628
height_settings = 229
if about(li= True):
	height_offset = 1
if about(win= True):
	height_offset = 3


def ui_settings():
	"""
	"""
	workConfig = sbsrender.workConfig
	if columnLayout(column_settings, q= 1, ex= 1):
		deleteUI(column_settings)
	columnLayout(column_settings, adj= 1, cal= 'left', p= column_main)

	text(l= '  - Sbsrender App Path')
	rowLayout(nc= 1, adj= 1)
	renP_text = textField(text= workConfig['sbsrender'])
	setParent('..')

	text(l= '', h= 2)

	text(l= '  - Converter Lib Path')
	rowLayout(nc= 1, adj= 1)
	sLib_text = textField(text= workConfig['sbsarLib'])
	setParent('..')

	text(l= '', h= 2)

	text(l= '  - Save Last UI Settings')
	text(l= '', h= 2)
	rowLayout(nc= 2, adj= 2)
	text(l= '', w= 1)
	stA= columnLayout()
	save_mqsb = mqsb.SwitchBox(onl= 'YES', ofl= 'NO', w= 130, h= 25, v= workConfig['saveLast'], p= stA)
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
		workConfig = sbsrender.workConfig
		workConfig['sbsrender'] = renP_text.getText()
		workConfig['sbsarLib'] = sLib_text.getText()
		workConfig['saveLast'] = save_mqsb.isChecked()
		sbsrender.set_sbsWorkConfigs(workConfig)
		warning('[SBS2MAYA] : Config saved.')

	sFig_btn.setCommand(saveConfigs)


def ui_main():
	"""
	"""
	if window(windowName, q= 1, ex= 1):
		deleteUI(windowName)

	window(windowName, t= windowTitle, s= 0, mxb= 0, mnb= 0)
	columnLayout(column_main, adj= 1)

	rowLayout(nc= 2, adj= 1, w= windowWidth)
	bannerArea = columnLayout(adj= 1, h= 40)
	bannerTxt = text(l= '  sbsrender 2 maya')
	QBannerTxt = mqt.convert(bannerTxt)
	QBannerTxt.setStyleSheet('QObject {font: bold 26px; color: #222222;}')
	setParent('..')
	columnLayout(adj= 1, w= 20)
	configBtn = iconTextButton(i= 'nodeGrapherGear.svg', h= 18, w= 18)
	text(l= '', h= 20)
	setParent('..')
	setParent('..')
	
	text(l= '', h= 4)
	separator()
	text(l= '', h= 4)
	
	columnLayout(column_workArea, adj= 1, cal= 'left')

	text(l= ' - Select Converter', al= 'left', h= 20)

	rowLayout(nc= 2, adj= 1)
	sbsarFile_menu = optionMenu(h= 21)
	mcBtn_textF_choose = iconTextButton(i= 'editRenderPass.png', w= 20, h= 20)
	setParent('..')

	text(l= '', h= 2)

	text(l= '  - Texture Folder Path')

	rowLayout(nc= 2, adj= 1)
	inputDir_textF = textField(text= workspace(q= 1, rd= 1) + workspace('sourceImages', q= 1, fre= 1))
	icBtn_textF_choose = iconTextButton(i= 'fileOpen.png', w= 20, h= 20)
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
	for ext in sbsrender.imgFormat:
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
	for ext in sbsrender.imgFormat:
		menuItem(ext)
	text(l= '', w= 3)
	setParent('..')

	rowLayout(nc= 3, adj= 1, h= 28)
	text(l= ' + Output Texture Size', al= 'left', h= 20)
	outputSiz_menu = optionMenu(h= 21)
	menuItem('{ As is }')
	for res in [str(2**q) for q in range(6, 14)]:
		menuItem(res)
	text(l= '', w= 3)
	setParent('..')

	text(l= '', h= 6)
	text(l= '  - Output Folder Path')
	text(l= '', h= 2)
	rowLayout(nc= 2, adj= 1)
	outputDir_textF = textField(text= '')
	ocBtn_textF_choose = iconTextButton(i= 'fileOpen.png', w= 20, h= 20)
	setParent('..')

	text(l= '', h= 8)
	separator()
	text(l= '', h= 2)
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
		iconImg = 'SP_FileDialogBack_Disabled.png' if mainVis else 'nodeGrapherGear.svg'
		iconTextButton(configBtn, e= 1, i= iconImg)
		columnLayout(column_workArea, e= 1, vis= not mainVis)
		columnLayout(column_settings, e= 1, vis= mainVis)
		window(windowName, e= 1,
			t= windowTitle + (windowSettings if mainVis else ''),
			h= height_settings if mainVis else (height_workArea + height_offset))

	configBtn.setCommand(switchSettingsUI)


	def listSbsrenderArgsFiles(*args):
		workConfig = sbsrender.workConfig
		sbsarFile_menu.clear()
		for root, dirs, files in os.walk(workConfig['sbsarLib']):
			for f in files:
				if f.endswith(".json"):
					fileName = os.path.join(root, f).split(workConfig['sbsarLib'])[-1]
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


	def checkTextureFile(*args):
		sbsrender.sbsArgsFile = sbsarFile_menu.getValue()
		sbsrender.isUDIM = udim_mqsb.isChecked()
		sbsrender.sepUDIM = sepUDIM_btn.getLabel()
		sbsrender.sepTYPE = sepTYPE_btn.getLabel()
		sbsrender.get_sbsArgs()
		inputDir = os.path.abspath(inputDir_textF.getText())
		dirWalk = walk_mqsb.isChecked()
		extType = inputExt_menu.getValue()
		extType = '' if extType == '. ***' else extType
		# reset
		checkResult_txsc.removeAll()
		sbsrender.imgInputSet = {}
		# analyse
		sbsrender.imageFileNameAnalyse(inputDir, dirWalk, extType)
		for item in sbsrender.imgInputSet:
			checkResult_txsc.append(item)

	checkTexture_btn.setCommand(partial(checkTextureFile))


	def scrollList_deselectAll(*args):
		checkResult_txsc.deselectAll()
	def scrollList_doubleClick(*args):
		item = checkResult_txsc.getSelectItem()
		if item:
			print '-'*10
			print '***  ' + item[0]
			info = sbsrender.imgInputSet[item[0]]
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
		outputFormat = outputExt_menu.getValue()
		outputFormat = '' if outputFormat == '{ As is }' else outputFormat
		outputSize = outputSiz_menu.getValue()
		outputSize = '' if outputSize == '{ As is }' else outputSize
		buildShad = shad_mqsb.isChecked()
		outputDirTF = outputDir_textF.getText()
		outputDir = os.path.abspath(outputDirTF) if outputDirTF else ''
		if selt_mqsb.isChecked():
			selectedItem = checkResult_txsc.getSelectItem()
			allItems = checkResult_txsc.getAllItems()
			for item in allItems:
				if not item in selectedItem:
					sbsrender.imgInputSet.pop(item, None)
		if sbsrender.imgInputSet:
			progressWindow(t= 'SBS2MAYA Converting...', max= len(sbsrender.imgInputSet), ii= True)
			sbsrender.dist(outputFormat, outputSize, buildShad, outputDir, sbsProcBar)
		else:
			warning('SBS2MAYA : Empty input.')

	sendMission_btn.setCommand(partial(sendMission))

	def saveLastStatus(*args):
		workConfig = sbsrender.workConfig
		if workConfig['saveLast']:
			lastStatus = sbsrender.lastStatus
			lastStatus['inputPath'] = inputDir_textF.getText()
			lastStatus['outputPath'] = outputDir_textF.getText()
			lastStatus['walkSub'] = walk_mqsb.isChecked()
			lastStatus['udim_uv'] = udim_mqsb.isChecked()
			lastStatus['sep_name'] = sepUDIM_btn.getLabel()
			lastStatus['sep_udim'] = sepTYPE_btn.getLabel()
			lastStatus['img_type'] = inputExt_menu.getValue()
			lastStatus['hide_udim'] = hide_mqsb.isChecked()
			lastStatus['selected'] = selt_mqsb.isChecked()
			lastStatus['buildShd'] = shad_mqsb.isChecked()
			lastStatus['outFormat'] = outputExt_menu.getValue()
			lastStatus['outSize'] = outputSiz_menu.getValue()
			sbsrender.set_lastStatus(lastStatus)

	window(windowName, e= 1, w= windowWidth, h= height_workArea, cc= saveLastStatus)

	def restoreLastStatus():
		workConfig = sbsrender.workConfig
		if workConfig['saveLast']:
			lastStatus = sbsrender.lastStatus
			inputDir_textF.setText(lastStatus['inputPath'])
			outputDir_textF.setText(lastStatus['outputPath'])
			walk_mqsb.setChecked(lastStatus['walkSub'])
			udim_mqsb.setChecked(lastStatus['udim_uv'])
			sepUDIM_btn.setLabel(lastStatus['sep_name'])
			sepTYPE_btn.setLabel(lastStatus['sep_udim'])
			inputExt_menu.setValue(lastStatus['img_type'])
			hide_mqsb.setChecked(lastStatus['hide_udim'])
			selt_mqsb.setChecked(lastStatus['selected'])
			shad_mqsb.setChecked(lastStatus['buildShd'])
			outputExt_menu.setValue(lastStatus['outFormat'])
			outputSiz_menu.setValue(lastStatus['outSize'])
	
	restoreLastStatus()

	showWindow(windowName)

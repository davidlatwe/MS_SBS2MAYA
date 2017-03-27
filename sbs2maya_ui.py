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
sbs_typeA = ['albedo', 'metalness', 'normal', 'roughness']
sbs_typeB = ['BaseColor', 'Metallic', 'Normal', 'Roughness']
sbs_typeC = ['BaseColor', 'Metalness', 'Normal', 'Roughness']
global sbs_type
sbs_type = []


def ui_main():
	
	windowName = 'ms_sbs2maya_mainUI'
	windowWidth = 320

	if window(windowName, q= 1, ex= 1):
		deleteUI(windowName)

	window(windowName, t= 'SBS 2 MAYA - v1.2', s= 0, mxb= 0, mnb= 0)
	main_column = columnLayout(adj= 1, cal= 'left')
	
	#main_form = formLayout()

	bannerArea = columnLayout(adj= 1)
	bannerTxt = text(l= 'SBS2MAYA', w= windowWidth)
	QBannerTxt = mqt.convert(bannerTxt)
	QBannerTxt.setStyleSheet('QObject {font: bold 42px; color: #222222;}')
	setParent('..')

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
	hide_mqsb = mqsb.SwitchBox(onl= 'Yes, Hide', ofl= 'No, Show All', w= 180, h= 20, v= False, p= cmC)
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
	rowLayout(nc= 3, adj= 1)
	text(l= '  - Convert Selected Only', al= 'left', h= 20)
	columnLayout()
	cmD= columnLayout()
	selt_mqsb = mqsb.SwitchBox(onl= 'Yes, Selected', ofl= 'No, All', w= 180, h= 24, v= False, p= cmD)
	setParent('..')
	setParent('..')
	text(l= '', w= 1)
	setParent('..')

	rowLayout(nc= 3, adj= 1)
	text(l= '  - Build VRay Shader', al= 'left', h= 20)
	columnLayout()
	cmE= columnLayout()
	shad_mqsb = mqsb.SwitchBox(onl= 'Yes', ofl= 'No', w= 180, h= 24, v= True, p= cmE)
	setParent('..')
	setParent('..')
	text(l= '', w= 1)
	setParent('..')

	rowLayout(nc= 3, adj= 1, h= 30)
	text(l= ' + Output Texture File Format', al= 'left', h= 20)
	outputExt_menu = optionMenu(h= 21)
	menuItem('{ As is }')
	for ext in ext_list:
		menuItem(ext)
	text(l= '', w= 10)
	setParent('..')

	rowLayout(nc= 3, adj= 1, h= 30)
	text(l= ' + Output Texture Size', al= 'left', h= 20)
	outputSiz_menu = optionMenu(h= 21)
	menuItem('{ As is }')
	for siz in siz_list:
		menuItem(siz)
	text(l= '', w= 10)
	setParent('..')
	
	text(l= '', h= 6)
	rowLayout(nc= 3, adj= 2)
	text(l= '', w= 1)
	sendMission_btn = button(l= 'Start Process', h= 40)
	text(l= '', w= 1)
	setParent('..')
	text(l= '', h= 2)


	window(windowName, e= 1, w= windowWidth, h= 430)



	# #################################################################################################
	# ui commands
	# 
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


	def scrollList_deselectAll(*args):
		checkResult_txsc.deselectAll()
	def scrollList_doubleClick(*args):
		global textureInputSet
		item = checkResult_txsc.getSelectItem()
		if item:
			print '-'*10
			print '***  ' + item[0]
			for i, info in enumerate(textureInputSet[item[0]]):
				print '[' + str(i) + ']  ' + info
			warning('SBS2MAYA : Info printed out, Please see scriptEditor.')

	checkResult_txsc.deleteKeyCommand(partial(scrollList_deselectAll))
	checkResult_txsc.doubleClickCommand(partial(scrollList_doubleClick))


	global textureInputSet
	textureInputSet = {}
	def checkTextureFile(*args):
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
		pathTmp = []
		itemName_currentMatch = ''
		for f in fileList:
			fileName = os.path.basename(os.path.splitext(f)[0])
			typeName = fileName.split(sepTYPE)[-1]
			itemName = fileName[:-(len(typeName) + 1)]
			udimCode = itemName.split(sepUDIM)[-1] if isUDIM else ''
			if not isUDIM and hide_mqsb.isChecked() and len(itemName) > 5 and itemName[-5] in ['_', '.']:
				continue
			if not itemName_currentMatch and not itemName == itemName_currentMatch:
				if len(pathTmp) > 0 and len(pathTmp) < 6:
					pathTmp = []
			if typeName in sbs_type and (udimCode.isdigit() if isUDIM else True):
				if typeName == sbs_type[0] and not pathTmp:
					pathTmp.append(os.path.dirname(f))
					pathTmp.append(os.path.splitext(f)[-1][1:])
					itemName_currentMatch = itemName
				if len(pathTmp) >= 2:
					pathTmp.append(f)
			if len(pathTmp) == 6:
				textureInputSet[itemName] = pathTmp
				pathTmp = []

		for item in textureInputSet:
			checkResult_txsc.append(item)

	checkTexture_btn.setCommand(partial(checkTextureFile))

	def sendMission(*args):
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
			sbs2maya.dist(textureInputSet, outputFormat, outputSize, sepTYPE, isUDIM, buildShad, outputDir)
		else:
			warning('SBS2MAYA : Empty input.')

	sendMission_btn.setCommand(partial(sendMission))


	showWindow(windowName)
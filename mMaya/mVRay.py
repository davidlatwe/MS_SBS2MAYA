# -*- coding:utf-8 -*-
'''
Created on 2016.12.30

@author: davidpower
'''
from pymel.core import *


def setVrayTextureFilter(textureNode, filterType):
	"""
	"""
	mel.eval('vray addAttributesFromGroup "' + textureNode + '" vray_texture_filter 1;')
	textureNode.vrayTextureSmoothType.set(filterType)


def setVrayTextureGamma(textureNode, colorspace):
	"""
	"""
	mel.eval('vray addAttributesFromGroup "' + textureNode + '" vray_file_gamma 1;')
	textureNode.vrayFileColorSpace.set(colorspace)
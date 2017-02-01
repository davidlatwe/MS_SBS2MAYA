# -*- coding:utf-8 -*-
'''
Created on 2016.12.30

@author: davidpower
'''
from pymel.core import *


def createShader(shaderType, shaderNode_name, noSG= None):
	"""
	"""
	shaderNode = shadingNode(shaderType, asShader= 1, n= shaderNode_name)
	shaderNodeSG = None
	if not noSG:
		shaderNodeSG = sets(renderable= 1, noSurfaceShader= 1, empty= 1, n= shaderNode.name() + 'SG')
		shaderNode.outColor.connect(shaderNodeSG.surfaceShader)

	return shaderNode, shaderNodeSG


def createFileTexture(textureNode_name, place2dNode_name):
	"""
	"""
	textureNode = shadingNode('file', asTexture= 1, icm= 1, n= textureNode_name)
	place2dNode = shadingNode('place2dTexture', asUtility= 1, icm= 1, n= place2dNode_name)

	place2dNode.coverage.connect(textureNode.coverage, f= 1)
	place2dNode.translateFrame.connect(textureNode.translateFrame, f= 1)
	place2dNode.rotateFrame.connect(textureNode.rotateFrame, f= 1)
	place2dNode.mirrorU.connect(textureNode.mirrorU, f= 1)
	place2dNode.mirrorV.connect(textureNode.mirrorV, f= 1)
	place2dNode.stagger.connect(textureNode.stagger, f= 1)
	place2dNode.wrapU.connect(textureNode.wrapU, f= 1)
	place2dNode.wrapV.connect(textureNode.wrapV, f= 1)
	place2dNode.repeatUV.connect(textureNode.repeatUV, f= 1)
	place2dNode.offset.connect(textureNode.offset, f= 1)
	place2dNode.rotateUV.connect(textureNode.rotateUV, f= 1)
	place2dNode.noiseUV.connect(textureNode.noiseUV, f= 1)
	place2dNode.vertexUvOne.connect(textureNode.vertexUvOne, f= 1)
	place2dNode.vertexUvTwo.connect(textureNode.vertexUvTwo, f= 1)
	place2dNode.vertexUvThree.connect(textureNode.vertexUvThree, f= 1)
	place2dNode.vertexCameraOne.connect(textureNode.vertexCameraOne, f= 1)
	place2dNode.outUV.connect(textureNode.uv, f= 1)
	place2dNode.outUvFilterSize.connect(textureNode.uvFilterSize, f= 1)

	return textureNode, place2dNode


def dumpToBin(shadingNodes, binName):
	"""
	"""
	binMembership(shadingNodes, add= binName)
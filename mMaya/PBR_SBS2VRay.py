# -*- coding:utf-8 -*-
'''
Created on 2017.04.09

@author: davidpower
'''
from pymel.core import *
import mMaya; reload(mMaya)
import mMaya.mShading as mShading; reload(mShading)
import mMaya.mTexture as mTexture; reload(mTexture)
import mMaya.mVRay as mVRay; reload(mVRay)


def buildShader():
	"""
	"""
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
# MS_SBS2MAYA

Moonshine Pipeline Tool - for sbs

## TODO:

#### UI Settings

* Base
	* sbsrender exec path
	* sbsarLib path

* output
	* output size
	* output format

* options
	* compression
	* memory
	* engine

#### Template(JSON)

* sbsarFile

	* sbsarGraph - one or all
	* input_channel map
	* output_channel map
	* direct copy list

* mayaVRayShader

	* textureFile noed input map
	* shader naming map

#### Rule

* If render only selected graph/output, can't build vray shading network.
* Selected graph/output rendering can be used in updating image outputs.

---

## DOC:

[Substance Batchtools User's Guide - sbsrender](https://support.allegorithmic.com/documentation/display/SB10/sbsrender)

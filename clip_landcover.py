#Define the function to clip land cover (if landcover is vector) 
def Clip_Landcover(InputFeatures, ClipFeatures, OutputFeatureClass):
	arcpy.analysis.Clip(InputFeatures, ClipFeatures, OutputFeatureClass)
	# Save the output 
	return OutputFeatureClass

#Define to extract the land cover by mask (if landcover is raster)
def ExtractByMask_Landcover(InputRaster, InputMask):
	# Execute ExtractByMask
	outExtractByMask = arcpy.sa.ExtractByMask(InputRaster, InputMask)
	# Save the output 
	output = r"E:\NOVA IMS\Muenster_semester\4_Python\PROJECT\Owls\Owls.gdb\LC2012_bb"
	outExtractByMask.save(output)
	return output

# Set local variables (vector case)
InputFeatures = "CLC2012_DEv"
ClipFeatures = "territory_bb"
OutputFeatureClass = r"E:\NOVA IMS\Muenster_semester\4_Python\PROJECT\Owls\Owls.gdb\CLC2012_territory_bb"

#Set local variables (raster case)
# Set local variables
InputRaster = "CLC2012_DEr"
InputMask= "territory_bb"

#Testing the functions
# Execute Clip
Clip_Landcover(InputFeatures, ClipFeatures, OutputFeatureClass)

# Execute ExtractByMask
ExtractByMask_Landcover(InputRaster, InputMask)

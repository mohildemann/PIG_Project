import numpy as np
import arcpy
import math
from matplotlib import cm
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from functools import reduce
import random
import scipy.stats as stats
import datetime
from arcpy import env, analysis, management
from arcpy.sa import *
arcpy.CheckOutExtension('Spatial')
arcpy.env.overwriteOutput = True
from functools import reduce
from scipy.spatial import distance
import pickle
import pandas as pd
from datetime import datetime
import dataprocessing

def main():
    ##Inputs from Charly Brown
    arcpy.env.workspace = r'D:\Master_Shareverzeichnis\2.Semester\PythonGIS\FinalProject\budo_budo.gdb'
    selected_seasons = []
    selected_bird_ids = ["1751", "1292"]
    selected_gender = []
    buffer_size = 15
    buffer_size_default = None

    if buffer_size is None:
        buffer_size = buffer_size_default

    df_metadata = pd.read_csv(r'D:\Master_Shareverzeichnis\2.Semester\PythonGIS\FinalProject\movebank\eagle_owl\Eagle owl Reinhard Vohwinkel MPIO-reference-data.csv')
    # Set local variables (vector case)
    InputFeatures_name = "CLC2012_DEv"
    ClipFeatures_name = "territory_bb"
    OutputFeatureClass_name = "CLC2012_territory_bb"

    #Set local variables for landuse extraction (raster case)
    #InputRaster_name = "CLC2012_DEr"
    #InputMask_name= "territory_bb"

    #change ID type to string
    df_metadata["tag-id"] = df_metadata["tag-id"].astype(str)

    dataprocessing.get_territories_from_selected_features("all_birds",selected_seasons,selected_bird_ids,selected_gender, buffer_size,df_metadata)

    # Execute Clip
    #dataprocessing.Clip_Landcover(InputFeatures_name, ClipFeatures_name, OutputFeatureClass_name)

    # Execute ExtractByMask
    #dataprocessing.ExtractByMask_Landcover(InputRaster_name, InputMask_name)
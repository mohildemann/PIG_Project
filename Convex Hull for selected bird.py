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


def unique_values(table, field):
    #this function returns the unique values of a feature
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({row[0] for row in cursor})

def select_features( input_data, output_data,field_name, selection_value):
    #this function does a attribute selection in a more generic way than the standard arcpy.Select_analysis
    qry = str(field_name) + "= '" + str(selection_value) + "'"
    arcpy.Select_analysis(input_data, output_data,qry)

def update_datetime_to_seasons(input_features):
    with arcpy.da.UpdateCursor(input_features, ["timestamp","time"]) as dt_cursor:
        for row in dt_cursor:
            if row[1] not in ["spring","summer","autumn","winter"]:
                month  = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S').strftime('%B')
                if month in ["March", "April", "May"]:
                    row[1] = "spring"
                elif month in ["June", "July", "August"]:
                    row[1] = "summer"
                elif month in ["September", "October", "November"]:
                    row[1] = "autumn"
                else:
                    row[1] = "winter"
                dt_cursor.updateRow(row)

def select_features_by_season(input_features, selected_seasons, output_name):
    if len(selected_seasons) >1 :
        qry = """time IN {0}""".format(str(selected_seasons))
    else:
        qry = "time" + "= '" + str(selected_seasons[0]) + "'"
    arcpy.Select_analysis(input_features, output_name, qry)



def get_territories_from_selected_features(all_birds,selected_seasons,selected_bird_ids,selected_gender,buffer_size, metadata = None):
    unique_bird_ids = unique_values(all_birds, 'tag_ident')
    selected_birds = unique_bird_ids

    # Get all tag_idents with the timestamp and save in numpy array
    if len(selected_bird_ids) > 0:
        selected_birds = []
        for unique_id in unique_bird_ids:
            if unique_id in selected_bird_ids:
                selected_birds.append(unique_id)

    if len(selected_gender) > 0 and metadata is not None:
        fildered_metadata = metadata[metadata["animal-sex"] == selected_gender[0]]
        # filtering data
        iterator = 0
        for unique_id in selected_birds:
            if not fildered_metadata['tag-id'].str.contains(unique_id).any():
                selected_birds.pop(iterator)
            iterator = iterator + 1

    if len(selected_seasons) > 0:
        update_datetime_to_seasons(all_birds)
        select_features_by_season(all_birds, selected_seasons, "in_memory\selected_Points_for_convex_hull")
    else:
        arcpy.CopyFeatures_management(all_birds,  "in_memory\selected_Points_for_convex_hull")

    for unique_bird_id in selected_birds:
        #Get only the rows that are in the specified
        select_features("in_memory\selected_Points_for_convex_hull", "bird_" + str(unique_bird_id), 'tag_ident', unique_bird_id)
        create_convex_hull("bird_" + str(unique_bird_id), "conv_hull_" + str(unique_bird_id), buffer_size)

def create_convex_hull(input,output_name, distance):
    #this function creates the convex hulls for the territories.
    # 1. Create buffers around the points with a dissolve type all (every points leads to one buffer)
    # 2. Overlapping buffers will be combined to one feature with arcpy.MultipartToSinglepart
    # 3. The biggest shape will be considered as the convex hull for the territory for the specific bird with the selected points
    # Buffer areas of impact around major roads
    distanceField = str(distance) + " Meter"
    sideType = "FULL"
    endType = "ROUND"
    dissolveType = "ALL"
    arcpy.Buffer_analysis(input, "in_memory\\"+ output_name + "buffer_output", distanceField, sideType, endType, dissolveType)
    arcpy.MultipartToSinglepart_management("in_memory\\"+output_name +"buffer_output", output_name + "buffer_output_comb")
    arcpy.Select_analysis( output_name +"buffer_output_comb", "in_memory\\"+ output_name +"buffer_output_comb_max",
                          "Shape_Area = (SELECT MAX( Shape_Area) FROM " +  str(output_name + "buffer_output_comb" + ")" ))
    arcpy.Delete_management(output_name +"buffer_output_comb")
    arcpy.analysis.Intersect([input,"in_memory\\"+ output_name +"buffer_output_comb_max"],"in_memory\\"+ output_name +"buffer_output_comb_max_Inter", "ALL", None,
                             "POINT")
    arcpy.management.MinimumBoundingGeometry("in_memory\\"+ output_name +"buffer_output_comb_max_Inter", output_name + "territory_bb", "CONVEX_HULL", "ALL", None,
                                             "NO_MBG_FIELDS")
##Inputs from Charly Brown
arcpy.env.workspace = r'D:\Master_Shareverzeichnis\2.Semester\PythonGIS\FinalProject\budo_budo.gdb'
selected_seasons = []
selected_bird_ids = ["1751", "1292"]
selected_gender = []
buffer_size = 15
df_metadata = pd.read_csv(r'D:\Master_Shareverzeichnis\2.Semester\PythonGIS\FinalProject\movebank\eagle_owl\Eagle owl Reinhard Vohwinkel MPIO-reference-data.csv')

#change ID type to string
df_metadata["tag-id"] = df_metadata["tag-id"].astype(str)

get_territories_from_selected_features("all_birds",selected_seasons,selected_bird_ids,selected_gender, buffer_size,df_metadata)

import numpy as np
from math import pi
import matplotlib.pyplot as plt
import arcpy
from textwrap import wrap
import arcpy
import datetime
from arcpy import env, analysis, management
from arcpy.sa import *
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(3035)
arcpy.CheckOutExtension('Spatial')
arcpy.env.overwriteOutput = True
import pandas as pd
from datetime import datetime
import time
import os

shapefile_birds = arcpy.GetParameterAsText(0)
csv_owl_metadata = arcpy.GetParameterAsText(1)
buffer_distance_territory = arcpy.GetParameterAsText(2)
buffer_distance_territory_other = arcpy.GetParameterAsText(3)
select_gender_boolean = arcpy.GetParameterAsText(4)
selected_gender = arcpy.GetParameterAsText(5)
select_seasons_boolean = arcpy.GetParameterAsText(6)
selected_seasons = arcpy.GetParameterAsText(7)
select_bird_id_boolean = arcpy.GetParameterAsText(8)
selected_bird_ids = arcpy.GetParameterAsText(9)
workspace = arcpy.GetParameterAsText(10)
landuse_InputFeatures_name = r"landuse.gdb\CLC2012_DEv"
landuse_InfoTable = r"landuse.gdb\CLC2012_DEv_Statistics3"


def main(shapefile_birds, buffer_distance_territory, buffer_distance_territory_other,
         csv_owl_metadata, select_gender_boolean,selected_gender, select_seasons_boolean, selected_seasons, select_bird_id_boolean,
         selected_bird_ids, workspace, landuse_InputFeatures_name, landuse_info_table):
    arcpy.CreateFileGDB_management(workspace, "owlsGDB.gdb")
    trash = arcpy.CreateFileGDB_management(workspace, "trash.gdb")
    trash_path = os.path.join(workspace, "trash.gdb")
    arcpy.env.workspace = workspace + r"\owlsGDB.gdb"

    if buffer_distance_territory is None:
        buffer_size = buffer_distance_territory_other
    else:
        buffer_size = buffer_distance_territory

    if select_bird_id_boolean.lower() == 'false':
        selected_bird_ids = []

    if select_seasons_boolean.lower() == 'false':
        selected_seasons = ["Spring", "Summer", "Fall", "Winter"]

    df_metadata = pd.read_csv(csv_owl_metadata)
    df_metadata["tag-id"] = df_metadata["tag-id"].astype(str)

    # Do the actual calculation of the territories
    get_territories_from_selected_features(shapefile_birds, selected_seasons, selected_bird_ids,
                                           buffer_size, trash_path, df_metadata)

    # Getting the information of the landuse
    territory_w_landuse = extract_landuse_information(landuse_InputFeatures_name)

    # Writing the information to a pandas dataframe
    territory_w_landuse_df = generate_bubo_df(territory_w_landuse)

    whole_dataframe = territory_w_landuse_df.to_csv(os.path.join(workspace, "whole_dataframe.csv"))
    #drop all rows wo landuse information
    #territory_w_landuse_df = territory_w_landuse_df.dropna(subset=['season'], inplace=True)

    # Generate aggregated pandas dataframes as input for plots
    general_info = aggregate_general_bubo_landuse_information(territory_w_landuse_df)
    general_info.to_csv(os.path.join(workspace, "general_info.csv"))

    specific_landuse_info_season = aggregate_specific_bubo_landuse_information(territory_w_landuse_df,                                                                         aggregate_column="season")
    specific_landuse_info_season.to_csv(os.path.join(workspace, "specific_landuse_info_season.csv"))

    season_info = aggregate_specific_column(territory_w_landuse_df, aggregate_column="season")
    season_info.to_csv(os.path.join(workspace, 'season_info.csv'))

    specific_info_gender = aggregate_specific_bubo_landuse_information(territory_w_landuse_df,    aggregate_column="gender")
    specific_info_gender.to_csv(os.path.join(workspace, 'specific_info_gender.csv'))

    # logic for the plots, which depends on the selection and the available data
    # logic 0: no condition           -->    data_preparation_CLC_graphs(path_CLC_shp,general_info, 0)

    # logic 1: select_gender_boolean -->     if male and female exist: data_preparation_CLC_graphs(path_CLC_shp,specific_landuse_info_gender, 1)

    # logic 2: select_seasons_boolean -->    if more than 1 seasons exists :data_preparation_CLC_graphs(path_CLC_shp,specific_landuse_info_season, 2)

    #function for logic one
    def plot_gender_info():
        # give if specific information for gender required and male and female exist
        if specific_info_gender["gender"].nunique()>1:
            data_preparation_CLC_graphs(landuse_info_table, specific_info_gender,workspace, 1)

    #function logic 2
    def plot_season_info():
        # give plot if specific info for season required and more than one season exists
        if specific_landuse_info_season["season"].nunique() > 1:
            data_preparation_CLC_graphs(landuse_info_table, specific_landuse_info_season,workspace, 2)
    #function logic 3
    def plot_selected_birds_info():
        if whole_dataframe["tag_ident"].nunique() > 1:
            plot_gender_info()
            plot_season_info()
        else:
            plot_season_info()

    #call the plot functions,
    # give general information in each case
    data_preparation_CLC_graphs(landuse_info_table,general_info,workspace, 0)
   
    plot_gender_info()
    plot_season_info()

    # Delete all unnnecessary information
    arcpy.Delete_management(trash)
    arcpy.Delete_management("trash.gdb")

    # close/save necessary on disc
    all_featureclasses = arcpy.ListFeatureClasses()
    # Close and save all featureclasses that are not in trash
    for fc in all_featureclasses:
        fc = None
    landuse_InputFeatures_name = None
    landuse_InfoTable = None

def unique_values(table, field):
    # this function returns the unique values of a feature
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({row[0] for row in cursor})


def select_features(input_data, output_data, field_name, selection_value):
    start = time.time()
    # this function does a attribute selection in a more generic way than the standard arcpy.Select_analysis
    qry = str(field_name) + "= '" + str(selection_value) + "'"
    arcpy.Select_analysis(input_data, output_data, qry)
    end = time.time()
    print("Time for select_features: " + str(end - start))


def update_datetime_to_seasons(input_features):
    start = time.time()
    with arcpy.da.UpdateCursor(input_features, ["timestamp", "time"]) as dt_cursor:
        for row in dt_cursor:
            if row[1] not in ["Spring", "Summer", "Fall", "Winter"]:
                month = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S').strftime('%B')
                if month in ["March", "April", "May"]:
                    row[1] = "Spring"
                elif month in ["June", "July", "August"]:
                    row[1] = "Summer"
                elif month in ["September", "October", "November"]:
                    row[1] = "Fall"
                else:
                    row[1] = "Winter"
                dt_cursor.updateRow(row)
    end = time.time()
    print("Time for update_datetime_to_seasons: " + str(end - start))

def select_features_by_season(input_features, selected_seasons, output_name):
    start = time.time()
    if len(selected_seasons) > 1:
        qry = """time IN {0}""".format(str(selected_seasons))
    else:
        qry = "time" + "= '" + str(selected_seasons[0]) + "'"
    arcpy.Select_analysis(input_features, output_name, qry)
    end = time.time()
    print("Time for select_features_by_season: " + str(end - start))

def filter_by_gender(bird_ids, metadata, selected_gender):
    remaining_ids = []
    for i in bird_ids:
        if metadata[metadata["tag-id"]== str(i)]["gender"] == selected_gender:
            remaining_ids.append(i)
    return remaining_ids

def get_territories_from_selected_features(all_birds, selected_seasons, selected_bird_ids, buffer_size, trash,
                                           metadata=None):
    unique_bird_ids = unique_values(all_birds, 'tag_ident')
    selected_birds = unique_bird_ids
    # Get all tag_idents with the timestamp and save in numpy array
    if len(selected_bird_ids) > 0:
        selected_birds = []
        for unique_id in unique_bird_ids:
            if unique_id in selected_bird_ids:
                selected_birds.append(unique_id)
    #fill the empty column "time" with the season
    update_datetime_to_seasons(all_birds)

    if select_gender_boolean.lower == "true":
        selected_birds = filter_by_gender(selected_birds, metadata, selected_gender)

    for season_iterator in range(len(selected_seasons)):
        select_features_by_season(all_birds, [selected_seasons[season_iterator]],
                                  trash + "\selected_Points_for_convex_hull" + selected_seasons[season_iterator])
        for unique_bird_id in selected_birds:
            start_bird = time.time()
            # Get only the rows that are in the specified
            select_features(trash + "\\selected_Points_for_convex_hull" + selected_seasons[season_iterator],
                            "bird_" + str(unique_bird_id) + selected_seasons[season_iterator], 'tag_ident',
                            unique_bird_id)
            bird = metadata[metadata["tag-id"] == unique_bird_id]
            gender = bird["animal-sex"].values[0]
            create_convex_hull("bird_" + str(unique_bird_id) + selected_seasons[season_iterator],
                               "conv_hull_" + str(unique_bird_id) + selected_seasons[season_iterator], buffer_size,
                               unique_bird_id, selected_seasons[season_iterator], gender, trash)
            end_bird = time.time()
            print("Time used for bird " + unique_bird_id + ": " + str(
                end_bird - start_bird))


def create_convex_hull(input, output_name, distance, bird_id, season, gender, trash):
    start = time.time()
    if arcpy.Exists(trash + "\\" + output_name + "buffer_output"):
        arcpy.Delete_management(trash + "\\" + output_name + "buffer_output")
    if arcpy.Exists(output_name + "buffer_output_comb"):
        arcpy.Delete_management(output_name + "buffer_output_comb")
    if arcpy.Exists(trash + "\\" + output_name + "buffer_output_comb_max_Inter"):
        arcpy.Delete_management(trash + "\\" + output_name + "buffer_output_comb_max_Inter")
    if arcpy.Exists(output_name + "territory_bb"):
        arcpy.Delete_management(output_name + "territory_bb")
    # this function creates the convex hulls for the territories.
    # 1. Create buffers around the points with a dissolve type all (every points leads to one buffer)
    # 2. Overlapping buffers will be combined to one feature with arcpy.MultipartToSinglepart
    # 3. The biggest shape will be considered as the convex hull for the territory for the specific bird with the selected points
    # Buffer areas of impact around major roads
    distanceField = str(distance) + " Meter"
    sideType = "FULL"
    endType = "ROUND"
    dissolveType = "ALL"
    arcpy.Buffer_analysis(input, trash + "\\" + output_name + "buffer_output", distanceField, sideType, endType,
                          dissolveType)
    arcpy.MultipartToSinglepart_management(trash + "\\" + output_name + "buffer_output",
                                           output_name + "buffer_output_comb")
    arcpy.Select_analysis(output_name + "buffer_output_comb", trash + "\\" + output_name + "buffer_output_comb_max",
                          "Shape_Area = (SELECT MAX( Shape_Area) FROM " + str(output_name + "buffer_output_comb" + ")"))

    arcpy.analysis.Intersect([input, trash + "\\" + output_name + "buffer_output_comb_max"],
                             trash + "\\" + output_name + "buffer_output_comb_max_Inter", "ALL", None,
                             "POINT")

    # only create output if points of selection exist
    if int(arcpy.GetCount_management(trash + "\\" + output_name + "buffer_output_comb_max_Inter").getOutput(0)) > 0:
        arcpy.management.MinimumBoundingGeometry(trash + "\\" + output_name + "buffer_output_comb_max_Inter",
                                                 output_name + "territory_bb", "CONVEX_HULL", "ALL", None,
                                                 "NO_MBG_FIELDS")
        arcpy.AddField_management(output_name + "territory_bb", "tag_ident", "TEXT", 9, "", "", "tag_ident", "NULLABLE")
        arcpy.AddField_management(output_name + "territory_bb", "season", "TEXT", 9, "", "", "season", "NULLABLE")
        arcpy.AddField_management(output_name + "territory_bb", "gender", "TEXT", 9, "", "", "gender", "NULLABLE")
        cursor = arcpy.UpdateCursor(output_name + "territory_bb")
        row = cursor.next()
        while row:
            row.setValue("tag_ident", str(bird_id))
            row.setValue("season", season)
            row.setValue("gender", gender)
            cursor.updateRow(row)
            row = cursor.next()
    arcpy.Delete_management(output_name + "buffer_output_comb")
    end = time.time()
    print("Time for create_convex_hull: " + str(end - start))


def extract_landuse_information(landuse_vector):
    start = time.time()
    fcList = arcpy.ListFeatureClasses()
    input_merge = []
    fieldMappings = arcpy.FieldMappings()
    for fc in fcList:
        desc = arcpy.Describe(fc)
        if "conv_hull_" in fc and "territory_bb" in fc:
            input_merge.append(desc.name)
    for i in range(len(input_merge)):
        fieldMappings.addTable(input_merge[i])
    # Add all fields from both oldStreets and newStreets

    arcpy.management.Merge(input_merge, "merged_territories", field_mappings=fieldMappings)
    arcpy.analysis.Intersect(["merged_territories", landuse_vector],
                             "merged_territories_w_landuse",
                             "ALL", None, "INPUT")
    end = time.time()
    print("Time for Intersection with landuse: " + str(end - start))
    return "merged_territories_w_landuse"


def generate_bubo_df(input_shapefile):
    return pd.DataFrame(
        arcpy.da.FeatureClassToNumPyArray(input_shapefile,
                                          ["tag_ident", "season", "gender", "CLC_CODE", "LABEL3v2", "Shape_Area"],
                                          skip_nulls=False,
                                          null_value=-99999))


def aggregate_general_bubo_landuse_information(input_df):
    general_landuse_info = input_df.groupby(["CLC_CODE","LABEL3v2"], as_index=False)[['Shape_Area']].mean()
    return general_landuse_info


def aggregate_specific_bubo_landuse_information(input_df, aggregate_column=None):
    column_specific_info_with_landuse = input_df.groupby([aggregate_column,"CLC_CODE","LABEL3v2"], as_index=False)[
        ['Shape_Area']].mean()
    return column_specific_info_with_landuse


def aggregate_specific_column(input_df, aggregate_column=None):
    column_specific_info = input_df.groupby(["CLC_CODE",aggregate_column], as_index=False)[['Shape_Area']].mean()
    return column_specific_info


def bird_specific_info(input_df, bird_ids):
    input_df_filter = input_df[input_df['tag_ident'].isin([bird_ids])]
    info_for_specific_birds = input_df_filter.groupby(["CLC_CODE","LABEL3v2"], as_index=False)[['Shape_Area']].mean()
    return info_for_specific_birds


# Function to create Radar Chart by comparing female and male bubo bubos
def createRadarGender(name_bubo_bubo, data_values_m, data_values_f, attributes, workspace):
    print("Creating graph with gender information")
    attributes = ['\n'.join(wrap(l, 11)) for l in attributes]
    data_values_m += data_values_m[:1]
    data_values_f += data_values_f[:1]
    angles = [n / 6 * 2 * pi for n in range(6)]
    angles += angles[:1]
    angles2 = [n / 6 * 2 * pi for n in range(6)]
    angles2 += angles2[:1]
    ax = plt.subplot(111, polar=True)
    ax = plt.subplot(111, polar=True)
    plt.xticks(angles[:-1], attributes)
    ax.plot(angles, data_values_m)
    ax.fill(angles, data_values_m, 'blue', alpha=0.1)
    ax.plot(angles2, data_values_f)
    ax.fill(angles2, data_values_f, 'red', alpha=0.1)
    ax.set_title(name_bubo_bubo)
    labels = ('Males', 'Females')
    legend = ax.legend(labels, loc=(0.9, .95),
                       labelspacing=0.1, fontsize='small')
    plt.savefig(os.path.join(workspace, "genders.png"))
    plt.show()
    plt.close() 

    

# Function to create Radar Chart in a general overview for all the bubo bubos
def createRadarGeneral(name_bubo_bubo, data_values, attributes,workspace):
    print("Creating graph general")
    attributes = ['\n'.join(wrap(l, 11)) for l in attributes]
    data_values += data_values[:1]
    angles = [n / 6 * 2 * pi for n in range(6)]
    angles += angles[:1]
    ax = plt.subplot(111, polar=True)
    plt.xticks(angles[:-1], attributes)
    ax.plot(angles, data_values)
    ax.fill(angles, data_values, 'orange', alpha=0.1)
    ax.set_title(name_bubo_bubo)
    plt.savefig(os.path.join(workspace,"general.png"))
    plt.show()
    plt.close() 

# Function to create Radar Chart per each season for the bubo bubos
def createRadarSeasons(name_bubo_bubo, data_values, attributes, row, color_var, max_value):
    print("Creating graph season")
    attributes = [ '\n'.join(wrap(l, 17)) for l in attributes]
    data_values += data_values [:1]
    angles = [n / 6 * 2 * pi for n in range(6)]
    angles += angles [:1]
    ax = plt.subplot(2,2,row+1, polar=True)
    for theta, label in zip(ax.get_xticks(), ax.get_xticklabels()):
        theta = theta * ax.get_theta_direction() + ax.get_theta_offset()
        theta = np.pi/2 - theta
        y, x = np.cos(theta), np.sin(theta)
        if y >= 0.5 and x==0:
            label.set_verticalalignment('bottom')
        elif y >= 0.5 and x > 0.1:
            label.set_verticalalignment('bottom')
            label.set_horizontalalignment('left')
        elif y <= -0.5 and x == 0:
            label.set_verticalalignment('top')
        elif y >= -0.5 and x <= -0.1:
            label.set_verticalalignment('top')
            label.set_horizontalalignment('right')
        elif x >= 0.1 and y == 0:
            label.set_horizontalalignment('left')
        elif x <= -0.1 and y ==0:
            label.set_horizontalalignment('right')
        else:
            label.set_horizontalalignment('left')
            label.set_verticalalignment('top')

    plt.xticks(angles[:-1], attributes)
    axes = ax.plot(angles,data_values, color=color_var)
    ax.fill(angles, data_values, color=color_var, alpha=0.1)
    ax.set_title(name_bubo_bubo, y=1.2)
    plt.ylim(0, round(max_value))


def data_preparation_CLC_graphs(path_summary_table, data_filtered,workspace, type_request):
    dic_codes = {}
    default_field_ord_area = []
    default_cod_ord_area = []
    print("Calculating dictionary and other arrays")
    for row in arcpy.da.SearchCursor(path_summary_table, ['CLC_CODE', 'LABEL3v2', 'SUM_Shape_Area'],
                                     sql_clause=(None, 'ORDER BY SUM_Shape_Area DESC')):
        dic_codes[row[0]] = row[1]
        default_field_ord_area.append(row[1])
        default_cod_ord_area.append(row[0])
    # Call the fucntion to build the graph general
    if type_request == 0:
        types_LC = []
        area_totals = []
        codes_CLC = []
        i = 0
        for i in range(len(data_filtered)):
            types_LC.append(dic_codes[data_filtered.CLC_CODE[i]])
            codes_CLC.append(str(data_filtered.CLC_CODE[i]))
            area_totals.append(data_filtered.Shape_Area[i] / 10000)
        len_initial_types_LC = len(types_LC)
        if len_initial_types_LC < 6:
            for i in default_field_ord_area:
                if i not in types_LC:
                    types_LC.append(i)
                    area_totals.append(0)
                print(types_LC)
                if len(types_LC) >= 6:
                    break
        else:
            types_LC = types_LC[0:6]
            area_totals = area_totals[0:6]
        createRadarGeneral("All Bubo Bubos", area_totals, types_LC,workspace,)
    ###Case when the user wants the graphs per gender
    elif type_request == 1:
        # Filtering data for males
        filter_df_males = data_filtered[data_filtered.gender == 'm']
        final_df_males = filter_df_males.sort_values(by=['Shape_Area'], ascending=False)
        # Filteringdata for females
        filter_df_females = data_filtered[data_filtered.gender == 'f']
        final_df_females = filter_df_females.sort_values(by=['Shape_Area'], ascending=False)
        top_3_males = final_df_males.head(3)
        top_3_females = final_df_females.head(3)
        print(top_3_males)
        print(top_3_females)
        final_types = (list(set().union(top_3_males.CLC_CODE, top_3_females.CLC_CODE)))
        print(final_types)
        final_attributes = []
        area_totals_males = []
        area_totals_females = []
        for i in final_types:
            print(i)
            query_area_m = final_df_males.loc[final_df_males['CLC_CODE'] == i]
            query_area_f = final_df_females.loc[final_df_females['CLC_CODE'] == i]
            final_attributes.append(dic_codes[i])
            if query_area_m.empty == True:
                area_totals_males.append(0)
            else:
                area_totals_males.append((query_area_m['Shape_Area'].iloc[0]) / 10000)

            if query_area_f.empty == True:
                area_totals_females.append(0)
            else:
                area_totals_females.append((query_area_f['Shape_Area'].iloc[0]) / 10000)
        print(final_attributes)
        print(area_totals_males)
        print(area_totals_females)
        if len(final_attributes) < 6:
            for i in default_cod_ord_area:
                if i not in final_types:
                    final_attributes.append(dic_codes[i])
                    query_area_m = final_df_males.loc[final_df_males['CLC_CODE'] == i]
                    if query_area_m.empty == True:
                        area_totals_males.append(0)
                    else:
                        area_totals_males.append((query_area_m['Shape_Area'].iloc[0]) / 10000)
                    query_area_f = final_df_females.loc[final_df_females['CLC_CODE'] == i]
                    if query_area_f.empty == True:
                        area_totals_females.append(0)
                    else:
                        area_totals_females.append((query_area_f['Shape_Area'].iloc[0]) / 10000)
                print(final_attributes)
                if len(final_attributes) >= 6:
                    break
            print(final_attributes)
            print(area_totals_males)
            print(area_totals_females)
            createRadarGender("Male And Female Bubo Bubos", area_totals_males, area_totals_females, final_attributes,workspace,)
    # Case for the seasons
    elif type_request == 2:
        season_available = data_filtered.season.unique()
        print(season_available)
        my_dpi = 96
        plt.figure(figsize=(1000 / my_dpi, 1000 / my_dpi), dpi=my_dpi)
        # Create a color palette:
        my_palette = plt.cm.get_cmap("Set2", 4)
        row = 0
        maximum_Value_Area = data_filtered['Shape_Area'].max()
        arcpy.AddMessage("Maximum value =" + str(maximum_Value_Area))
        for season in season_available:
            query_season = data_filtered.loc[data_filtered['season'] == season]
            final_df_season = query_season.sort_values(by=['Shape_Area'], ascending=False)
            final_df_season = final_df_season.reset_index()
            print(final_df_season)
            types_LC = []
            area_totals = []
            codes_CLC = []
            i = 0
            for i in range(len(final_df_season)):
                types_LC.append(dic_codes[final_df_season.CLC_CODE[i]])
                codes_CLC.append(str(final_df_season.CLC_CODE[i]))
                area_totals.append(final_df_season.Shape_Area[i] / 10000)
            len_initial_types_LC = len(types_LC)
            if len_initial_types_LC < 6:
                for i in default_field_ord_area:
                    if i not in types_LC:
                        types_LC.append(i)
                        area_totals.append(0)
                    print(types_LC)
                    if len(types_LC) >= 6:
                        break
            else:
                types_LC = types_LC[0:6]
                area_totals = area_totals[0:6]

            createRadarSeasons(season, area_totals, types_LC, row, my_palette(row), maximum_Value_Area/10000)
            row += 1

        '''# Loop to plot
        for row in range(0, 4):
            area_totals = area_totals[0:6]
            print(area_totals)
            createRadarSeasons("All Bubo Bubos", area_totals, types_LC, row, my_palette(row))
            #make_spider( row=row, title='group '+df['group'][row], color=my_palette(row))'''
        plt.tight_layout()
        plt.savefig(os.path.join(workspace,"seasons.png"))
        plt.show()
        plt.close() 
    else:
        print("Error with the type of request to draw the spider graph")


if __name__ == '__main__':
    main(shapefile_birds, buffer_distance_territory, buffer_distance_territory_other,
         csv_owl_metadata, select_gender_boolean, selected_gender, select_seasons_boolean, selected_seasons, select_bird_id_boolean,
         selected_bird_ids, workspace, landuse_InputFeatures_name, landuse_InfoTable)


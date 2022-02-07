import gdal
import numpy as np
import os
import sys
import requests
# import numpy.ma as ma
# import copy
import json
import boto3
from botocore.exceptions import ClientError
# import geopandas as gpd
import logging

s3 = boto3.client('s3')
#%%

def lambda_handler(event, context):

    body = json.loads(event['body'])
    json_file = body
    #get  input json and extract geojson
    try:
        project_id = json_file["project_id"]
        pol_shape = json_file["polygon"]
        roi_shape = json_file["ROI"]
    except Exception as e:
        print(e)
        print("Input JSON field have an error.")
    

    #for local
    # path_to_tmp = "/home/christos/Desktop/SCiO_Projects/lup4ldn/data/cropped_files/"
    #for aws
    path_to_tmp = "/tmp/"
    
    # s3_file_path = '/vsis3/lup4ldn-dataset' + "/" + country_iso + "/"
    # s3_file_path = "https://lup4ldn-default-global-datasets.s3.eu-central-1.amazonaws.com/"
    s3_file_path = '/vsis3/lup4ldn-default-global-datasets/'
    path_to_100m_grid = s3_file_path + "global_100m_grid.tif"
    save_intersection_path = path_to_tmp + "intersection.tif"
    
    
    response = requests.post("https://lambda.qvantum.polygons-intersection.scio.services", json = json_file)
    
    if response.text=="not intersecting geometries":
        return {
             "statusCode": 200,
             "body": "not intersecting geometries"
             }
    else:
        json_file = response.json()
 
        gdal_warp_kwargs_target_area = {
            'format': 'GTiff',
            'cutlineDSName' : json.dumps(json_file),
            'cropToCutline' : True,
            'height' : None,
            'width' : None,
            'srcNodata' : -32768.0,
            'dstNodata' : -32768.0,
            'creationOptions' : ['COMPRESS=DEFLATE']
        }
        
        
        
        try:
            gdal.Warp(save_intersection_path,path_to_100m_grid,**gdal_warp_kwargs_target_area)
        except Exception as e:
            print(e)
            print("if 'returned NULL without setting an error', probably at least one of the file paths is wrong")
        
        try:
            intersect_area_tif = gdal.Open(save_intersection_path)
            intersect_area_array = intersect_area_tif.ReadAsArray()
        except Exception as e:
            print(e)
            print("if ''NoneType' object has no attribute', probably the file path is wrong")
        
        intersect_area_array = np.where(intersect_area_array!=-32768,1,-32768)
        
        unique,counts = np.unique(intersect_area_array,return_counts=True)
        total_hectares = 9*int(counts[-1])
        return {
             "statusCode": 200,
             "body": total_hectares
             }
    

#%%
# #overlapping
# input_json = {
#     "body" :"{\"project_id\":\"some_project_ID\",\"ROI\":{\"type\":\"FeatureCollection\",\"features\":[{\"type\":\"Feature\",\"properties\":{},\"geometry\":{\"type\":\"Polygon\",\"coordinates\":[[[8.865966796875,36.416862115300304],[9.4647216796875,36.416862115300304],[9.4647216796875,36.804886560237236],[8.865966796875,36.804886560237236],[8.865966796875,36.416862115300304]]]}},{\"type\":\"Feature\",\"properties\":{},\"geometry\":{\"type\":\"Polygon\",\"coordinates\":[[[8.4869384765625,35.66622234103479],[8.7066650390625,35.66622234103479],[8.7066650390625,36.33725319397006],[8.4869384765625,36.33725319397006],[8.4869384765625,35.66622234103479]]]}},{\"type\":\"Feature\",\"properties\":{},\"geometry\":{\"type\":\"Polygon\",\"coordinates\":[[[8.4759521484375,34.75966612466248],[8.6737060546875,34.75966612466248],[8.6737060546875,35.33977430038646],[8.4759521484375,35.33977430038646],[8.4759521484375,34.75966612466248]]]}}]},\"polygon\":{\"type\":\"FeatureCollection\",\"features\":[{\"type\":\"Feature\",\"properties\":{},\"geometry\":{\"type\":\"Polygon\",\"coordinates\":[[[9.184570312499998,36.34610265300638],[9.5635986328125,36.34610265300638],[9.5635986328125,36.901587303978474],[9.184570312499998,36.901587303978474],[9.184570312499998,36.34610265300638]]]}},{\"type\":\"Feature\",\"properties\":{},\"geometry\":{\"type\":\"Polygon\",\"coordinates\":[[[8.5418701171875,36.20217441183449],[8.773956298828125,36.20217441183449],[8.773956298828125,36.34942094089192],[8.5418701171875,36.34942094089192],[8.5418701171875,36.20217441183449]]]}}]}}"
#     }

##non-overlapping
# input_json = {
#     "body" :"{\"project_id\":\"some_project_ID\",\"ROI\":{\"type\":\"FeatureCollection\",\"features\":[{\"type\":\"Feature\",\"properties\":{},\"geometry\":{\"type\":\"Polygon\",\"coordinates\":[[[8.865966796875,36.416862115300304],[9.4647216796875,36.416862115300304],[9.4647216796875,36.804886560237236],[8.865966796875,36.804886560237236],[8.865966796875,36.416862115300304]]]}},{\"type\":\"Feature\",\"properties\":{},\"geometry\":{\"type\":\"Polygon\",\"coordinates\":[[[8.4869384765625,35.66622234103479],[8.7066650390625,35.66622234103479],[8.7066650390625,36.33725319397006],[8.4869384765625,36.33725319397006],[8.4869384765625,35.66622234103479]]]}},{\"type\":\"Feature\",\"properties\":{},\"geometry\":{\"type\":\"Polygon\",\"coordinates\":[[[8.4759521484375,34.75966612466248],[8.6737060546875,34.75966612466248],[8.6737060546875,35.33977430038646],[8.4759521484375,35.33977430038646],[8.4759521484375,34.75966612466248]]]}}]},\"polygon\":{\"type\":\"FeatureCollection\",\"features\":[{\"type\":\"Feature\",\"properties\":{},\"geometry\":{\"type\":\"Polygon\",\"coordinates\":[[[9.6295166015625,35.178298352001214],[10.2996826171875,35.178298352001214],[10.2996826171875,35.51881428123057],[9.6295166015625,35.51881428123057],[9.6295166015625,35.178298352001214]]]}},{\"type\":\"Feature\",\"properties\":{},\"geometry\":{\"type\":\"Polygon\",\"coordinates\":[[[9.68994140625,34.129994745824746],[10.2117919921875,34.129994745824746],[10.2117919921875,34.79125047210742],[9.68994140625,34.79125047210742],[9.68994140625,34.129994745824746]]]}}]}}"
# }

# results = lambda_handler(input_json,1)
# print(results)
#%%

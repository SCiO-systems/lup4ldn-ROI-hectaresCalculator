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
        if pol_shape==None:
            pol_shape = requests.get(json_file["polygon_url"])
            pol_shape = json.loads(pol_shape.text) #.replace("'",'"')
            json_file["polygon"] = pol_shape
            
        roi_shape = json_file["ROI"]
        if roi_shape==None:
            roi_shape = requests.get(json_file["ROI_file_url"])
            roi_shape = json.loads(roi_shape.text) #.replace("'",'"')
            json_file["ROI"] = roi_shape
            
    except Exception as e:
        print("Input JSON field have an error.")
        return {
            "statusCode": 400,
            "body": e
        }
    
    
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
            print("if 'returned NULL without setting an error', probably at least one of the file paths is wrong")
            raise(e)
        
        try:
            intersect_area_tif = gdal.Open(save_intersection_path)
            intersect_area_array = intersect_area_tif.ReadAsArray()
        except Exception as e:
            print("if ''NoneType' object has no attribute', probably the file path is wrong")
            return {
                "statusCode": 400,
                "body": e
            }
        
        intersect_area_array = np.where(intersect_area_array!=-32768,1,-32768)
        
        unique,counts = np.unique(intersect_area_array,return_counts=True)
        total_hectares = int(counts[-1])
        return {
             "statusCode": 200,
             "body": total_hectares
             }

from django.shortcuts import render, HttpResponse
from ui.forms import ImportGeojsonfileForm

import ee
ee.Initialize()
import os
from datetime import date , timedelta
from datetime import datetime
from dateutil.parser import parse
import pandas as pd
import pygeoj
import json
# from django.conf.settings import PROJECT_ROOT
# Create your views here.

def index(request):
    coord=''
    from_date = '2019-01-01'
    end_date = '2019-04-30'
    if request.method == "POST":
        form = ImportGeojsonfileForm(request.POST, request.FILES)
        if form.is_valid():
            geoJson = request.FILES['import_file']
            data = json.load(geoJson)
            a = pygeoj.load(None,data)
            for feature in a:
                coord = feature.geometry.coordinates
                gtype = feature.geometry.type
                print(gtype)
            from_date = request.POST['from_date']
            end_date = request.POST['end_date']
    # file_ = open(os.path.join(PROJECT_ROOT, 'filename'))
    form = ImportGeojsonfileForm()
    if(coord!=''):
        geometry = ee.Geometry.MultiPolygon(coord)
    else:
        geometry = ee.Geometry.Polygon([[[83.829803, 28.316455],
            [84.157677, 28.316455],
            [84.157677, 28.150463],
            [83.829803, 28.150463]]])

    context = {
        "ndvi": ndvi(geometry, from_date, end_date),
        "Evi":Evi(geometry, from_date, end_date),
        'ndbi':ndbi(geometry, from_date, end_date),
        'ndwi':ndwi(geometry, from_date, end_date),
        "band_viz" : getVisParam(),
        "geometry" : coord,
        "title" : "Earthengine api",
        "startDate" : '2019-01-01',
        "endDate" : '2019-04-30',
        "form":form,
    }

    return render(request,'index.html',context)

def getVisParam():
    viz_param = {
        "min" : 0.0,
        "max" : 0.4,
        "palette" : ['black','yellow'],
    }
    return viz_param

def index_calculation(a,b):
    return a.subtract(b).divide(a.add(b))

def ndvi(geometry, from_date, end_date):
    image = ee.ImageCollection("COPERNICUS/S2_SR").filterDate(from_date, end_date).median().clip(geometry)
    ndvi_image = ndvi1(image)
    viz_param = ndviParams()
    map_id_dict = ee.Image(ndvi_image).getMapId(viz_param)
    tile = str(map_id_dict['tile_fetcher'].url_format)
    return tile

def ndvi1(a):
    return a.normalizedDifference(['B8', 'B4']).rename('NDVI')

def ndviParams():
    viz_param = {
        "min" : -0.4,
        "max" : 0.6,
        "palette" : ['blue','white','DarkGreen'],
    }
    return viz_param

def Evi(geometry, from_date, end_date):
    # added image that contain the toa correction
    image = ee.ImageCollection("LANDSAT/LC08/C01/T1_TOA").filterDate(from_date,end_date).filterMetadata("CLOUD_COVER","less_than",10).median().clip(geometry)
    Evi_calclucate = Evi_function(image)
    viz_param = ndviParams()
    map_id_dict = ee.Image(Evi_calclucate).getMapId(viz_param)
    tile = str(map_id_dict['tile_fetcher'].url_format)
    return tile

def Evi_function(a):
    evi = a.expression(
    '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))', {
      'NIR': a.select('B5'),
      'RED': a.select('B4'),
      'BLUE': a.select('B2')
    })
    return evi

# adding the NDBI 
def ndbi(geometry, from_date, end_date):
    image = ee.ImageCollection("COPERNICUS/S2").filterDate(from_date, end_date).median().clip(geometry)
    ndbi_image = ndbiCalculate(image)
    ndbi_visulaize = ndbiParam()
    map_id_dict = ee.Image(ndbi_image).getMapId(ndbi_visulaize)
    tile = str(map_id_dict['tile_fetcher'].url_format)
    return tile

def ndbiCalculate(a):
    NIR = a.select('B8')
    SWIR = a.select('B11')
    return SWIR.subtract(NIR).divide(SWIR.add(NIR))

def ndbiParam():
    viz_param = {
         "min" : -0.8,
        "max" : 0.2,
        "palette" : ['blue','green','red'],
    }
    return viz_param
    # gives the value nearly equal to 0.1 - 0.3 for the built up area in nepal

# adding the ndwi 
def ndwi(geometry, from_date, end_date):
    image = image = ee.ImageCollection("LANDSAT/LC08/C01/T1_TOA").filterDate(from_date, end_date).filterMetadata('CLOUD_COVER','less_than',10).median().clip(geometry)
    ndwi_image = ndwiCalculate(image)#calculate the ndwi
    ndwi_visual = ndwiParms()#gives the visula varaible
    map_id_dict = ee.Image(ndwi_image).getMapId(ndwi_visual)
    tile = str(map_id_dict['tile_fetcher'].url_format)
    return tile

def ndwiCalculate(a):
    GREEN = a.select("B3")
    SWIR = a.select("B6")
    return GREEN.subtract(SWIR).divide(GREEN.add(SWIR))

def ndwiParms():
    viz_param = {
        "min" : -0.2,
        "max" : 0.5,
        "palette" : ['green','red','blue'],
    }
    return viz_param
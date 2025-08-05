# -*- coding: utf-8 -*-
"""
This script processes the output of the heatwave cluster identification algorithm
and tracks clusters over time to build heatwave events.

Adapted from the drought cluster tracking script by Julio E. Herrera Estrada, Ph.D.
"""

import yaml
import numpy as np
import pickle
from netCDF4 import Dataset
from datetime import datetime
from dateutil.relativedelta import relativedelta

import drought_clusters_utils as dclib

##################################################################################
############################ SET PATHS AND DEFINITIONS ###########################
##################################################################################

# Load config
with open("src/definitions.yaml") as f:
    definitions = yaml.load(f, Loader=yaml.FullLoader)

dataset = definitions["dataset"]
region = definitions["region"]
drought_metric = definitions["drought_metric"]
drought_threshold = definitions["drought_threshold"]
drought_threshold_name = str(drought_threshold)
start_year = definitions["start_year"]
end_year = definitions["end_year"]
lat_var = definitions["lat_var"]
lon_var = definitions["lon_var"]

clusters_partial_path = definitions["clusters_partial_path"]
clusters_full_path = f"{clusters_partial_path}/{dataset}/{region}/{drought_metric}/{drought_threshold_name}"

# File to get coordinates
f = Dataset(
    definitions["drought_metric_path"] + definitions["drought_metric_file_name"]
)
lons = f.variables[lon_var][:]
lats = f.variables[lat_var][:]
f.close()

##################################################################################
########################## TRACK HEATWAVE CLUSTERS THROUGH TIME ##################
##################################################################################

start_date = datetime(start_year, 5, 1)
end_date = datetime(end_year, 9, 30)
nt = (end_date - start_date).days + 1  # 日数据

dclib.track_heatwave_clusters_and_save(
    clusters_full_path,
    start_date,
    end_date,
    nt,
    lons,
    lats,
    drought_threshold_name,
    dataset,
)

print("✅ Done tracking heatwave clusters.")

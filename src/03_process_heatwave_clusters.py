# -*- coding: utf-8 -*-
"""
This script processes the output of the heatwave cluster identification algorithm
and tracks clusters over time to build heatwave events.

Adapted from the drought cluster tracking script by Julio E. Herrera Estrada, Ph.D.
"""

import glob
import os
import pickle
from datetime import datetime

import numpy as np
import yaml
from dateutil.relativedelta import relativedelta
from netCDF4 import Dataset

import heatwave_clusters_utils as hclib

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

# 检查实际可用的聚类文件来确定真实的结束日期
clusters_partial_path = definitions["clusters_partial_path"]
clusters_full_path = f"{clusters_partial_path}/{dataset}/{region}/{drought_metric}/{drought_threshold_name}"

# 获取所有可用的聚类文件
dict_files = glob.glob(f"{clusters_full_path}/heatwave-dictionary_*.pck")
if dict_files:
    # 从文件名中提取日期，找到真实的结束日期
    dates = []
    for f in dict_files:
        date_str = f.split("_")[-1].replace(".pck", "")
        try:
            date_obj = datetime.strptime(date_str, "%Y%m%d")
            dates.append(date_obj)
        except:
            continue

    if dates:
        dates.sort()
        actual_start_date = dates[0]
        actual_end_date = dates[-1]
        actual_nt = len(dates)

        print(
            f"📅 实际聚类文件日期范围: {actual_start_date.strftime('%Y-%m-%d')} 到 {actual_end_date.strftime('%Y-%m-%d')}"
        )
        print(f"📊 实际文件数量: {actual_nt}")

        # 使用实际的日期范围
        start_date = actual_start_date
        end_date = actual_end_date
        nt = actual_nt
    else:
        print("❌ 未找到有效的聚类文件")
        exit(1)
else:
    print("❌ 未找到聚类文件目录")
    exit(1)

hclib.track_heatwave_clusters_and_save(
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

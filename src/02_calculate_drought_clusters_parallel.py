# -*- coding: utf-8 -*-
"""
This script identifies 2D heatwave clusters for each time step using ERA5 temperature data.
Adapted from original drought code by Julio E. Herrera Estrada, Ph.D.
"""

import yaml
import numpy as np
from mpi4py import MPI
import pickle
from netCDF4 import Dataset
from datetime import datetime
from dateutil.relativedelta import relativedelta

import drought_clusters_utils as dclib

# Initialize MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

##################################################################################
############################ LOAD CONFIGURATION ##################################
##################################################################################

with open("src/definitions.yaml") as f:
    definitions = yaml.load(f, Loader=yaml.FullLoader)

dataset = definitions["dataset"]
region = definitions["region"]
start_year = definitions["start_year"]
end_year = definitions["end_year"]
periodic_bool = definitions["periodic_bool"]
heatwave_file_path = (
    definitions["drought_metric_path"] + definitions["drought_metric_file_name"]
)
lat_var = definitions["lat_var"]
lon_var = definitions["lon_var"]
minimum_area_threshold = definitions["minimum_area_threshold"]

# Cluster output folder
clusters_partial_path = definitions["clusters_partial_path"]
clusters_full_path = f"{clusters_partial_path}/{dataset}/{region}/heatwave/90p/"

##################################################################################
############################ LOAD INPUT DATA #####################################
##################################################################################

f = Dataset(heatwave_file_path)
T_actual = f.variables["T_actual"][:]  # shape: (time, lat, lon)
T_threshold = f.variables["T_threshold"][:]
heatwave_mask = f.variables["heatwave_mask"][:]
lons = f.variables[lon_var][:]
lats = f.variables[lat_var][:]
f.close()

start_date = datetime(start_year, 5, 1)  # May–Sep only
nsteps = T_actual.shape[0]
resolution_lon = np.mean(lons[1:] - lons[:-1])
resolution_lat = np.mean(lats[1:] - lats[:-1])

##################################################################################
#################### IDENTIFY HEATWAVE CLUSTERS (PER TIME STEP) ##################
##################################################################################


import os  # 确保放在文件顶部


def find_clusters(chunk):
    chunk_length = len(chunk)

    # 🛠️ 确保输出路径存在（只执行一次）
    if not os.path.exists(clusters_full_path):
        os.makedirs(clusters_full_path)

    for i in range(0, chunk_length):
        index = int(chunk[i])
        current_date = start_date + relativedelta(days=index)  # daily time
        safe_date_str = current_date.strftime("%Y%m%d")  # 🆗 无空格的日期字符串

        # STEP 1: Extract 2D fields for this timestep
        binary_mask = heatwave_mask[index, :, :]
        temp_diff = T_actual[index, :, :] - T_threshold[index, :, :]

        # STEP 2: Identify heatwave clusters using spatial connectivity
        print(
            f"Rank {rank + 1}: Identifying clusters for time step {index + 1} of {nsteps} ({i + 1}/{chunk_length})..."
        )
        cluster_count, cluster_dict = dclib.find_drought_clusters(
            binary_mask, lons, lats, resolution_lon, resolution_lat, periodic_bool
        )

        # STEP 3: Filter small clusters
        binary_mask, cluster_count, cluster_dict = dclib.filter_drought_clusters(
            binary_mask, cluster_count, cluster_dict, minimum_area_threshold
        )

        # STEP 4: Compute heatwave features (intensity, centroid)
        cluster_dict = dclib.add_heatwave_metrics(
            cluster_dict, temp_diff, lons, lats, resolution_lon, resolution_lat
        )

        # STEP 5: Save results with safe file names
        f_name_mask = f"{clusters_full_path}/heatwave-mask_{safe_date_str}.pck"
        f_name_dict = f"{clusters_full_path}/heatwave-dictionary_{safe_date_str}.pck"
        f_name_count = f"{clusters_full_path}/heatwave-count_{safe_date_str}.pck"

        with open(f_name_mask, "wb") as f:
            pickle.dump(binary_mask, f, pickle.HIGHEST_PROTOCOL)
        with open(f_name_dict, "wb") as f:
            pickle.dump(cluster_dict, f, pickle.HIGHEST_PROTOCOL)
        with open(f_name_count, "wb") as f:
            pickle.dump(cluster_count, f, pickle.HIGHEST_PROTOCOL)

        print(f"Rank {rank + 1}: Saved results for time step {index + 1}.")


##################################################################################
########################### PARALLEL EXECUTION ###################################
##################################################################################

offset = 0
h = np.ceil(nsteps / np.float32(size - offset))

if rank >= offset and rank < size - 1:
    chunk = np.arange((rank - offset) * h, (rank - offset) * h + h)
elif rank == size - 1:
    chunk = np.arange((rank - offset) * h, nsteps)

find_clusters(chunk)

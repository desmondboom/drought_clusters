# -*- coding: utf-8 -*-
import os
from datetime import datetime

import numpy as np
from netCDF4 import Dataset, date2num, num2date

# ----------------------------------------
# 用户需定义的路径和变量
# ----------------------------------------
dataset = "ERA5"
start_date = datetime(2011, 5, 1)
end_date = datetime(2020, 9, 30)

temp_path = "./data/era5_daily_mean_198005-202009_CHINA_new.nc"  # 你的实际文件路径
clim_path = "./data/era5_daily_mean_201105-201109_CHINA_new.nc"  # 气候基准期，用于计算阈值
output_path = "./data/processed/heatwave_processed.nc"

var_name = "t2m"  # NetCDF 中的温度变量名（单位为 Kelvin）
percentile_level = 90


# ----------------------------------------
# 加载原始温度数据（ERA5）
# ----------------------------------------
def load_temperature(path):
    f = Dataset(path)
    temp = f.variables[var_name][:]  # shape: (time, lat, lon)
    # 已经转换过单位，不需要再转换
    # temp = temp - 273.15  # 转为摄氏度
    time = f.variables["time"]
    lons = f.variables["lon"][:]
    lats = f.variables["lat"][:]
    time_units = time.units
    time_calendar = time.calendar if hasattr(time, "calendar") else "standard"
    dates = num2date(time[:], units=time_units, calendar=time_calendar)
    f.close()
    return temp, dates, lats, lons


T_actual, dates_actual, lats, lons = load_temperature(temp_path)
T_clim, dates_clim, _, _ = load_temperature(clim_path)

# ----------------------------------------
# 计算气候基准期每年同日的第 90 百分位（动态阈值）
# ----------------------------------------
T_threshold = np.full_like(T_actual, np.nan)

for day_index, target_date in enumerate(dates_actual):
    clim_days = [
        i
        for i, d in enumerate(dates_clim)
        if d.month == target_date.month and d.day == target_date.day
    ]
    if not clim_days:
        continue
    clim_samples = T_clim[clim_days, :, :]  # shape: (N_years, lat, lon)
    T_threshold[day_index, :, :] = np.percentile(clim_samples, percentile_level, axis=0)

# ----------------------------------------
# 生成二值热浪掩码矩阵（实际温度超过动态阈值）
# ----------------------------------------
heatwave_mask = (T_actual > T_threshold).astype(np.uint8)

# ----------------------------------------
# 保存到一个 NetCDF 文件中
# ----------------------------------------
output_nc = Dataset(output_path, "w", format="NETCDF4")
output_nc.createDimension("time", len(dates_actual))
output_nc.createDimension("lat", len(lats))
output_nc.createDimension("lon", len(lons))

# 时间变量
time_var = output_nc.createVariable("time", "f8", ("time",))
time_var.units = "hours since 1900-01-01 00:00:00"
time_var.calendar = "standard"
time_var[:] = date2num(dates_actual, units=time_var.units, calendar=time_var.calendar)

# 空间变量
output_nc.createVariable("lat", "f4", ("lat",))[:] = lats
output_nc.createVariable("lon", "f4", ("lon",))[:] = lons

# 写入变量
output_nc.createVariable("T_actual", "f4", ("time", "lat", "lon"), zlib=True)[:] = (
    T_actual
)
output_nc.createVariable("T_threshold", "f4", ("time", "lat", "lon"), zlib=True)[:] = (
    T_threshold
)
output_nc.createVariable("heatwave_mask", "i1", ("time", "lat", "lon"), zlib=True)[
    :
] = heatwave_mask

output_nc.description = "Processed ERA5 heatwave data with dynamic threshold and mask"
output_nc.close()
print("处理完成，数据保存为：", output_path)

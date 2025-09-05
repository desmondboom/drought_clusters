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
clim_path = (
    "./data/era5_daily_mean_201105-201109_CHINA_new.nc"  # 气候基准期，用于计算阈值
)
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
# 应用连续3天筛选（热浪定义要求至少连续3天）
# ----------------------------------------
def apply_consecutive_days_filter(mask, min_consecutive_days=3):
    """
    应用连续天数筛选，只保留连续至少min_consecutive_days天的热浪
    
    Args:
        mask: 3D数组 (time, lat, lon)，二值热浪掩码
        min_consecutive_days: 最小连续天数，默认3天
    
    Returns:
        filtered_mask: 筛选后的热浪掩码
    """
    print(f"应用连续{min_consecutive_days}天筛选...")
    
    nt, nlats, nlons = mask.shape
    filtered_mask = np.zeros_like(mask, dtype=np.uint8)
    
    # 使用向量化操作提高效率
    print(f"处理 {nlats} x {nlons} = {nlats * nlons} 个格点...")
    
    # 对每个格点进行时间序列分析
    processed = 0
    total = nlats * nlons
    
    for lat_idx in range(nlats):
        for lon_idx in range(nlons):
            time_series = mask[:, lat_idx, lon_idx]
            
            # 找到连续的热浪期
            consecutive_periods = find_consecutive_periods(time_series, min_consecutive_days)
            
            # 标记满足条件的连续期
            for start, end in consecutive_periods:
                filtered_mask[start:end+1, lat_idx, lon_idx] = 1
            
            processed += 1
            if processed % 10000 == 0:
                print(f"已处理 {processed}/{total} 个格点 ({processed/total*100:.1f}%)")
    
    # 统计筛选效果
    original_count = np.sum(mask > 0)
    filtered_count = np.sum(filtered_mask > 0)
    
    print(f"原始热浪格点总数: {original_count}")
    print(f"筛选后热浪格点总数: {filtered_count}")
    print(f"保留比例: {filtered_count / original_count * 100:.2f}%")
    
    return filtered_mask

def find_consecutive_periods(time_series, min_length):
    """
    找到时间序列中连续1的段落，长度至少为min_length
    
    Args:
        time_series: 1D二值数组
        min_length: 最小连续长度
    
    Returns:
        periods: 连续期的列表，每个元素为(start, end)元组
    """
    periods = []
    start = None
    
    for i, value in enumerate(time_series):
        if value == 1 and start is None:
            # 开始一个新的连续期
            start = i
        elif value == 0 and start is not None:
            # 结束当前连续期
            if i - start >= min_length:
                periods.append((start, i - 1))
            start = None
    
    # 处理序列末尾的情况
    if start is not None and len(time_series) - start >= min_length:
        periods.append((start, len(time_series) - 1))
    
    return periods

# 应用连续3天筛选
heatwave_mask = apply_consecutive_days_filter(heatwave_mask, min_consecutive_days=3)

# ----------------------------------------
# 保存到一个 NetCDF 文件中
# ----------------------------------------
output_nc = Dataset(output_path, "w", format="NETCDF4")
output_nc.createDimension("time", len(dates_actual))
output_nc.createDimension("lat", len(lats))
output_nc.createDimension("lon", len(lons))

# 时间变量
f_src = Dataset(temp_path)
src_time = f_src.variables["time"]
time_var = output_nc.createVariable("time", src_time.datatype, ("time",))
time_var.setncatts({k: getattr(src_time, k) for k in src_time.ncattrs()})
time_var[:] = src_time[:]
f_src.close()

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

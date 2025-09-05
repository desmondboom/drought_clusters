#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试第二步聚类识别的时间筛选
"""

import numpy as np
from netCDF4 import Dataset, num2date
from datetime import datetime

def debug_step2_timing():
    """调试第二步的时间筛选逻辑"""
    
    # 加载处理后的数据
    f = Dataset("./data/processed/heatwave_processed.nc")
    T_actual = f.variables["T_actual"][:]
    heatwave_mask = f.variables["heatwave_mask"][:]
    
    # 获取时间信息
    time_var = f.variables["time"]
    time_units = time_var.units
    time_calendar = time_var.calendar if hasattr(time_var, "calendar") else "standard"
    actual_dates = num2date(time_var[:], units=time_units, calendar=time_calendar)
    f.close()
    
    print(f"=== 原始数据信息 ===")
    print(f"总天数: {len(actual_dates)}")
    print(f"时间范围: {actual_dates[0]} 到 {actual_dates[-1]}")
    print(f"T_actual形状: {T_actual.shape}")
    print(f"heatwave_mask形状: {heatwave_mask.shape}")
    
    # 模拟第二步的时间筛选逻辑
    start_year = 2011
    end_year = 2020
    start_date = datetime(start_year, 5, 1)
    end_date = datetime(end_year, 9, 30)
    
    print(f"\n=== 目标时间范围 ===")
    print(f"开始日期: {start_date}")
    print(f"结束日期: {end_date}")
    
    # 筛选出目标时间段的数据
    time_mask = []
    for i, date in enumerate(actual_dates):
        if (date.year >= start_year and date.year <= end_year and 
            date.month >= 5 and date.month <= 9):
            time_mask.append(i)
    
    time_mask = np.array(time_mask)
    print(f"\n=== 筛选结果 ===")
    print(f"筛选出的天数: {len(time_mask)}")
    print(f"筛选出的日期范围: {actual_dates[time_mask[0]]} 到 {actual_dates[time_mask[-1]]}")
    
    # 检查筛选后的数据
    T_actual_filtered = T_actual[time_mask]
    heatwave_mask_filtered = heatwave_mask[time_mask]
    
    print(f"\n=== 筛选后数据统计 ===")
    print(f"T_actual_filtered形状: {T_actual_filtered.shape}")
    print(f"heatwave_mask_filtered形状: {heatwave_mask_filtered.shape}")
    
    # 检查每天的热浪情况
    daily_heatwave = np.sum(heatwave_mask_filtered > 0, axis=(1, 2))
    print(f"有热浪的天数: {np.sum(daily_heatwave > 0)}")
    print(f"最大日热浪格点数: {np.max(daily_heatwave)}")
    
    # 显示前10天的热浪情况
    print(f"\n=== 前10天热浪情况 ===")
    for i in range(min(10, len(time_mask))):
        date = actual_dates[time_mask[i]]
        heatwave_count = daily_heatwave[i]
        print(f"  {date.strftime('%Y-%m-%d')}: {heatwave_count} 个热浪格点")
    
    # 检查是否有问题
    if len(time_mask) == 0:
        print(f"\n❌ 错误：没有筛选出任何数据！")
        return
    
    if np.sum(daily_heatwave > 0) == 0:
        print(f"\n❌ 错误：筛选后的数据中没有热浪！")
        return
    
    print(f"\n✅ 筛选逻辑正常")

if __name__ == "__main__":
    debug_step2_timing()

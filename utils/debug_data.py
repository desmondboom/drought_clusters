#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试数据预处理结果
"""

import numpy as np
from netCDF4 import Dataset, num2date
import matplotlib.pyplot as plt

def debug_heatwave_data():
    """调试热浪数据"""
    
    # 加载处理后的数据
    f = Dataset("./data/processed/heatwave_processed.nc")
    T_actual = f.variables["T_actual"][:]
    T_threshold = f.variables["T_threshold"][:]
    heatwave_mask = f.variables["heatwave_mask"][:]
    
    # 获取时间信息
    time_var = f.variables["time"]
    time_units = time_var.units
    time_calendar = time_var.calendar if hasattr(time_var, "calendar") else "standard"
    dates = num2date(time_var[:], units=time_units, calendar=time_calendar)
    
    print(f"=== 数据基本信息 ===")
    print(f"时间范围: {dates[0]} 到 {dates[-1]}")
    print(f"总天数: {len(dates)}")
    print(f"T_actual形状: {T_actual.shape}")
    print(f"T_threshold形状: {T_threshold.shape}")
    print(f"heatwave_mask形状: {heatwave_mask.shape}")
    
    # 检查温度数据
    print(f"\n=== 温度数据统计 ===")
    print(f"T_actual范围: {np.nanmin(T_actual):.2f} 到 {np.nanmax(T_actual):.2f} °C")
    print(f"T_threshold范围: {np.nanmin(T_threshold):.2f} 到 {np.nanmax(T_threshold):.2f} °C")
    
    # 检查热浪掩膜
    print(f"\n=== 热浪掩膜统计 ===")
    print(f"热浪格点总数: {np.sum(heatwave_mask > 0)}")
    print(f"总格点数: {heatwave_mask.size}")
    print(f"热浪比例: {np.sum(heatwave_mask > 0) / heatwave_mask.size * 100:.2f}%")
    
    # 检查每天的热浪情况
    print(f"\n=== 每日热浪统计 ===")
    daily_heatwave = np.sum(heatwave_mask > 0, axis=(1, 2))
    print(f"有热浪的天数: {np.sum(daily_heatwave > 0)}")
    print(f"最大日热浪格点数: {np.max(daily_heatwave)}")
    
    # 找出热浪最多的几天
    top_days = np.argsort(daily_heatwave)[-5:]
    print(f"\n热浪最多的5天:")
    for i, day_idx in enumerate(top_days):
        print(f"  {i+1}. {dates[day_idx].strftime('%Y-%m-%d')}: {daily_heatwave[day_idx]} 格点")
    
    # 检查温度差异
    temp_diff = T_actual - T_threshold
    print(f"\n=== 温度差异统计 ===")
    print(f"温度差异范围: {np.nanmin(temp_diff):.2f} 到 {np.nanmax(temp_diff):.2f} °C")
    print(f"正差异格点数: {np.sum(temp_diff > 0)}")
    print(f"正差异比例: {np.sum(temp_diff > 0) / temp_diff.size * 100:.2f}%")
    
    # 可视化一个样本
    sample_idx = len(dates) // 2  # 中间的一天
    sample_date = dates[sample_idx]
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    # 实际温度
    im1 = ax1.imshow(T_actual[sample_idx], cmap='RdBu_r', origin='lower')
    ax1.set_title(f'实际温度 - {sample_date.strftime("%Y-%m-%d")}')
    ax1.set_xlabel('经度索引')
    ax1.set_ylabel('纬度索引')
    plt.colorbar(im1, ax=ax1, label='温度 (°C)')
    
    # 阈值温度
    im2 = ax2.imshow(T_threshold[sample_idx], cmap='RdBu_r', origin='lower')
    ax2.set_title(f'阈值温度 - {sample_date.strftime("%Y-%m-%d")}')
    ax2.set_xlabel('经度索引')
    ax2.set_ylabel('纬度索引')
    plt.colorbar(im2, ax=ax2, label='温度 (°C)')
    
    # 温度差异
    im3 = ax3.imshow(temp_diff[sample_idx], cmap='RdBu_r', origin='lower')
    ax3.set_title(f'温度差异 - {sample_date.strftime("%Y-%m-%d")}')
    ax3.set_xlabel('经度索引')
    ax3.set_ylabel('纬度索引')
    plt.colorbar(im3, ax=ax3, label='温度差异 (°C)')
    
    # 热浪掩膜
    im4 = ax4.imshow(heatwave_mask[sample_idx], cmap='Reds', origin='lower')
    ax4.set_title(f'热浪掩膜 - {sample_date.strftime("%Y-%m-%d")}')
    ax4.set_xlabel('经度索引')
    ax4.set_ylabel('纬度索引')
    plt.colorbar(im4, ax=ax4, label='热浪 (0/1)')
    
    plt.tight_layout()
    plt.savefig('debug_heatwave_data.png', dpi=150, bbox_inches='tight')
    print(f"\n可视化结果已保存到: debug_heatwave_data.png")
    plt.show()
    
    f.close()

if __name__ == "__main__":
    debug_heatwave_data()

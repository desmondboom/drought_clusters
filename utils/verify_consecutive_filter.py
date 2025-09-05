#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证连续3天筛选的效果
"""

import numpy as np
import netCDF4
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from datetime import datetime
import os

def verify_consecutive_filter():
    """验证连续3天筛选的效果"""
    
    print("=== 验证连续3天筛选效果 ===")
    
    # 读取处理后的数据
    data_path = "./data/processed/heatwave_processed.nc"
    if not os.path.exists(data_path):
        print(f"❌ 数据文件不存在: {data_path}")
        return
    
    f = Dataset(data_path)
    heatwave_mask = f.variables["heatwave_mask"][:]
    time_var = f.variables["time"]
    lats = f.variables["lat"][:]
    lons = f.variables["lon"][:]
    
    # 转换时间
    from netCDF4 import num2date
    actual_dates = num2date(time_var[:], units=time_var.units, 
                           calendar=getattr(time_var, "calendar", "standard"))
    f.close()
    
    print(f"数据形状: {heatwave_mask.shape}")
    print(f"时间范围: {actual_dates[0]} 到 {actual_dates[-1]}")
    
    # 1. 检查连续3天筛选的基本效果
    print(f"\n=== 基本统计 ===")
    total_grid_points = heatwave_mask.size
    heatwave_points = np.sum(heatwave_mask > 0)
    print(f"总格点数: {total_grid_points:,}")
    print(f"热浪格点数: {heatwave_points:,}")
    print(f"热浪比例: {heatwave_points/total_grid_points*100:.2f}%")
    
    # 2. 检查每日热浪格点数的分布
    daily_heatwave_counts = np.sum(heatwave_mask > 0, axis=(1, 2))
    print(f"\n=== 每日热浪统计 ===")
    print(f"有热浪的天数: {np.sum(daily_heatwave_counts > 0)}")
    print(f"最大日热浪格点数: {np.max(daily_heatwave_counts)}")
    print(f"平均日热浪格点数: {np.mean(daily_heatwave_counts):.1f}")
    
    # 3. 检查连续热浪期的分布
    print(f"\n=== 连续热浪期分析 ===")
    consecutive_periods = analyze_consecutive_periods(heatwave_mask, actual_dates)
    
    # 4. 检查特定时间段的热浪模式
    print(f"\n=== 夏季热浪模式检查 ===")
    check_summer_patterns(heatwave_mask, actual_dates)
    
    # 5. 可视化结果
    visualize_consecutive_filter_results(heatwave_mask, actual_dates, lats, lons)
    
    print(f"\n✅ 连续3天筛选验证完成")

def analyze_consecutive_periods(mask, dates):
    """分析连续热浪期的分布"""
    
    nt, nlats, nlons = mask.shape
    consecutive_periods = []
    
    # 对每个格点分析连续期
    for lat_idx in range(0, nlats, 10):  # 采样分析，每10个格点取一个
        for lon_idx in range(0, nlons, 10):
            time_series = mask[:, lat_idx, lon_idx]
            periods = find_consecutive_periods(time_series, 3)
            
            for start, end in periods:
                consecutive_periods.append({
                    'lat_idx': lat_idx,
                    'lon_idx': lon_idx,
                    'start_date': dates[start],
                    'end_date': dates[end],
                    'duration': end - start + 1
                })
    
    if consecutive_periods:
        durations = [p['duration'] for p in consecutive_periods]
        print(f"采样格点中发现的连续期数量: {len(consecutive_periods)}")
        print(f"连续期长度分布:")
        print(f"  3天: {sum(1 for d in durations if d == 3)} 个")
        print(f"  4-7天: {sum(1 for d in durations if 4 <= d <= 7)} 个")
        print(f"  8-14天: {sum(1 for d in durations if 8 <= d <= 14)} 个")
        print(f"  15天以上: {sum(1 for d in durations if d >= 15)} 个")
        print(f"最长连续期: {max(durations)} 天")
        
        # 显示最长的几个连续期
        sorted_periods = sorted(consecutive_periods, key=lambda x: x['duration'], reverse=True)
        print(f"\n最长的5个连续期:")
        for i, period in enumerate(sorted_periods[:5]):
            print(f"  {i+1}. {period['start_date'].strftime('%Y-%m-%d')} 到 {period['end_date'].strftime('%Y-%m-%d')} ({period['duration']}天)")
    
    return consecutive_periods

def find_consecutive_periods(time_series, min_length):
    """找到连续1的段落"""
    periods = []
    start = None
    
    for i, value in enumerate(time_series):
        if value == 1 and start is None:
            start = i
        elif value == 0 and start is not None:
            if i - start >= min_length:
                periods.append((start, i - 1))
            start = None
    
    if start is not None and len(time_series) - start >= min_length:
        periods.append((start, len(time_series) - 1))
    
    return periods

def check_summer_patterns(mask, dates):
    """检查夏季热浪模式"""
    
    # 筛选夏季数据 (6-8月)
    summer_indices = []
    for i, date in enumerate(dates):
        if date.month in [6, 7, 8]:
            summer_indices.append(i)
    
    if summer_indices:
        summer_mask = mask[summer_indices]
        summer_dates = [dates[i] for i in summer_indices]
        
        print(f"夏季(6-8月)数据天数: {len(summer_indices)}")
        print(f"夏季热浪格点总数: {np.sum(summer_mask > 0):,}")
        
        # 检查夏季连续热浪期
        summer_periods = []
        for lat_idx in range(0, summer_mask.shape[1], 20):  # 更稀疏的采样
            for lon_idx in range(0, summer_mask.shape[2], 20):
                time_series = summer_mask[:, lat_idx, lon_idx]
                periods = find_consecutive_periods(time_series, 3)
                
                for start, end in periods:
                    summer_periods.append({
                        'start_date': summer_dates[start],
                        'end_date': summer_dates[end],
                        'duration': end - start + 1
                    })
        
        if summer_periods:
            durations = [p['duration'] for p in summer_periods]
            print(f"夏季连续热浪期数量: {len(summer_periods)}")
            print(f"夏季最长连续期: {max(durations)} 天")
            print(f"夏季平均连续期长度: {np.mean(durations):.1f} 天")

def visualize_consecutive_filter_results(mask, dates, lats, lons):
    """可视化连续3天筛选结果"""
    
    # 创建图形
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('连续3天筛选效果验证', fontsize=16)
    
    # 1. 每日热浪格点数时间序列
    daily_counts = np.sum(mask > 0, axis=(1, 2))
    axes[0, 0].plot(daily_counts, linewidth=0.8)
    axes[0, 0].set_title('每日热浪格点数时间序列')
    axes[0, 0].set_xlabel('时间步')
    axes[0, 0].set_ylabel('热浪格点数')
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. 热浪格点数分布直方图
    axes[0, 1].hist(daily_counts[daily_counts > 0], bins=50, alpha=0.7, edgecolor='black')
    axes[0, 1].set_title('每日热浪格点数分布')
    axes[0, 1].set_xlabel('热浪格点数')
    axes[0, 1].set_ylabel('频次')
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. 选择几个代表性日期进行空间分布展示
    # 找到热浪格点数最多的几个日期
    top_dates_idx = np.argsort(daily_counts)[-3:]
    
    for i, date_idx in enumerate(top_dates_idx):
        if i >= 3:
            break
        row = 1
        col = i
        if i == 0:
            ax = axes[row, col]
        else:
            ax = axes[row, col] if col < 2 else axes[row, 1]
        
        heatwave_snapshot = mask[date_idx, :, :]
        im = ax.imshow(heatwave_snapshot, cmap='Reds', aspect='auto', 
                      extent=[lons.min(), lons.max(), lats.min(), lats.max()])
        ax.set_title(f'{dates[date_idx].strftime("%Y-%m-%d")} 热浪分布')
        ax.set_xlabel('经度')
        ax.set_ylabel('纬度')
        plt.colorbar(im, ax=ax, label='热浪掩码')
    
    plt.tight_layout()
    plt.savefig('verify_consecutive_filter.png', dpi=150, bbox_inches='tight')
    print(f"可视化结果已保存到: verify_consecutive_filter.png")
    plt.show()

if __name__ == "__main__":
    verify_consecutive_filter()

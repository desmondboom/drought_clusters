#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证pck文件正确性的脚本
"""

import os
import pickle
import numpy as np
from datetime import datetime
import glob

def verify_pck_files(cluster_path):
    """验证pck文件的基本信息"""
    
    # 获取所有pck文件
    mask_files = glob.glob(f"{cluster_path}/heatwave-mask_*.pck")
    dict_files = glob.glob(f"{cluster_path}/heatwave-dictionary_*.pck")
    count_files = glob.glob(f"{cluster_path}/heatwave-count_*.pck")
    
    print(f"=== 文件统计 ===")
    print(f"Mask文件数量: {len(mask_files)}")
    print(f"Dictionary文件数量: {len(dict_files)}")
    print(f"Count文件数量: {len(count_files)}")
    
    # 检查文件完整性
    print(f"\n=== 文件完整性检查 ===")
    dates = []
    for f in mask_files:
        date_str = f.split('_')[-1].replace('.pck', '')
        dates.append(date_str)
    
    dates.sort()
    print(f"日期范围: {dates[0]} 到 {dates[-1]}")
    print(f"总天数: {len(dates)}")
    
    # 检查几个样本文件
    print(f"\n=== 样本文件检查 ===")
    sample_files = dates[::len(dates)//5]  # 取5个样本
    
    for date_str in sample_files:
        print(f"\n--- 检查 {date_str} ---")
        
        # 检查mask文件
        mask_file = f"{cluster_path}/heatwave-mask_{date_str}.pck"
        if os.path.exists(mask_file):
            with open(mask_file, 'rb') as f:
                mask = pickle.load(f)
            print(f"  Mask形状: {mask.shape}, 类型: {mask.dtype}")
            print(f"  热浪格点数: {np.sum(mask > 0)}")
            print(f"  总格点数: {mask.size}")
            print(f"  热浪比例: {np.sum(mask > 0) / mask.size * 100:.2f}%")
        
        # 检查dictionary文件
        dict_file = f"{cluster_path}/heatwave-dictionary_{date_str}.pck"
        if os.path.exists(dict_file):
            with open(dict_file, 'rb') as f:
                cluster_dict = pickle.load(f)
            print(f"  聚类数量: {len(cluster_dict)}")
            
            if len(cluster_dict) > 0:
                # 显示第一个聚类的信息
                first_cluster = cluster_dict[1]
                print(f"  第一个聚类:")
                print(f"    面积: {first_cluster.get('area', 'N/A')} km²")
                print(f"    强度: {first_cluster.get('intensity', 'N/A')}")
                print(f"    质心: {first_cluster.get('centroid', 'N/A')}")
                print(f"    格点数: {len(first_cluster.get('coordinates', []))}")
        
        # 检查count文件
        count_file = f"{cluster_path}/heatwave-count_{date_str}.pck"
        if os.path.exists(count_file):
            with open(count_file, 'rb') as f:
                count = pickle.load(f)
            print(f"  聚类计数: {count}")

def check_date_consistency(cluster_path):
    """检查日期一致性"""
    print(f"\n=== 日期一致性检查 ===")
    
    mask_files = glob.glob(f"{cluster_path}/heatwave-mask_*.pck")
    dates = []
    for f in mask_files:
        date_str = f.split('_')[-1].replace('.pck', '')
        try:
            date_obj = datetime.strptime(date_str, '%Y%m%d')
            dates.append((date_str, date_obj))
        except:
            print(f"  警告: 无法解析日期 {date_str}")
    
    dates.sort(key=lambda x: x[1])
    
    # 检查日期连续性
    print(f"  日期范围: {dates[0][0]} 到 {dates[-1][0]}")
    
    # 检查是否有缺失的日期
    expected_dates = []
    current = dates[0][1]
    end = dates[-1][1]
    
    while current <= end:
        if current.month >= 5 and current.month <= 9:  # 只检查5-9月
            expected_dates.append(current.strftime('%Y%m%d'))
        current = current.replace(day=current.day + 1)
    
    actual_dates = [d[0] for d in dates]
    missing_dates = set(expected_dates) - set(actual_dates)
    
    if missing_dates:
        print(f"  缺失日期数量: {len(missing_dates)}")
        print(f"  前5个缺失日期: {sorted(list(missing_dates))[:5]}")
    else:
        print(f"  日期连续性: 正常")

def check_cluster_quality(cluster_path):
    """检查聚类质量"""
    print(f"\n=== 聚类质量检查 ===")
    
    dict_files = glob.glob(f"{cluster_path}/heatwave-dictionary_*.pck")
    
    total_clusters = 0
    total_days = 0
    cluster_areas = []
    cluster_intensities = []
    
    for dict_file in dict_files:
        with open(dict_file, 'rb') as f:
            cluster_dict = pickle.load(f)
        
        total_days += 1
        total_clusters += len(cluster_dict)
        
        for cluster_id, cluster_info in cluster_dict.items():
            if 'area' in cluster_info:
                cluster_areas.append(cluster_info['area'])
            if 'intensity' in cluster_info:
                cluster_intensities.append(cluster_info['intensity'])
    
    print(f"  总处理天数: {total_days}")
    print(f"  总聚类数: {total_clusters}")
    print(f"  平均每天聚类数: {total_clusters / total_days:.2f}")
    
    if cluster_areas:
        print(f"  聚类面积统计:")
        print(f"    最小: {min(cluster_areas):.0f} km²")
        print(f"    最大: {max(cluster_areas):.0f} km²")
        print(f"    平均: {np.mean(cluster_areas):.0f} km²")
        print(f"    中位数: {np.median(cluster_areas):.0f} km²")
    
    if cluster_intensities:
        print(f"  聚类强度统计:")
        print(f"    最小: {min(cluster_intensities):.2f}")
        print(f"    最大: {max(cluster_intensities):.2f}")
        print(f"    平均: {np.mean(cluster_intensities):.2f}")

if __name__ == "__main__":
    cluster_path = "./clusters_output/ERA5/China/heatwave/90p"
    
    if not os.path.exists(cluster_path):
        print(f"错误: 路径不存在 {cluster_path}")
        exit(1)
    
    verify_pck_files(cluster_path)
    check_date_consistency(cluster_path)
    check_cluster_quality(cluster_path)
    
    print(f"\n=== 验证完成 ===")

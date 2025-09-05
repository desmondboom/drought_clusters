#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速检查pck文件的基本信息
"""

import os
import pickle
import glob
from datetime import datetime

def quick_check():
    cluster_path = "./clusters_output/ERA5/China/heatwave/90p"
    
    if not os.path.exists(cluster_path):
        print(f"❌ 路径不存在: {cluster_path}")
        return
    
    # 检查文件数量
    mask_files = glob.glob(f"{cluster_path}/heatwave-mask_*.pck")
    dict_files = glob.glob(f"{cluster_path}/heatwave-dictionary_*.pck")
    count_files = glob.glob(f"{cluster_path}/heatwave-count_*.pck")
    
    print(f"📁 文件统计:")
    print(f"  Mask文件: {len(mask_files)}")
    print(f"  Dictionary文件: {len(dict_files)}")
    print(f"  Count文件: {len(count_files)}")
    
    if len(mask_files) == 0:
        print("❌ 没有找到任何pck文件")
        return
    
    # 检查日期范围
    dates = []
    for f in mask_files:
        date_str = f.split('_')[-1].replace('.pck', '')
        try:
            date_obj = datetime.strptime(date_str, '%Y%m%d')
            dates.append((date_str, date_obj))
        except:
            print(f"⚠️ 无法解析日期: {date_str}")
    
    dates.sort(key=lambda x: x[1])
    print(f"📅 日期范围: {dates[0][0]} 到 {dates[-1][0]}")
    
    # 检查几个样本
    print(f"\n🔍 样本检查:")
    sample_indices = [0, len(dates)//4, len(dates)//2, 3*len(dates)//4, -1]
    
    for i in sample_indices:
        if i < len(dates):
            date_str = dates[i][0]
            check_sample(cluster_path, date_str)

def check_sample(cluster_path, date_str):
    """检查单个样本"""
    try:
        # 检查mask
        mask_file = f"{cluster_path}/heatwave-mask_{date_str}.pck"
        with open(mask_file, 'rb') as f:
            mask = pickle.load(f)
        
        # 检查dictionary
        dict_file = f"{cluster_path}/heatwave-dictionary_{date_str}.pck"
        with open(dict_file, 'rb') as f:
            cluster_dict = pickle.load(f)
        
        # 检查count
        count_file = f"{cluster_path}/heatwave-count_{date_str}.pck"
        with open(count_file, 'rb') as f:
            count = pickle.load(f)
        
        print(f"  {date_str}: 形状{mask.shape}, 热浪格点{np.sum(mask > 0)}, 聚类{len(cluster_dict)}, 计数{count}")
        
    except Exception as e:
        print(f"  {date_str}: ❌ 错误 - {e}")

if __name__ == "__main__":
    import numpy as np
    quick_check()

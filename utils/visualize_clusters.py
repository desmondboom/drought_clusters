#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化聚类结果进行验证
"""

import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import glob

def load_sample_data(cluster_path, date_str):
    """加载指定日期的数据"""
    mask_file = f"{cluster_path}/heatwave-mask_{date_str}.pck"
    dict_file = f"{cluster_path}/heatwave-dictionary_{date_str}.pck"
    
    with open(mask_file, 'rb') as f:
        mask = pickle.load(f)
    
    with open(dict_file, 'rb') as f:
        cluster_dict = pickle.load(f)
    
    return mask, cluster_dict

def visualize_heatwave_map(cluster_path, date_str, save_path=None):
    """可视化热浪分布图"""
    
    mask, cluster_dict = load_sample_data(cluster_path, date_str)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # 原始热浪掩膜
    im1 = ax1.imshow(mask, cmap='Reds', origin='lower')
    ax1.set_title(f'热浪掩膜 - {date_str}')
    ax1.set_xlabel('经度索引')
    ax1.set_ylabel('纬度索引')
    plt.colorbar(im1, ax=ax1, label='热浪强度')
    
    # 聚类结果
    cluster_map = np.zeros_like(mask, dtype=float)
    for cluster_id, cluster_info in cluster_dict.items():
        coords = cluster_info.get('coordinates', [])
        for y, x in coords:
            cluster_map[y, x] = cluster_id
    
    im2 = ax2.imshow(cluster_map, cmap='tab20', origin='lower')
    ax2.set_title(f'聚类结果 - {date_str} (共{len(cluster_dict)}个聚类)')
    ax2.set_xlabel('经度索引')
    ax2.set_ylabel('纬度索引')
    plt.colorbar(im2, ax=ax2, label='聚类ID')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"图片已保存到: {save_path}")
    
    plt.show()

def plot_cluster_statistics(cluster_path, save_path=None):
    """绘制聚类统计图表"""
    
    dict_files = glob.glob(f"{cluster_path}/heatwave-dictionary_*.pck")
    
    dates = []
    cluster_counts = []
    total_areas = []
    max_intensities = []
    
    for dict_file in sorted(dict_files):
        date_str = dict_file.split('_')[-1].replace('.pck', '')
        try:
            date_obj = datetime.strptime(date_str, '%Y%m%d')
            dates.append(date_obj)
            
            with open(dict_file, 'rb') as f:
                cluster_dict = pickle.load(f)
            
            cluster_counts.append(len(cluster_dict))
            
            if cluster_dict:
                areas = [info.get('area', 0) for info in cluster_dict.values()]
                intensities = [info.get('intensity', 0) for info in cluster_dict.values()]
                total_areas.append(sum(areas))
                max_intensities.append(max(intensities))
            else:
                total_areas.append(0)
                max_intensities.append(0)
                
        except Exception as e:
            print(f"处理文件 {dict_file} 时出错: {e}")
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    # 聚类数量时间序列
    ax1.plot(dates, cluster_counts, 'b-', linewidth=1)
    ax1.set_title('每日聚类数量')
    ax1.set_xlabel('日期')
    ax1.set_ylabel('聚类数量')
    ax1.grid(True, alpha=0.3)
    
    # 总热浪面积时间序列
    ax2.plot(dates, total_areas, 'r-', linewidth=1)
    ax2.set_title('每日总热浪面积')
    ax2.set_xlabel('日期')
    ax2.set_ylabel('面积 (km²)')
    ax2.grid(True, alpha=0.3)
    
    # 最大强度时间序列
    ax3.plot(dates, max_intensities, 'g-', linewidth=1)
    ax3.set_title('每日最大聚类强度')
    ax3.set_xlabel('日期')
    ax3.set_ylabel('强度')
    ax3.grid(True, alpha=0.3)
    
    # 聚类数量分布直方图
    ax4.hist(cluster_counts, bins=20, alpha=0.7, color='purple')
    ax4.set_title('聚类数量分布')
    ax4.set_xlabel('每日聚类数量')
    ax4.set_ylabel('频次')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"统计图已保存到: {save_path}")
    
    plt.show()

def check_specific_date(cluster_path, date_str):
    """检查特定日期的详细信息"""
    
    print(f"=== 检查日期: {date_str} ===")
    
    mask, cluster_dict = load_sample_data(cluster_path, date_str)
    
    print(f"热浪掩膜形状: {mask.shape}")
    print(f"热浪格点数: {np.sum(mask > 0)}")
    print(f"总格点数: {mask.size}")
    print(f"热浪比例: {np.sum(mask > 0) / mask.size * 100:.2f}%")
    print(f"聚类数量: {len(cluster_dict)}")
    
    if cluster_dict:
        print(f"\n聚类详情:")
        for i, (cluster_id, info) in enumerate(cluster_dict.items()):
            print(f"  聚类 {cluster_id}:")
            print(f"    面积: {info.get('area', 'N/A')} km²")
            print(f"    强度: {info.get('intensity', 'N/A')}")
            print(f"    质心: {info.get('centroid', 'N/A')}")
            print(f"    格点数: {len(info.get('coordinates', []))}")
            if i >= 4:  # 只显示前5个
                print(f"    ... (还有 {len(cluster_dict) - 5} 个聚类)")
                break

if __name__ == "__main__":
    cluster_path = "./clusters_output/ERA5/China/heatwave/90p"
    
    if not os.path.exists(cluster_path):
        print(f"错误: 路径不存在 {cluster_path}")
        exit(1)
    
    # 获取一些样本日期
    mask_files = glob.glob(f"{cluster_path}/heatwave-mask_*.pck")
    sample_dates = [f.split('_')[-1].replace('.pck', '') for f in mask_files[::len(mask_files)//5]]
    
    print("=== 样本日期检查 ===")
    for date_str in sample_dates[:3]:  # 检查前3个样本
        check_specific_date(cluster_path, date_str)
        print()
    
    # 可视化第一个样本
    if sample_dates:
        print(f"=== 可视化样本: {sample_dates[0]} ===")
        visualize_heatwave_map(cluster_path, sample_dates[0])
        
        print(f"=== 绘制统计图表 ===")
        plot_cluster_statistics(cluster_path)

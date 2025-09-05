#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试连续3天筛选功能
"""

import numpy as np

def find_consecutive_periods(time_series, min_length):
    """
    找到时间序列中连续1的段落，长度至少为min_length
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

def test_consecutive_filter():
    """测试连续3天筛选功能"""
    
    print("=== 测试连续3天筛选功能 ===")
    
    # 测试用例1：包含连续3天的情况
    test_case1 = np.array([0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0])
    print(f"\n测试用例1: {test_case1}")
    periods1 = find_consecutive_periods(test_case1, 3)
    print(f"连续≥3天的期段: {periods1}")
    
    # 测试用例2：只有1-2天的情况
    test_case2 = np.array([0, 1, 1, 0, 1, 0, 1, 1, 0])
    print(f"\n测试用例2: {test_case2}")
    periods2 = find_consecutive_periods(test_case2, 3)
    print(f"连续≥3天的期段: {periods2}")
    
    # 测试用例3：边界情况
    test_case3 = np.array([1, 1, 1, 0, 0, 1, 1, 1, 1, 1])
    print(f"\n测试用例3: {test_case3}")
    periods3 = find_consecutive_periods(test_case3, 3)
    print(f"连续≥3天的期段: {periods3}")
    
    # 测试用例4：全为1的情况
    test_case4 = np.array([1, 1, 1, 1, 1])
    print(f"\n测试用例4: {test_case4}")
    periods4 = find_consecutive_periods(test_case4, 3)
    print(f"连续≥3天的期段: {periods4}")
    
    # 测试用例5：全为0的情况
    test_case5 = np.array([0, 0, 0, 0, 0])
    print(f"\n测试用例5: {test_case5}")
    periods5 = find_consecutive_periods(test_case5, 3)
    print(f"连续≥3天的期段: {periods5}")
    
    print(f"\n✅ 连续3天筛选功能测试完成")

if __name__ == "__main__":
    test_consecutive_filter()

# 热浪识别与追踪系统（ERA5 数据版）

本项目是一个基于 ERA5 再分析数据的热浪识别与追踪系统，能够自动识别热浪事件、进行空间聚类分析，并追踪热浪事件在时间维度上的演化过程。

## 🌟 主要功能

- **动态阈值计算**：基于历史同期数据计算 90 百分位动态阈值
- **连续 3 天筛选**：确保热浪事件至少持续 3 天，符合气象学定义
- **空间聚类识别**：识别空间上连续的热浪区域
- **时间事件追踪**：追踪热浪事件在时间维度上的演化
- **跨年边界处理**：避免将不同年份的热浪事件错误连接
- **并行计算支持**：支持 MPI 并行处理，提高计算效率

## 📁 项目结构

```txt
drought_clusters/
│
├── data/                                    # 数据目录
│   ├── era5_daily_mean_198005-202009_CHINA.nc    # 原始ERA5数据
│   ├── era5_daily_mean_201105-201109_CHINA.nc    # 气候基准期数据
│   └── processed/
│       └── heatwave_processed.nc                  # 预处理后的热浪数据
│
├── clusters_output/                         # 输出目录（自动生成）
│   └── ERA5/China/heatwave/90p/
│       ├── heatwave-dictionary_*.pck       # 每日聚类字典文件
│       ├── heatwave-mask_*.pck             # 每日热浪掩膜文件
│       ├── heatwave-count_*.pck            # 每日聚类数量文件
│       └── result/
│           └── tracked_clusters_dictionary_2011-2020.pck  # 最终追踪结果
│
├── src/                                     # 源代码目录
│   ├── 01_data_preprocessing.py            # 数据预处理脚本
│   ├── 02_calculate_heatwave_clusters_parallel.py  # 热浪聚类识别（并行）
│   ├── 03_process_heatwave_clusters.py     # 热浪事件追踪
│   ├── heatwave_clusters_utils.py          # 热浪聚类工具函数
│   └── definitions.yaml                    # 配置文件
│
├── environment.yaml                        # Conda环境配置
├── LICENSE                                 # 许可证文件
└── README.md                              # 项目说明文档
```

## 🚀 快速开始

### 1. 环境配置

确保已安装 Miniconda 或 Anaconda，然后创建项目环境：

```bash
conda env create -f environment.yaml
conda activate heatwave
```

### 2. 数据准备

将 ERA5 数据文件放置在 `data/` 目录下：

- **主数据文件**：`era5_daily_mean_198005-202009_CHINA.nc`（1980-2020 年完整数据）
- **气候基准文件**：`era5_daily_mean_201105-201109_CHINA.nc`（2011-2019 年 5-9 月数据，用于计算阈值）

确保 NetCDF 文件包含以下变量：

- `t2m`：2 米气温（单位：开尔文）
- `lat`：纬度
- `lon`：经度
- `time`：时间

### 3. 配置参数

编辑 `src/definitions.yaml` 文件，根据需要调整参数：

```yaml
# 数据集信息
dataset: ERA5
region: China

# 热浪定义
drought_metric: heatwave
drought_threshold: 90p # 90百分位阈值

# 输入文件路径
drought_metric_path: ./data/processed/
drought_metric_file_name: heatwave_processed.nc

# 变量名称
lat_var: lat
lon_var: lon

# 时间范围
start_year: 2011
end_year: 2020

# 聚类参数
minimum_area_threshold: 100 # 最小面积阈值（km²）
periodic_bool: False # 是否周期性边界

# 输出路径
clusters_partial_path: ./clusters_output
```

## 🔧 使用步骤

### 步骤 1：数据预处理

```bash
python src/01_data_preprocessing.py
```

**功能说明：**

- 计算实际温度 `T_actual`
- 基于历史同期数据计算 90 百分位动态阈值 `T_threshold`
- 生成二值热浪掩膜 `heatwave_mask`
- 应用连续 3 天筛选，确保热浪事件至少持续 3 天
- 输出处理后的 NetCDF 文件：`data/processed/heatwave_processed.nc`

**输出示例：**

```
应用连续3天筛选...
处理 201 x 161 = 32361 个格点...
已处理 10000/32361 个格点 (30.9%)
已处理 20000/32361 个格点 (61.8%)
已处理 30000/32361 个格点 (92.7%)
原始热浪格点总数: 1234567
筛选后热浪格点总数: 987654
保留比例: 80.00%
处理完成，数据保存为：./data/processed/heatwave_processed.nc
```

### 步骤 2：热浪聚类识别（并行）

```bash
mpirun -np 4 python src/02_calculate_heatwave_clusters_parallel.py
```

**功能说明：**

- 对每个时间步进行空间聚类分析
- 识别空间上连续的热浪区域
- 计算聚类面积、强度、质心等特征
- 过滤小于面积阈值的聚类
- 支持 MPI 并行计算

**参数说明：**

- `-np 4`：使用 4 个 CPU 核心（可根据系统配置调整）

**输出示例：**

```
[Rank 0] 1/378 | global 1/1510 | date 20110501: heatwave pixels = 1234
[Rank 0] saved 20110501 | clusters=5 | step=2.34s
[Rank 1] 1/378 | global 2/1510 | date 20110502: heatwave pixels = 987
[Rank 1] saved 20110502 | clusters=3 | step=1.89s
...
```

### 步骤 3：热浪事件追踪

```bash
python src/03_process_heatwave_clusters.py
```

**功能说明：**

- 遍历所有时间步的聚类数据
- 基于空间重叠度追踪热浪事件
- 处理跨年边界，避免错误连接
- 计算事件持续时间、最大面积、总强度等特征
- 生成最终的热浪事件字典

**输出示例：**

```
📅 实际聚类文件日期范围: 2011-05-01 到 2020-09-30
📊 实际文件数量: 1510
开始追踪热浪事件...
🔍 搜索路径: ./clusters_output/ERA5/China/heatwave/90p
🔍 找到文件数量: 1510
📊 成功解析日期的文件数量: 1510
📊 找到 1510 个聚类文件
处理进度: 1/1510 - 2011-05-01
处理进度: 101/1510 - 2011-08-09
...
边界重置: 2012-05-01
边界重置: 2013-05-01
...
✅ 共识别热浪事件数：74278
✅ 热浪追踪数据保存至：./clusters_output/ERA5/China/heatwave/90p/result/tracked_clusters_dictionary_2011-2020.pck
✅ Done tracking heatwave clusters.
```

## 📊 输出结果

### 中间文件

每个时间步生成三个文件：

- `heatwave-dictionary_YYYYMMDD.pck`：聚类特征字典
- `heatwave-mask_YYYYMMDD.pck`：热浪掩膜矩阵
- `heatwave-count_YYYYMMDD.pck`：聚类数量

### 最终结果

`tracked_clusters_dictionary_2011-2020.pck` 包含所有热浪事件的完整信息：

```python
{
    0: {
        "start": datetime(2011, 5, 1),
        "end": datetime(2011, 5, 2),
        "duration": 2,                    # 持续时间（天）
        "total_intensity": -2325356.61,   # 总强度
        "max_area": 1041331,             # 最大面积（km²）
        "centroid_trajectory": {         # 质心轨迹
            datetime(2011, 5, 1): (lon, lat),
            datetime(2011, 5, 2): (lon, lat)
        },
        "daily_coordinates": {           # 每日格点坐标
            datetime(2011, 5, 1): [(y1, x1), (y2, x2), ...],
            datetime(2011, 5, 2): [(y1, x1), (y2, x2), ...]
        }
    },
    # ... 更多事件
}
```

## 🔍 结果验证

### 基本统计

```python
import pickle

# 加载结果
with open('clusters_output/ERA5/China/heatwave/90p/result/tracked_clusters_dictionary_2011-2020.pck', 'rb') as f:
    events = pickle.load(f)

print(f"总事件数量: {len(events):,}")
print(f"平均持续时间: {np.mean([e['duration'] for e in events.values()]):.1f} 天")
print(f"最大面积: {max([e['max_area'] for e in events.values()]):,.0f} km²")
```

### 年度统计

```python
# 按年度统计
yearly_events = {}
for event in events.values():
    year = event['start'].year
    yearly_events[year] = yearly_events.get(year, 0) + 1

for year in sorted(yearly_events.keys()):
    print(f"{year}: {yearly_events[year]:,} 个热浪事件")
```

## ⚙️ 配置参数说明

### 关键参数

| 参数                     | 说明                | 推荐值    | 影响                                     |
| ------------------------ | ------------------- | --------- | ---------------------------------------- |
| `minimum_area_threshold` | 最小面积阈值（km²） | 100-1000  | 过滤小尺度噪声，值越大事件越少           |
| `drought_threshold`      | 百分位阈值          | 90p       | 热浪定义标准，90p 表示超过 90%的历史同期 |
| `start_year/end_year`    | 分析时间范围        | 2011-2020 | 数据覆盖的时间段                         |

### 性能优化

- **并行核心数**：根据 CPU 核心数调整 `-np` 参数
- **内存使用**：大数据集建议增加系统内存
- **存储空间**：确保有足够磁盘空间存储中间文件

## 🐛 常见问题

### 1. MPI 错误

**问题**：`Fatal error in MPI_Init_thread: gethostbyname failed`

**解决**：使用 `-host localhost` 参数

```bash
mpirun -host localhost -np 4 python src/02_calculate_heatwave_clusters_parallel.py
```

### 2. 内存不足

**问题**：处理大数据集时内存溢出

**解决**：

- 减少并行核心数
- 增加系统内存
- 考虑分时段处理

### 3. 文件路径错误

**问题**：找不到输入文件

**解决**：

- 检查 `definitions.yaml` 中的路径配置
- 确保数据文件存在且可读
- 使用绝对路径避免相对路径问题

## 📈 性能指标

基于中国区域 ERA5 数据（2011-2020 年）的典型性能：

- **数据规模**：201×161 格点，1510 个时间步
- **处理时间**：约 2-4 小时（4 核心并行）
- **输出事件**：约 7 万个热浪事件
- **存储需求**：约 500MB 中间文件 + 200MB 最终结果

## 📚 技术细节

### 热浪定义

1. **温度阈值**：日平均温度超过历史同期 90 百分位
2. **持续时间**：至少连续 3 天
3. **空间连续性**：相邻格点温度均超过阈值

### 聚类算法

- 基于 8 邻域连通性分析
- 使用加权质心计算聚类中心
- 考虑地球曲率的面积计算

### 追踪算法

- 基于空间重叠度的事件匹配
- 跨年边界自动重置
- 支持事件分裂和合并

## 📄 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

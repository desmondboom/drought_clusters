# 热浪识别项目使用手册（ERA5 数据版）

本项目包含三个步骤，依次完成气象数据处理、热浪事件识别与聚类追踪。以下为详细操作说明：

---

## 目录结构

```
project-root/
│
├── data/                          # 存放 ERA5 原始数据的文件夹
│   └── ERA5_temperature.nc        # 示例：含有 t2m（2米气温）的 NetCDF 文件
│
├── clusters_output/               # 脚本运行后自动生成的输出文件夹（不用提前创建）
│
├── environment.yaml              # Conda 环境配置文件
│
├── definitions.yaml              # 项目运行配置（如数据集名、阈值、保存路径等）
│
├── src/                          # 所有 Python 脚本
│   ├── 01_data_preprocessing.py
│   ├── 02_calculate_drought_clusters_parallel.py
│   ├── 03_process_drought_clusters.py
│   └── drought_clusters_utils.py
│
└── README.md
```

---

## 第一步：创建 Conda 环境

确保你已安装 Miniconda 或 Anaconda。

```bash
conda env create -f environment.yaml
conda activate heatwave
```

---

## 第二步：放置原始 ERA5 数据

将 NetCDF 数据（包含 `t2m`、`lat`、`lon`、`time` 四个变量）放入 `./data` 文件夹，例如：

```
./data/era5_daily_mean_198005-202009_CHINA.nc
```

你需要将该路径配置到 `src/01_data_preprocessing.py` 的如下变量中：

```python
file_path = "./data/era5_daily_mean_198005-202009_CHINA.nc"
```

---

## 第三步：运行 01 处理数据

执行命令：

```bash
python ./src/01_data_preprocessing.py
```

功能：

* 计算实际温度 `T_actual`
* 基于 90 分位数计算动态阈值 `T_threshold`
* 生成热浪掩膜 `heatwave_mask`
* 输出保存为 NetCDF 文件 `heatwave_processed.nc`

---

## 第四步：运行 02 聚类识别（支持并行）

使用 `mpirun` 命令并行执行热浪聚类识别：

```bash
mpirun -np 4 python ./src/02_calculate_drought_clusters_parallel.py
```

说明：

* `-np 4` 表示使用 4 个核心进行并行处理
* 如果出错请检查是否正确安装了 `mpi4py`，并且 `openmpi` 已正确配置

输出：

* 每个时间点的热浪聚类数据将以 `.pck` 格式保存在：

  ```
  ./clusters_output/{dataset}/{region}/{drought_metric}/{drought_threshold}/
  ```

---

## 第五步：运行 03 聚类追踪

执行命令：

```bash
python ./src/03_process_drought_clusters.py
```

功能：

* 遍历每个时间点的聚类数据
* 追踪跨天的热浪事件
* 生成并保存最终结果字典：

  ```
  ./clusters_output/.../result/tracked_clusters_dictionary_2011-2020.pck
  ```

---

## 📌 常见配置说明（definitions.yaml）

```yaml
dataset: ERA5
region: China
drought_metric: heatwave
drought_metric_path: ./  # heatwave_processed.nc 的目录
drought_metric_file_name: heatwave_processed.nc
lat_var: lat
lon_var: lon
metric_var: percentiles
start_year: 2011
end_year: 2020
drought_threshold: 0.9
minimum_area_threshold: 10000
periodic_bool: False
clusters_partial_path: ./clusters_output
```

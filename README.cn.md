_[:us:](https://github.com/AureClai/stream-python/blob/master/README.md)_ _[:fr:](https://github.com/AureClai/stream-python/blob/master/README.fr.md)_ _[:es:](https://github.com/AureClai/stream-python/blob/master/README.es.md)_ _[:cn:](https://github.com/AureClai/stream-python/blob/master/README.cn.md)_
_[:jp:](https://github.com/AureClai/stream-python/blob/master/README.jp.md)_ _[:portugal:](https://github.com/AureClai/stream-python/blob/master/README.pt.md)_

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)
[![Open Source? Yes!](https://badgen.net/badge/Open%20Source%20%3F/Yes%21/blue?icon=github)](https://github.com/Naereen/badges/)
[![Join the chat at https://gitter.im/FaradayRF/Lobby](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/stream-python/community)

<p align="center">
  <img src="https://github.com/AureClai/stream-python/blob/master/img/logo_plus_name.png" width=256 height=256/>
</p>

<h1 align="center">开源事件驱动的中观交通流模拟器</h1>

## Stream是什么？

Stream是一种中观交通流模拟工具，即分辨率介于微观和宏观水平之间的工具。它考虑的是车辆而非流量，但只计算车辆经过路网节点的时间，而不是以固定时间间隔计算所有位置。这种解决方法的优点是：(i)相比于微观水平，计算时间大大缩短，(ii)参数数量减少且具有明确的物理意义，比微观水平更容易进行参数设定，(iii)用例种类多样，比宏观水平的限制要少得多。

## 主要特性

- 事件驱动的中观计算核心
- 预先和最短路径的**静态**分配
- 有限的*不同车辆类别管理
- 复杂节点管理
- 信号交叉口管理
- 特定车道管理（预留和辅助车道）
- 模拟过程中的动态调控

## 联系方式

主要贡献者为Cerema的东部地区部门。如有问题，请发送邮件至以下地址：aurelien.clairais@cerema.fr

## 安装

Stream在[Anaconda](https://www.anaconda.com/distribution/)环境下的Python 3.9上运行良好。我们推荐使用Anaconda的[虚拟环境](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)：

```console
$ conda create --name myenv
$ conda activate myenv
```

安装步骤是先克隆仓库，然后用`pip`安装包。

### 1. 克隆仓库

```console
$ git clone https://github.com/AureClai/stream-python
$ cd stream-python
```

### 2. _(可选)_ 切换分支（如果在_master_分支以外的分支上开发）

```console
$ git checkout la_branche
```

### 3. 安装

```console
$ pip install .
```

## 使用方式

### 命令行使用

```console
$ stream -i file_of_inputs.npy
```

从这一步开始，一个名为`result`的新文件夹已经在包含输入文件的文件夹中创建，包含模拟结果，时间和日期以`.npy`格式保存。如果指定了结果文件夹（参见命令行的`stream --help`），结果将保存在该文件夹中。

### 通过python脚本使用

```python
from stream.main import run_simulation_from_inputs
import numpy as np

# 导入输入文件
Inputs = np.load("chemin_vers_le_fichier_inputs.npy", allow_pickle=True).item()
Simulation = run_simulation_from_inputs(Inputs)
```

在这里，结果以字典的形式在`Simulation`变量中创建。

### 通过图形用户界面使用

```console
$ stream-gui
```

## 使用QStream设计场景

QGIS扩展[https://gitlab.cerema.fr/Stream/qstream](https://gitlab.cerema.fr/Stream/qstream) 允许：

- 场景定义
- 分析功能

## Bug报告

未知的bugs。如果您发现一个bug，请开启一个["_issue_"](https://github.com/AureClai/stream-python/issues/new)。

## 许可证

[Cecill-B](http://www.cecill.info/licences/Licence_CeCILL-B_V1-fr.html)。

## 待办事项

1. 使用Plotly的`dash`库实现可视化工具
2. 网络输出的可变容量管理
3. 多种分配方式
4. 动态速度调控
5. 接入调控
6. 其他类型的输入/输出格式管理


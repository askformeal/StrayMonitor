# StrayMonitor

一个基于Python的系统监控工具，提供CPU和内存使用情况的实时监控功能。通过系统托盘图标展示资源使用率，并支持阈值颜色提示。

## 功能特性
- 实时监控CPU和内存使用率
- 系统托盘图标显示
- 颜色编码的阈值警告（绿色-正常，橙色-中等，红色-高负载）
- 支持查看详细的系统信息弹窗

## 安装依赖
```bash
pip install -r requirements.txt
```

## 使用说明
1. 直接运行主程序：
   ```bash
   python app.py
   ```
2. 可指定监控类型：
   ```bash
   python app.py cpu   # 只监控CPU
   python app.py mem   # 只监控内存
   python app.py both  # 同时监控CPU和内存（默认）
   ```

## 配置选项
在`src/settings.py`中可配置以下参数：
- 图标尺寸和颜色方案
- 日志级别和存储路径
- 资源使用阈值
- 界面显示参数

## 开发者信息
项目使用了以下主要技术：
- `psutil`：系统信息采集
- `pystray`：系统托盘图标实现
- `PIL`：图像生成与处理
- `loguru`：日志记录

## 许可证
本项目遵循MIT许可证，详细信息请参见LICENSE文件。
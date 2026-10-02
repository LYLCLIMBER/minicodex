# 修复文件路径错误

修复 `app/report.py` 读取数据文件时对启动目录的依赖。无论从工作区根目录运行 `python app/report.py`，还是从 `app/` 目录运行 `python report.py`，都应读取同一份 `app/data/metrics.json` 并输出正确的结果。不要修改数据文件。

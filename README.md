# Simplified Aircraft Engine Health Monitor

这是一个面试用的简化航空发动机实时监测项目。仓库只有 10 个文件，不保存训练过程、中间矩阵或重复结果。

`data.csv` 是从 NASA N-CMAPSS DS02-006 中提取的 unit 5 连续 12,000 个 `health_state=1` 健康样本，采样率为 1 Hz。目标是 T50，输入为 31 个工况、传感器和虚拟传感器变量。温度已统一转换为摄氏度。

五个模块：

1. `module1_data.py`：检查非数值、重复和孤立毛刺，再按时间顺序划分 40%/30%/30%；不会因为模型误差删除 NASA 已标记的健康工况。
2. `module2_baseline.py`：只用前 40% 训练 ElasticNet，计算非负绝对残差和单边 10-SD 边界。
3. `module3_kalman.py`：在中间 30% 上注入多种渐进故障，训练 A/B/C、偏置、Q/R；每秒只更新状态和 P，并直接外推最多 600 个一秒采样步。
4. `module4_root_cause.py`：在第一个报警点比较标准化传感器变化，定位根因。
5. `module5_adjustment.py`：验证人工监督下返回故障前参考状态，不发送控制命令。

运行：

```powershell
pip install -r requirements.txt
./run_all.ps1
```

每个模块的简要验证结果直接打印到终端。故障测试使用 10、30、100、300、600 个采样步；航空数据是 1 Hz，因此也分别等于 10–600 秒。报警要求残差连续两个采样点上升并且 Kalman 外推会在 600 秒内越界，所以红点应在故障开始后约 2–5 秒出现。唯一保留的结果文件是 `residual_alarm.png`。

人工故障、统计边界和调整仅用于简化演示，不是 NASA 提供的真实故障响应或发动机控制指令。

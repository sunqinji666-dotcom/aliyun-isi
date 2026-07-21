# Aliyun Bailian ASR Pricing

Last verified: **2026-04-11**
Source: https://help.aliyun.com/zh/model-studio/model-pricing

> 统一计费规则：按输入音频的秒数计费，输出文本不计费。
> 请求失败不产生费用，也不消耗免费额度。

---

## Paraformer Series（仅中国内地）

### 录音文件识别（我们最常用的）

| 模型版本 | 单价 |
|----------|------|
| `paraformer-v2` | **0.00008 元/秒**（≈ 0.29 元/小时） |
| `paraformer-8k-v2` | 同上 |
| `paraformer-v1` | 同上 |
| `paraformer-8k-v1` | 同上 |
| `paraformer-mtl-v1` | 同上 |

### 实时语音识别

| 模型版本 | 单价 |
|----------|------|
| `paraformer-realtime-v2` | **0.00024 元/秒**（≈ 0.86 元/小时） |
| `paraformer-realtime-v1` | 同上 |

---

## Fun-ASR Series

| 类型 | 模型 | 中国内地 | 国际 |
|------|------|---------|------|
| 录音文件识别 | `fun-asr` 系列 | 0.00022 元/秒 | 0.00026 元/秒 |
| 实时语音识别 | `fun-asr-realtime` 系列 | 0.00033 元/秒 | 0.00066 元/秒 |
| 实时语音识别 | `fun-asr-flash-8k-realtime` | 0.00022 元/秒 | 无 |

---

## 千问 ASR

| 类型 | 模型 | 中国内地 | 国际/美国 |
|------|------|---------|----------|
| 录音文件识别 | `qwen3-asr-flash-filetrans` | 0.00022 元/秒 | 0.00026 元/秒 |
| 录音文件识别 | `qwen3-asr-flash-us`（美国） | - | 0.000035 元/秒 |
| 实时语音识别 | `qwen3-asr-flash-realtime` | 0.00033 元/秒 | 0.00066 元/秒 |

---

## 其他模型

| 模型 | 类型 | 中国内地单价 |
|------|------|-------------|
| GUMMY（实时/对话） | `gummy-realtime-v1` | 0.00015 元/秒 |
| SenseVoice | `sensevoice-v1`（录音文件） | 0.0007 元/秒 |

---

## Cost Reference for Planning

### 录音文件识别（Paraformer）速查

| 时长 | 费用 |
|------|------|
| 1 分钟 | 0.005 元 |
| 5 分钟 | 0.024 元 |
| 15 分钟 | 0.072 元 |
| 30 分钟 | 0.144 元 |
| 1 小时 | 0.288 元 |
| 2 小时 | 0.576 元 |
| 4 小时 | 1.152 元 |

### OSS 费用（标准按量）

| 项目 | 费用 |
|------|------|
| 存储 | 0.12 元/GB/月（≈ 0.02 元/月/189MB） |
| 上传流量 | **免费**（外网传入） |
| 内网流出 | **免费**（同区域 Paraformer 读取） |
| PUT 请求 | 0.01 元/万次 |
| 删除 | 无额外费用 |

### 实际案例

2026-04-11 转录 8 个 Seedance 教程：
- 总音频时长：~2.3 小时（~8,220 秒）
- 总文件大小：~189 MB
- Paraformer 费用：0.66 元
- OSS 费用：~0.02 元（存储费，上传免费）
- 总耗时：~6 分钟
- **实际花费：约 0.68 元**

---

## Notes

- Paraformer 录音文件识别是最便宜的路线（0.00008 元/秒）
- Fun-ASR 比 Paraformer 贵约 2.75 倍
- SenseVoice 比 Paraformer 贵约 8.75 倍
- 如果文件已在 OSS 上，直接用 `transcribe_paraformer_url.py` 最省
- 本地文件走 `transcribe_paraformer_local.py` 自动上传 OSS → Paraformer → 可选清理
- 所有模型按量计费，请求失败不产生费用

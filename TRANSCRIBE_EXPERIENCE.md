# 音频转录实战 - 问题总结与经验教训

> 日期：2026-04-11
> 项目：爱戏剧的柏拉图（319视频）+ 恋爱脱单实战课（19视频）+ 恋爱成长课（37视频）
> 总计：375 个文件，100% 转录完成

---

## 一、费用失控问题（最严重）

### 问题
- 实际转录 374 个文件，但 API 调用了 **1,881 次**
- 多花了约 **5 倍的钱**（¥57 vs 应该的 ~¥12）
- 原因：多个进程同时运行，重复转录同一文件

### 根因
1. `download_and_transcribe.sh` 在转录
2. `batch_transcribe_paraformer_folder.py` 也在转录同一个文件夹
3. `daemon.sh` 守护进程又启动了一个转录
4. 手动启动的转录也在跑
5. **4 个进程同时扫同一个文件夹，都提交 API**

### 修复
- **只保留一个守护进程**（daemon.sh），严格检查是否已有转录进程在运行
- 使用 `batch_transcribe_paraformer_folder.py` 自带的跳过逻辑（`--force-rerun` 默认不重复）
- 确保 `is_transcribe_running()` 严格匹配，排除自身进程

### 教训
> **同一时间只能有一个转录进程运行！** 任何批量处理脚本都必须：
> 1. 启动前检查是否已有同类进程在运行
> 2. 跳过已完成的文件（检查 .txt 是否存在）
> 3. 不要用多个脚本同时处理同一个目录

---

## 二、Cookies 格式问题

### 问题
- 直接粘贴 cookies 字符串到文件，yt-dlp 无法识别
- 报错：`does not look like a Netscape format cookies file`

### 修复
- 必须转换为 **Netscape HTTP Cookie File** 格式
- 每行一个 cookie，格式：`domain flag path secure expiration name value`

### 教训
> yt-dlp 只支持 Netscape 格式的 cookies 文件，不接受浏览器导出的原始字符串。

---

## 三、视频标题为 NA 问题

### 问题
- B 站空间视频接口 `--flat-playlist` 不返回标题，`%(title)s` 全部为 `NA`
- 下载的音频文件全部命名为 `NA.mp3`，无法区分

### 修复
- 使用 yt-dlp 的 `--output "%(title)s.%(ext)s"` 在下载时自动获取标题
- 或者先用 `--print "%(id)s|%(url)s"` 获取链接，再逐个下载时获取标题

---

## 四、非 MP3 格式遗漏

### 问题
- 音频目录里有 319 个文件，但转录只有 318 个
- 缺失的那个是 `.m4a` 格式（`从i人变社牛：如何迅速和人拉近关系.m4a`）
- 转录脚本的 `iter_audio_files()` 默认支持 `.mp3, .wav, .mp4, .aac, .opus, .m4a`
- 但之前的自定义脚本只扫描了 `.mp3`

### 教训
> 扫描音频文件时，必须包含所有支持的格式，不要只检查 `.mp3`

---

## 五、监控页面看不到数据

### 问题
- 直接双击打开 `monitor.html` 本地文件，fetch API 被 CORS 阻止
- 必须通过 HTTP 服务器访问

### 修复
- 启动 Python HTTP 服务器：`python3 server.py`
- 通过 `http://localhost:9988/monitor.html` 访问

---

## 六、文件清理问题

### 问题
- 转录脚本默认生成 `.txt` + `.json` 两个文件
- `.json` 文件包含完整 API 响应（调试用），日常使用不需要
- 守护进程重启后会重新生成 `.json` 文件

### 修复
- 确认所有转录完成后，批量删除所有 `.json` 文件
- 关闭守护进程，防止自动重新生成

---

## 七、最终文件结构（推荐）

```
项目目录/
├── 音频文件/          # .mp3 / .m4a / .mp4 原始音频
├── 转录结果/          # 只保留 .txt 纯文本
└── 分类说明.md        # 项目说明（可选）
```

**不需要保留的文件：**
- `.json` - API 原始响应
- `.sh` - 临时脚本
- `.log` - 运行日志
- `monitor.html` / `server.py` - 监控工具
- `video_list.txt` - 视频列表缓存

---

## 八、最优转录流程（下次直接用这个）

```bash
# 1. 一次性批量转录（有跳过逻辑，不会重复）
cd .
source .venv/bin/activate
python3 scripts/batch_transcribe_paraformer_folder.py \
    <音频目录> \
    --out-dir <转录结果目录> \
    --json  # 如果需要 JSON 就加，不需要就不加

# 2. 转录完成后清理 JSON（如果不需要）
find <转录结果目录> -name "*.json" -delete

# 3. 检查结果
ls <转录结果目录>/*.txt | wc -l
ls <音频目录>/*.mp3 <音频目录>/*.m4a <音频目录>/*.mp4 | wc -l
# 两个数字应该一致
```

---

## 九、费用参考

| 项目 | 数量 | 费用 |
|------|------|------|
| 实际转录 | 374 个文件 | ~¥14.51 |
| 重复转录 | 1,507 次 | ~¥42.49 |
| 总计 | 1,881 次 | ~¥57.00 |
| OSS | 临时存储 | ≈ ¥0 |
| **如果只转录一次** | 374 个 | **~¥14.51** |

---

## 十、关键脚本说明

| 脚本 | 用途 | 注意 |
|------|------|------|
| `batch_transcribe_paraformer_folder.py` | 批量转录文件夹 | 有跳过逻辑，安全 |
| `transcribe_paraformer_local.py` | 单文件转录 | 手动调用，适合补漏 |
| `daemon.sh` | 守护进程（防中断） | 必须严格检查是否有转录进程在运行 |
| `download_and_transcribe.sh` | 下载+转录（B站专用） | 已废弃，不再使用 |

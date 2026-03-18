---
name: tts-indextts2
description: |
  IndexTTS2 文本转语音（TTS）skill。使用 IndexTTS2 模型生成高质量语音，支持情绪控制。
  当用户说"IndexTTS2"、"文字转语音"、"TTS"、"生成语音"时激活。
  支持通过飞书发送语音消息。
---

# IndexTTS2 TTS Skill

本 skill 使用 IndexTTS2 模型将文本转换为高质量语音，支持情绪控制，可直接发送飞书语音消息。

## 特性

- ✅ 高质量语音合成（IndexTTS2 模型）
- ✅ 支持情绪控制（快乐、平静、悲伤、兴奋）
- ✅ 支持飞书语音消息发送
- ✅ 自动回退到 macOS say（当模型不可用时）
- ✅ 本地离线运行（无需 API Key）

## 快速开始

### 1. 环境准备

```bash
# 激活 Conda 环境
conda activate indextts2_fixed

# 测试模型
cd ~/Documents/skills/tts-indextts2
python test_final.py
```

### 2. 生成语音

```bash
# 使用 run.sh 脚本
bash run.sh "你好，这是测试语音"

# 指定输出文件
bash run.sh "Hello World" -o output.wav
```

### 3. 发送飞书语音

```bash
# 激活环境
conda activate indextts2_fixed

# 基本用法（中性情绪）
python3 send_voice.py "你好，我是语音助手" "ou_xxx"

# 快乐情绪
python3 send_voice.py "太棒了！今天真是美好的一天！" "ou_xxx" --happy

# 平静情绪
python3 send_voice.py "你好，这是参考音频。" "ou_xxx" --calm

# 使用自定义参考音频
python3 send_voice.py "文本内容" "ou_xxx" --ref /path/to/ref.wav
```

**注意**：如果遇到 `open_id cross app` 错误，请使用 OpenClaw message 工具发送：

```bash
openclaw message send --asVoice --media output_voice.opus "语音消息"
```

## 使用方法

### 方法 1：命令行脚本

```bash
# 激活环境
conda activate indextts2_fixed

# 生成语音
bash ~/Documents/skills/tts-indextts2/run.sh "要转换的文本"

# 发送飞书语音
python3 ~/Documents/skills/tts-indextts2/send_voice.py "文本" "接收者ID" --happy
```

### 方法 2：Python API

```python
import sys
sys.path.insert(0, "~/Documents/skills/tts-indextts2/index-tts")

from indextts.infer import IndexTTS

# 初始化
tts = IndexTTS(
    cfg_path="checkpoints/config.yaml",
    model_dir="checkpoints",
    is_fp16=False,
    device="cpu"
)

# 合成语音
tts.infer(
    text="你好，这是测试语音",
    audio_prompt="reference.wav",
    output_path="output.wav"
)
```

### 方法 3：使用 tts_synth.py（多引擎支持）

```bash
python3 tts_synth.py "文本内容" output.wav
```

自动尝试以下引擎：
1. IndexTTS2
2. Piper TTS
3. eSpeak
4. macOS say

## 情绪控制

IndexTTS2 支持通过参考音频控制语音情绪：

| 情绪 | 参数 | 参考文本 |
|------|------|----------|
| 快乐 | `--happy` | "太棒了！今天真是美好的一天！" |
| 平静 | `--calm` | "你好，这是参考音频。" |
| 悲伤 | `--sad` | "唉，今天心情不太好。" |
| 兴奋 | `--excited` | "哇！太令人兴奋了！" |
| 中性 | (默认) | "你好，这是参考音频。" |

## 飞书语音发送

### 配置

编辑 `send_voice.py` 修改飞书应用凭证：

```python
FEISHU_APP_ID = "your_app_id"
FEISHU_APP_SECRET = "your_app_secret"
```

### 发送流程

```
文本 → IndexTTS2 → WAV → FFmpeg → OPUS → 飞书上传 → 发送消息
```

### 示例

```bash
# 发送快乐语音
python3 send_voice.py "项目完成了！" "ou_5b77ed9cb458f6ba08563cfcb1b39cc4" --happy

# 发送平静语音
python3 send_voice.py "收到，正在处理。" "ou_xxx" --calm
```

## 性能

**CPU 推理**（Apple Silicon M 系列）：
- RTF（实时率）：约 12-24 倍
- 5 秒音频：约 60 秒生成时间
- 10 秒音频：约 240 秒生成时间

**优化建议**：
- 使用 GPU 加速（如有）
- 控制文本长度（建议 50 字以内）
- 复用参考音频

## 输出格式

- 默认格式：WAV (24kHz, 16bit, 单声道)
- 飞书格式：OPUS (24kbps)
- 支持格式：WAV, M4A, OPUS

## 文件结构

```
~/Documents/skills/tts-indextts2/
├── SKILL.md              # 本文件
├── README.md             # 详细文档
├── send_voice.py         # 飞书语音发送脚本
├── run.sh                # 运行脚本
├── tts_synth.py          # 多引擎合成脚本
├── generate_happy.py     # 快乐情绪生成示例
├── test_final.py         # 完整测试脚本
├── index-tts/            # IndexTTS2 源码
└── checkpoints/          # 模型文件 (3.4GB)
    ├── gpt.pth
    ├── bigvgan_generator.pth
    ├── dvae.pth
    └── ...
```

## 依赖

- Python 3.10
- PyTorch (CPU)
- IndexTTS2
- FFmpeg
- Conda 环境：`indextts2_fixed`

## 故障排除

### 模型加载失败

```bash
# 检查模型文件
ls -lh ~/miniconda3/envs/indextts2/checkpoints/

# 重新激活环境
conda activate indextts2_fixed
```

### 语音生成失败

自动回退到 macOS say：
```bash
# 检查说命令
say -v "Ting-Ting" -o test.m4a "测试"
```

### 飞书发送失败

```bash
# 检查网络代理
curl -x http://127.0.0.1:7890 https://open.feishu.cn

# 检查凭证
python3 -c "from send_voice import get_token; print(get_token())"
```

## 参考资源

- [IndexTTS2 GitHub](https://github.com/iszhanjiawei/indexTTS2)
- [IndexTTS2 HuggingFace](https://huggingface.co/IndexTeam/IndexTTS-1.5)
- [OpenClaw Skills](https://docs.openclaw.ai/skills)
- [飞书开放平台](https://open.feishu.cn/document)

## 许可证

IndexTTS2 模型遵循 Apache License 2.0

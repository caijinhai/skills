# 🎙️ Index-TTS OpenClaw Skill

> 本地离线 TTS 技能，支持中英文语音合成

## 概述

Index-TTS 是一个高质量的本地离线文本转语音（TTS）系统，基于 Index-AN 的开源实现。

## 特性

- ✅ 本地离线运行，无需网络
- ✅ 支持中英文混合
- ✅ 高质量语音输出
- ✅ 可调节语速、音调等参数

## 环境要求

- Python 3.10+
- CUDA 12.1+ (GPU 推荐)
- 至少 8GB 显存

## 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/caijinhai/index-tts.git
cd index-tts
```

### 2. 创建虚拟环境

```bash
python3.10 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install torch==2.1.0 torchvision==0.16.0 --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
```

### 4. 下载模型

模型文件较大，需要单独下载：

```bash
# 方法 1: 从 HuggingFace 下载
git lfs install
git clone https://huggingface.co/lujunhong/index-tts model
```

或使用国内镜像：

```bash
# 方法 2: 从 ModelScope 下载
git clone https://modelscope.cn/models/lujunhong/index-tts.git model
```

### 5. 配置模型路径

编辑 `run.sh` 或 `deploy.sh`，设置模型路径：

```bash
export INDEX_TTS_MODEL_PATH="./model"
```

## 使用方法

### 基础合成

```python
from index_tts import IndexTTS

tts = IndexTTS(model_path="./model")
audio = tts.synthesize("你好，这是一个测试")
audio.save("output.wav")
```

### 使用 WebUI

```bash
python -m index_tts.webui
# 访问 http://localhost:7860
```

### 使用飞书发送语音

本目录包含 `send_voice.py` 脚本，可直接发送语音到飞书：

```bash
# 设置环境变量
export FEISHU_APP_ID="your_app_id"
export FEISHU_APP_SECRET="your_app_secret"

# 发送语音
python3 send_voice.py "要发送的文本" "接收者open_id"
```

## 文件说明

| 文件 | 说明 |
|------|------|
| `index-tts/` | 核心源代码 |
| `run.sh` | 快速运行脚本 |
| `deploy.sh` | 部署脚本 |
| `tts_synth.py` | 合成示例 |
| `send_voice.py` | 飞书语音发送脚本 |

## 常见问题

### Q: 模型下载失败

A: 尝试使用代理或国内镜像：
```bash
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
```

### Q: 显存不足

A: 可以使用 CPU 模式，但速度较慢：
```python
tts = IndexTTS(model_path="./model", device="cpu")
```

### Q: 音频输出异常

A: 确保 FFmpeg 已安装：
```bash
brew install ffmpeg  # macOS
# 或
apt install ffmpeg  # Linux
```

## 参考链接

- [Index-AN/Index-TTS](https://github.com/Index-AN/Index-TTS)
- [ModelScope](https://modelscope.cn/models/lujunhong/index-tts)
- [HuggingFace](https://huggingface.co/lujunhong/index-tts)

## 许可证

MIT License
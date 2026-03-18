# IndexTTS2 TTS Skill

文本转语音（Text-to-Speech）技能，使用 IndexTTS2 模型生成高质量语音。

## 快速开始

### 1. 部署环境（使用代理）

首次使用需要运行部署脚本：

```bash
cd ~/Documents/skills/tts-indextts2
bash deploy_proxy.sh
```

这将：
- 创建 conda 环境 `indextts2`
- 安装必要的 Python 依赖
- 通过代理克隆 IndexTTS2 仓库
- 通过 HuggingFace 镜像下载模型文件
- 创建测试脚本

### 2. 当前状态

✅ **已完成**：
- Conda 环境创建（两个环境）：
  - `indextts2` - 初始环境（有版本冲突）
  - `indextts2_fixed` - 修复后的环境（可用）
- IndexTTS2 代码仓库克隆
- 模型文件下载（约 3.4GB）
- ✅ **语音合成测试成功**！

### 3. 测试结果

**测试信息**：
- 合成文本："你好，这是 IndexTTS 语音合成测试。"
- 输出文件：`test_final_output.wav`
- 时长：5.12 秒
- 采样率：24000Hz
- 总推理时间：59.61 秒（CPU）
- RTF（实时率）：11.64

**性能分解**：
- GPT 生成：51.43 秒
- GPT 前向：0.30 秒
- BigVGAN 声码器：4.13 秒

### 2. 测试语音合成

```bash
# 使用 run.sh 脚本
bash run.sh "你好，这是 IndexTTS2 语音测试"

# 或直接使用 Python
conda activate indextts2
python test_tts.py "你好，测试语音"
```

## 使用方法

### 命令行

```bash
# 基本用法
bash run.sh "要转换的文本"

# 指定输出文件
bash run.sh "Hello World" -o output.wav

# 指定语音类型
bash run.sh "你好" -v zh-CN
```

### Python API

```python
from tts_synth import synthesize_with_indextts2

success = synthesize_with_indextts2(
    text="你好，世界",
    output_path="output.wav",
    voice="zh-CN"
)
```

## 文件说明

```
tts-indextts2/
├── SKILL.md          # Skill 描述文件（OpenClaw 标准）
├── README.md         # 本文件
├── deploy.sh         # 部署脚本
├── run.sh            # 运行脚本
├── tts_synth.py      # 语音合成核心脚本
├── test_tts.py       # 测试脚本
└── models/           # 模型目录（自动创建）
```

## 依赖

- Python 3.8+
- miniconda3 (~/miniconda3)
- PyTorch
- IndexTTS2 模型（或其他备选 TTS 引擎）

## 备选 TTS 引擎

如果 IndexTTS2 模型不可用，脚本会自动尝试以下备选方案：

1. **Piper TTS** - 快速本地 TTS 引擎
2. **eSpeak** - 开源 TTS 引擎
3. **macOS say** - macOS 系统自带 TTS

## 输出格式

- 默认格式：WAV (16kHz, 16bit, 单声道)
- 支持格式：WAV, M4A（取决于使用的引擎）

## 性能

- CPU 推理：实时率 1-5 倍
- GPU 推理：实时率 0.1-0.5 倍（如果支持）

## 故障排除

### 模型下载失败

如果自动下载失败，请手动下载模型并放置到：
```
~/miniconda3/envs/indextts2/models/
```

### Conda 环境问题

```bash
# 重新创建环境
conda env remove -n indextts2
bash deploy.sh
```

### 权限问题

```bash
# 给脚本添加执行权限
chmod +x deploy.sh run.sh tts_synth.py test_tts.py
```

## 集成到 OpenClaw

将 skill 目录链接到 OpenClaw skills 目录：

```bash
ln -s ~/Documents/skills/tts-indextts2 ~/.openclaw/skills/tts-indextts2
```

然后在 OpenClaw 配置中启用该 skill。

## 许可证

根据 IndexTTS2 原始项目的许可证。

## 参考

- [IndexTTS2 GitHub](https://github.com/index-tts/index-tts2)
- [OpenClaw Skills](https://docs.openclaw.ai/skills)
- [Piper TTS](https://github.com/rhasspy/piper)

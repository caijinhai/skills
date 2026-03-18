---
name: tts-pocket
description: |
  文本转语音（TTS）skill。使用 go-pocket-tts（PocketTTS）实现，纯 Go 语音合成，无需 Python。
  当用户说"生成语音"、"文字转语音"、"TTS"时激活。
---

# PocketTTS (go-pocket-tts)

本 skill 使用纯 Go 实现的 PocketTTS 文本到语音合成工具。

## 安装

已预装在 `~/.openclaw/skills/tts-pocket/` 目录：

- `pockettts` - 主程序
- `pockettts-tools` - 工具程序

## 下载模型

首次使用需要下载模型文件。如果网络访问 Hugging Face 有问题，需要设置代理：

```bash
cd ~/.openclaw/skills/tts-pocket
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
./pockettts model download --hf-repo kyutai/pocket-tts-without-voice-cloning --out-dir models
```

模型会下载到 `models/` 目录（约 225MB）。

> 注：如果下载后 doctor 检查失败，但 synth 可以正常运行，说明模型可用。

## 使用方法

### CLI 合成语音

```bash
cd ~/.openclaw/skills/tts-pocket

# 基本用法
./pockettts synth --text "你好，我是蔡金海的语音助手" --out output.wav

# 指定语音 (需要先导出 voice embedding)
./pockettts synth --text "Hello" --voice mimi --out hello.wav
```

### HTTP 服务器

```bash
# 启动服务
cd ~/.openclaw/skills/tts-pocket
./pockettts serve
# 默认监听 :8080

# 调用 API
curl -X POST http://localhost:8080/tts -d "要转换的文本"

# 获取可用语音
curl http://localhost:8080/voices

# 健康检查
curl http://localhost:8080/health
```

### 查看帮助

```bash
./pockettts --help
./pockettts synth --help
./pockettts serve --help
```

## 飞书语音发送

脚本已包含：`~/.openclaw/skills/tts-pocket/send_voice.py`

### 使用方法

```bash
# 发送语音（默认使用 pockettts）
python3 ~/.openclaw/skills/tts-pocket/send_voice.py "文本内容" "接收者ID"

# 示例
python3 ~/.openclaw/skills/tts-pocket/send_voice.py "你好，我是海贼王" "ou_xxx"
```

### 发送流程
```
文本 → pockettts → WAV → ffmpeg → OPUS → 飞书上传 → 发送消息
```

### 注意事项

- 生成的格式是 WAV
- 语音文件建议控制在 30 秒内
- 发送语音需要飞书支持 OPUS 格式
- 如果模型下载失败，可能是网络问题，需要手动下载或配置代理

## 语音导出（高级）

如果需要自定义语音：

```bash
./pockettts export-voice --input speaker.wav --out my_voice.safetensors --id my-voice

# 使用自定义语音
./pockettts synth --text "Hello" --voice my_voice.safetensors --out out.wav
```
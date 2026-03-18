---
name: tts-apple
description: |
  文本转语音（TTS）skill。使用 macOS say 命令生成语音（本地离线，无需 API）。
  当用户说"生成语音"、"文字转语音"、"TTS"时激活。
---

# macOS TTS (say 命令)

本 skill 提供将文本转换为语音的功能。

## 方法

### 方法1：使用 macOS say 命令（推荐）

macOS 自带的 `say` 命令，无需 API Key：

```bash
# 生成语音文件
say -o output.m4a "要转换的文本"

# 指定语音
say -v " Ting-Ting" -o output.m4a "文本"  # 中文女声

# 查看可用语音
say -v "?" 
```

**可用中文语音**：
- `Ting-Ting` - 中文女声
- `Mei-Jia` - 中文女声

### 方法2：豆包 TTS API

豆包有 TTS 服务，但需要配置。API 端点：
```
POST https://ark.cn-beijing.volces.com/api/v3/tts
```

参数：
- `model`: 模型名（如 `cosyvoice-v1`）
- `input`: 要转换的文本
- `voice`: 语音类型

### 方法3：OpenAI TTS

```bash
curl -s "https://api.openai.com/v1/audio/speech" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "tts-1",
    "input": "文本",
    "voice": "alloy"
  }' -o output.mp3
```

## 使用示例

```bash
# 生成 10 秒测试语音
say -o test.m4a "你好，我是蔡金海的语音助手。很高兴为你服务。"

# 使用中文语音
say -v "Ting-Ting" -o test.m4a "你好，我是蔡金海的语音助手。"
```

## 飞书语音发送

脚本已包含：`~/.openclaw/skills/tts-apple/send_voice.py`

### 使用方法

```bash
# 发送语音
python3 ~/.openclaw/skills/tts-apple/send_voice.py "文本内容" "接收者ID" [语音]

# 示例
python3 ~/.openclaw/skills/tts-apple/send_voice.py "你好，我是海贼王" "ou_xxx"
python3 ~/.openclaw/skills/tts-apple/send_voice.py "你好" "ou_xxx" "Mei-Jia"
```

### 可用语音
- `Ting-Ting` - 中文女声（默认）
- `Mei-Jia` - 中文女声

### 发送流程
```
文本 → say 命令 → M4A → ffmpeg → OPUS → 飞书上传 → 发送消息
```

## 注意事项

- macOS say 生成的格式是 .m4a（ AAC 编码）
- 语音文件不要太长，建议控制在 30 秒内
- 发送语音需要飞书支持 OPUS 格式
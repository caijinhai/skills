# OpenClaw Skills Collection

TTS (Text-to-Speech) Skills for OpenClaw

## Skills

### tts-apple
- 使用 macOS say 命令生成语音
- 本地离线，无需网络
- 位置：`~/.openclaw/skills/tts-apple/`

### tts-edge
- 使用 Microsoft Edge TTS 生成语音
- 语音自然度高
- 位置：`~/.openclaw/skills/tts-edge/`

### tts-pocket
- 使用 PocketTTS (go-pocket-tts) 生成语音
- 纯 Go 实现，本地离线
- 位置：`~/.openclaw/skills/tts-pocket/`

## 使用方法

详见各 skill 目录下的 SKILL.md

## 飞书语音发送

各 skill 均包含 `send_voice.py` 脚本，发送语音到飞书：

```bash
python3 send_voice.py "文本内容" "接收者ID"
```

**注意**：使用前需要配置飞书凭证（环境变量或修改代码）

## 许可证

MIT
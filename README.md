# 🦸 OpenClaw Skills Collection

> 为 OpenClaw 打造的强大技能集合 | Build powerful skills for OpenClaw

[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skills-blue?style=flat-square)](https://github.com/openclaw/openclaw)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/caijinhai/skills?style=flat-square)](https://github.com/caijinhai/skills/stargazers)

本仓库收录了一系列为 [OpenClaw](https://github.com/openclaw/openclaw) 打造的实用技能 (Skills)，涵盖语音合成、信息监控、文件处理等领域。

---

## 📦 技能列表

### 🗣️ 语音合成 (TTS)

| Skill | 描述 | 特点 | 标签 |
|-------|------|------|------|
| [tts-apple](./tts-apple) | macOS Say 命令 | 本地离线、无需网络 | `macOS` `离线` |
| [tts-edge](./tts-edge) | Microsoft Edge TTS | 语音自然、支持多语音 | `云端` `高自然度` |
| [tts-pocket](./tts-pocket) | PocketTTS | 纯 Go 实现、本地离线 | `Go` `离线` |

### 📊 信息监控

| Skill | 描述 | 平台 | 标签 |
|-------|------|------|------|
| [github-trending](./github-trending) | GitHub Trending 监控 | GitHub | `趋势` `AI` `开源` |
| [twitter-trending](./twitter-trending) | Twitter Trending 监控 | Twitter | `趋势` `社交` |

### ☁️ 飞书集成

| Skill | 描述 | 功能 | 标签 |
|-------|------|------|------|
| [feishu-file-upload](./feishu-file-upload) | 飞书文件上传 | 云盘文件管理 | `飞书` `云盘` |
| [deepseek-api-search](./deepseek-api-search) | DeepSeek API 搜索 | AI 驱动的搜索能力 | `DeepSeek` `AI` `搜索` |

---

## 🚀 快速开始

### 1. 安装 Skills

将 skills 复制到 OpenClaw 目录：

```bash
# 方式一：克隆仓库
git clone https://github.com/caijinhai/skills.git ~/.openclaw/skills

# 方式二：选择性安装
cp -r tts-apple ~/.openclaw/skills/
cp -r tts-edge ~/.openclaw/skills/
```

### 2. 配置凭证

部分 skills 需要配置凭证，详见各目录下的 `SKILL.md`。

```bash
# 环境变量方式（推荐）
export FEISHU_APP_ID="your_app_id"
export FEISHU_APP_SECRET="your_app_secret"
```

### 3. 使用示例

```bash
# 发送飞书语音
python3 tts-edge/send_voice.py "你好，我是海贼王助手" "ou_xxx"
```

---

## 📁 目录结构

```
skills/
├── tts-apple/              # TTS: macOS Say
│   ├── SKILL.md
│   └── send_voice.py
├── tts-edge/               # TTS: Microsoft Edge
│   ├── SKILL.md
│   └── send_voice.py
├── tts-pocket/             # TTS: PocketTTS
│   ├── SKILL.md
│   └── send_voice.py
├── github-trending/        # 监控: GitHub Trending
│   ├── SKILL.md
│   ├── skill.yaml
│   └── scripts/
├── twitter-trending/       # 监控: Twitter Trending
│   ├── SKILL.md
│   ├── skill.yaml
│   └── scripts/
├── feishu-file-upload/     # 飞书: 文件上传
│   └── SKILL.md
├── deepseek-api-search/    # AI: DeepSeek 搜索
│   ├── SKILL.md
│   ├── README.md
│   └── scripts/
└── README.md
```

---

## 🏷️ 按标签分类

### 按类型

- **TTS (语音合成)**: `tts-apple`, `tts-edge`, `tts-pocket`
- **监控 (Monitoring)**: `github-trending`, `twitter-trending`
- **集成 (Integration)**: `feishu-file-upload`, `deepseek-api-search`

### 按平台

- **飞书**: `feishu-file-upload`
- **GitHub**: `github-trending`
- **Twitter**: `twitter-trending`
- **DeepSeek**: `deepseek-api-search`

### 按特性

- **本地离线**: `tts-apple`, `tts-pocket`
- **云端服务**: `tts-edge`, `deepseek-api-search`
- **AI 驱动**: `deepseek-api-search`, `github-trending`

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/xxx`)
3. 提交更改 (`git commit -m 'feat: 添加 xxx'`)
4. 推送分支 (`git push origin feature/xxx`)
5. 创建 Pull Request

---

## 📄 许可证

本项目采用 [MIT](LICENSE) 许可证。

---

## 🔗 相关链接

- [OpenClaw 官方](https://github.com/openclaw/openclaw)
- [OpenClaw 文档](https://docs.openclaw.ai)
- [ClawHub Skills](https://clawhub.com)

---

<div align="center">

**⭐ 如果对你有帮助，请点个 Star 支持一下！**

Made with ❤️ by [caijinhai](https://github.com/caijinhai)

</div>
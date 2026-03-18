# GitHub Trending Skill 配置说明

## 前置准备

### 1. 安装依赖工具
```bash
# 确保已安装 jq（JSON 处理）
brew install jq  # macOS
# 或
apt-get install jq  # Linux
```

### 2. 配置飞书多维表格

#### 创建多维表格
1. 在飞书云空间创建新的多维表格
2. 添加以下字段：

| 字段名 | 字段类型 | 必填 |
|--------|----------|------|
| 项目名称 | 文本 | ✅ |
| 排名 | 数字 | ✅ |
| 星标数 | 数字 | ✅ |
| 描述 | 文本 | ✅ |
| 语言 | 文本 | ✅ |
| URL | 文本 | ✅ |
| 标签 | 多选 | ✅ |
| 日期 | 日期 | ✅ |

#### 获取表格信息
- **app_token**: 从多维表格 URL 中获取（`/base/XXX` 中的 XXX）
- **table_id**: 从 URL 参数获取（`?table=YYY` 中的 YYY）

### 3. 配置 OpenClaw

确保 OpenClaw 已配置飞书应用权限：
```bash
openclaw configure --section feishu
```

需要的权限：
- `bitable:app_table_record:read`
- `bitable:app_table_record:write`
- `bitable:app:read`

## 浏览器登录说明

### GitHub Trending 无需登录
GitHub Trending 页面 (`https://github.com/trending`) 是公开页面，**无需登录**即可访问。

### 如需扩展其他需要登录的功能

如果未来需要访问需要登录的 GitHub 页面，请使用 `agent-browser` skill：

```bash
# 1. 启动浏览器并登录
openclaw browser start --profile="user"

# 2. 手动登录 GitHub
# 在浏览器中访问 https://github.com/login 并登录

# 3. 保存 Cookie（可选）
# Cookie 会自动保存在浏览器配置目录中
```

### Cookie 缓存位置
- **macOS**: `~/Library/Application Support/Google/Chrome/Default/Cookies`
- **Linux**: `~/.config/google-chrome/Default/Cookies`
- **Windows**: `%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cookies`

## 使用方法

### 基础使用
```bash
cd ~/Documents/skills/github-trending
chmod +x scripts/fetch-github-trending.sh
./scripts/fetch-github-trending.sh
```

### 高级用法
```bash
# 指定日期
./scripts/fetch-github-trending.sh --date 2026-03-16

# 指定数量
./scripts/fetch-github-trending.sh --limit 20

# 组合使用
./scripts/fetch-github-trending.sh --date 2026-03-16 --limit 15
```

### 定时任务
```bash
# 添加到 crontab（每天 9:00 执行）
crontab -e

# 添加以下行
0 9 * * * /Users/caijinhai/Documents/skills/github-trending/scripts/fetch-github-trending.sh
```

## 故障排查

### 问题 1: web_fetch 调用失败
```bash
# 检查 OpenClaw 配置
openclaw status

# 检查网络连接
curl -I https://github.com/trending
```

### 问题 2: 飞书 API 权限错误
```bash
# 检查飞书应用权限
openclaw tool feishu_app_scopes

# 重新配置飞书
openclaw configure --section feishu
```

### 问题 3: JSON 解析失败
```bash
# 检查 jq 是否安装
jq --version

# 安装 jq
brew install jq
```

## 输出示例

### JSON 输出
```json
[
  {
    "rank": 1,
    "name": "MiroFish - 群体智能引擎",
    "stars": 30195,
    "description": "A Simple and Universal Swarm Intelligence Engine",
    "language": "Python",
    "url": "https://github.com/666ghj/MiroFish",
    "tags": ["AI", "开源"]
  }
]
```

### 飞书多维表格记录
| 项目名称 | 排名 | 星标数 | 描述 | 语言 | URL | 标签 | 日期 |
|----------|------|--------|------|------|-----|------|------|
| MiroFish | 1 | 30195 | A Simple and Universal... | Python | https://... | AI,开源 | 2026/03/17 |

## 相关链接
- [GitHub Trending](https://github.com/trending)
- [OpenClaw 文档](https://docs.openclaw.ai)
- [飞书开放平台](https://open.feishu.cn/document)

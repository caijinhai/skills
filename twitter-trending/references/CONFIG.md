# Twitter Trending Skill 配置说明

## ⚠️ 重要提示
**Twitter/X 必须登录后才能访问完整内容**，请按照以下步骤配置浏览器登录。

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
| 推文内容 | 文本 | ✅ |
| 排名 | 数字 | ✅ |
| 作者 | 文本 | ✅ |
| 点赞数 | 数字 | ✅ |
| 转发数 | 数字 | ✅ |
| 链接 | URL | ✅ |
| 标签 | 多选 | ✅ |
| Text 3 | 日期 | ✅ |

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

## 🔐 浏览器登录配置（必需）

### 步骤 1: 启动浏览器
```bash
# 启动用户浏览器（使用已登录的 Chrome 配置）
openclaw browser start --profile="user"
```

### 步骤 2: 登录 Twitter/X
1. 在启动的浏览器中访问：https://twitter.com/login
2. 输入账号密码登录
3. 完成两步验证（如已启用）
4. 确保能正常访问 https://twitter.com/explore

### 步骤 3: 验证登录状态
```bash
# 检查浏览器状态
openclaw browser status

# 获取页面快照验证
openclaw browser snapshot --url="https://twitter.com/explore" --refs="aria"
```

### 步骤 4: Cookie 缓存说明

Cookie 会自动保存在浏览器配置目录中，**无需手动导出**。

#### Cookie 存储位置
- **macOS (Chrome)**: 
  ```
  ~/Library/Application Support/Google/Chrome/Default/Cookies
  ```
- **macOS (Edge)**:
  ```
  ~/Library/Application Support/Microsoft Edge/Default/Cookies
  ```
- **Linux (Chrome)**:
  ```
  ~/.config/google-chrome/Default/Cookies
  ```

#### Cookie 管理
```bash
# 查看浏览器配置文件
openclaw browser profiles

# 重启浏览器（刷新 Cookie）
openclaw browser stop
openclaw browser start --profile="user"
```

### 步骤 5: 使用 agent-browser skill（可选）

如果需要更复杂的浏览器操作，可以使用 `agent-browser` skill：

```bash
# 安装 agent-browser skill
openclaw skill install agent-browser

# 使用 skill 进行自动化操作
openclaw browser act --profile="user" --url="https://twitter.com/explore" --action="snapshot"
```

## 使用方法

### 基础使用
```bash
cd ~/Documents/skills/twitter-trending
chmod +x scripts/fetch-twitter-trending.sh
./scripts/fetch-twitter-trending.sh
```

### 高级用法
```bash
# 关键词过滤
./scripts/fetch-twitter-trending.sh --keyword "AI"

# 指定数量
./scripts/fetch-twitter-trending.sh --limit 20

# 使用特定浏览器配置
./scripts/fetch-twitter-trending.sh --profile="chrome-relay"

# 组合使用
./scripts/fetch-twitter-trending.sh --keyword "OpenAI" --limit 15
```

### 定时任务
```bash
# 添加到 crontab（每天 9:00 执行）
crontab -e

# 添加以下行
0 9 * * * /Users/caijinhai/Documents/skills/twitter-trending/scripts/fetch-twitter-trending.sh
```

## 故障排查

### 问题 1: 浏览器未启动
```bash
# 手动启动浏览器
openclaw browser start --profile="user"

# 检查状态
openclaw browser status
```

### 问题 2: Twitter 需要登录
```
错误：Please log in to continue

解决方案:
1. 确保已执行 openclaw browser start --profile="user"
2. 在浏览器中访问 https://twitter.com/login 并登录
3. 验证能访问 https://twitter.com/explore
4. 重新运行抓取脚本
```

### 问题 3: Cookie 过期
```bash
# 重启浏览器刷新 Cookie
openclaw browser stop
openclaw browser start --profile="user"

# 重新登录 Twitter
# 访问 https://twitter.com/login
```

### 问题 4: 飞书 API 权限错误
```bash
# 检查飞书应用权限
openclaw tool feishu_app_scopes

# 重新配置飞书
openclaw configure --section feishu
```

## 浏览器配置文件说明

| 配置文件 | 说明 | 使用场景 |
|----------|------|----------|
| `user` | 用户本地 Chrome | 日常使用，已登录状态 |
| `chrome-relay` | Chrome 扩展中继 | 需要浏览器扩展时 |
| `sandbox` | 隔离沙箱环境 | 测试，无需登录 |

## 输出示例

### JSON 输出
```json
[
  {
    "rank": 1,
    "content": "Introducing GPT-5: The next generation of AI",
    "author": "OpenAI",
    "likes": 150000,
    "retweets": 45000,
    "url": "https://twitter.com/OpenAI/status/123456789",
    "tags": ["AI", "趋势"]
  }
]
```

### 飞书多维表格记录
| 推文内容 | 排名 | 作者 | 点赞数 | 转发数 | 链接 | 标签 | 日期 |
|----------|------|------|--------|--------|------|------|------|
| GPT-5 发布 | 1 | OpenAI | 150000 | 45000 | https://... | AI,趋势 | 2026/03/17 |

## 注意事项

1. **遵守 Twitter 使用条款**，不要频繁抓取
2. **Cookie 安全**：不要分享 Cookie 文件
3. **登录状态维护**：定期重新登录以更新 Cookie
4. **速率限制**：建议每小时间隔至少 5 分钟

## 相关链接
- [Twitter/X](https://twitter.com)
- [OpenClaw 文档](https://docs.openclaw.ai)
- [飞书开放平台](https://open.feishu.cn/document)
- [agent-browser skill](https://clawhub.com/skills/agent-browser)

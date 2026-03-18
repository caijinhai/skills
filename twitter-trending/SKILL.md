# Twitter Trending Skill

## 功能描述
抓取 Twitter/X 热点话题和推文，支持关键词过滤和自定义数量，将结果写入飞书多维表格。

## 依赖 Skills
- `agent-browser`: **必需**，用于浏览器自动化操作和 Cookie 管理
- `feishu-doc`: 飞书文档操作（写入多维表格）

## 依赖 MCP 工具
- `browser`: 浏览器自动化（快照、点击、输入等）
- `feishu_bitable_create_record`: 创建多维表格记录
- `feishu_bitable_list_fields`: 获取表格字段结构
- `feishu_bitable_update_record`: 更新记录

## ⚠️ 重要说明
**Twitter/X 需要登录才能访问完整内容**，必须预先配置浏览器 Cookie。

## 目录结构
```
twitter-trending/
├── SKILL.md              # 技能说明文档（本文件）
├── skill.yaml            # 技能配置文件
├── scripts/
│   └── fetch-twitter-trending.sh  # 主执行脚本
├── references/
│   └── CONFIG.md         # 配置说明和登录指南
└── output/               # 输出目录（运行时生成）
```

## 使用方法

### 首次使用 - 配置浏览器登录
```bash
# 1. 启动浏览器
openclaw browser start --profile="user"

# 2. 手动登录 Twitter/X
# 访问 https://twitter.com/login 并登录

# 3. 运行抓取脚本
./scripts/fetch-twitter-trending.sh
```

### 基础使用
```bash
# 抓取今日 Twitter 热点
./scripts/fetch-twitter-trending.sh

# 指定关键词过滤
./scripts/fetch-twitter-trending.sh --keyword "AI"

# 指定数量
./scripts/fetch-twitter-trending.sh --limit 10
```

### 配置飞书多维表格
编辑 `skill.yaml` 配置目标多维表格信息：
```yaml
bitable:
  app_token: "U9LXbdWnYa2CZLs5Wq3cu1u5nef"
  table_id: "tblugTl6xfiQlKDW"
```

## 输出字段
| 字段名 | 类型 | 说明 |
|--------|------|------|
| 推文内容 | Text | 推文文本 |
| 排名 | Number | 热度排名 |
| 作者 | Text | 推文作者 |
| 点赞数 | Number | 点赞数量 |
| 转发数 | Number | 转发数量 |
| 链接 | URL | 推文链接 |
| 标签 | MultiSelect | 分类标签 |
| 日期 | DateTime | 抓取日期 |

## 注意事项
1. **必须预先登录 Twitter/X**，否则无法获取数据
2. Cookie 缓存在浏览器配置目录中
3. 建议定期重新登录以更新 Cookie
4. 遵守 Twitter 使用条款，不要频繁抓取

## 作者
每日资讯 Agent

## 版本
1.0.0

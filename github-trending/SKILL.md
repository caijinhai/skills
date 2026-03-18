# GitHub Trending Skill

## 功能描述
抓取 GitHub Trending 热点项目，支持自定义日期和排名数量，将结果写入飞书多维表格。

## 依赖 Skills
- `agent-browser`: 用于浏览器自动化操作（可选，用于需要登录的场景）
- `feishu-doc`: 飞书文档操作（写入多维表格）

## 依赖 MCP 工具
- `web_fetch`: 获取 GitHub Trending 页面内容
- `feishu_bitable_create_record`: 创建多维表格记录
- `feishu_bitable_list_fields`: 获取表格字段结构
- `feishu_bitable_update_record`: 更新记录（如需要）

## 目录结构
```
github-trending/
├── SKILL.md              # 技能说明文档（本文件）
├── skill.yaml            # 技能配置文件
├── scripts/
│   └── fetch-github-trending.sh  # 主执行脚本
├── references/
│   └── CONFIG.md         # 配置说明和登录指南
└── output/               # 输出目录（运行时生成）
```

## 使用方法

### 基础使用
```bash
# 抓取今日 GitHub Trending Top 10
./scripts/fetch-github-trending.sh

# 指定日期和数量
./scripts/fetch-github-trending.sh --date 2026-03-16 --limit 10
```

### 配置飞书多维表格
编辑 `skill.yaml` 配置目标多维表格信息：
```yaml
bitable:
  app_token: "YOUR_APP_TOKEN"
  table_id: "tblR69If9EY4FcEW"
```

## 输出字段
| 字段名 | 类型 | 说明 |
|--------|------|------|
| 项目名称 | Text | GitHub 项目名称 |
| 排名 | Number | Trending 排名 |
| 星标数 | Number | 总星标数 |
| 描述 | Text | 项目描述 |
| 语言 | Text | 主要编程语言 |
| GitHub 地址 | URL | 项目链接 |
| 标签 | MultiSelect | 分类标签 |
| 日期 | DateTime | 抓取日期 |

## 注意事项
1. GitHub Trending 页面无需登录即可访问
2. 建议设置合理的抓取频率，避免触发反爬
3. 飞书多维表格需预先创建好对应字段

## 作者
每日资讯 Agent

## 版本
1.0.0

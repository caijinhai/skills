---
name: feishu-file-upload
description: |
  上传本地文件到飞书云盘目录。支持 zip、pdf、图片等任意文件类型。
  当用户说"上传文件到云盘"、"上传到飞书目录"时激活。
---

# 飞书文件上传到云盘

本 skill 提供将本地文件上传到飞书云盘指定目录的功能。

## 限制说明

OpenClaw 的 `feishu_drive` 工具没有直接的 upload 功能。

### 可用的上传方法

#### 方法1：直接上传到目标目录（推荐）

直接用 `feishu_doc` 在目标目录创建文档，然后上传文件：

```json
// 第1步：在目标目录创建文档
{
  "action": "create",
  "title": "文件名",
  "folder_token": "目标目录token",
  "owner_open_id": "ou_15e92b9af898346b135de2d06eae50d5"
}

// 第2步：上传文件到该文档
{
  "action": "upload_file",
  "doc_token": "返回的document_id",
  "file_path": "/本地文件路径",
  "filename": "文件名"
}
```

**这是目前唯一可行的方法！**

#### 方法2：API 直接上传（推荐）

飞书官方 API：`POST /open-apis/drive/v1/files/upload_all`

**关键参数**：
- `parent_type`: 必须设为 `explorer`
- `parent_node`: 文件夹 token
- `size`: 文件大小（字节）

```json
// 使用 feishu_doc 直接调用（需要工具支持）
// 或者用 curl 调用：
curl -X POST 'https://open.feishu.cn/open-apis/drive/v1/files/upload_all' \
  -H 'Authorization: Bearer <token>' \
  -F 'file_name=xxx.zip' \
  -F 'parent_type=explorer' \
  -F 'parent_node=<folder_token>' \
  -F 'size=6618' \
  -F 'file=@/path/to/file.zip'
```

**注意**：需要飞书应用有 `drive:file:upload` 权限。

#### 关于 move 功能

`feishu_drive.move` 目前返回 404 错误，无法将文件移动到其他目录。

## 使用步骤

### 步骤 1：上传文件到临时文档

使用 `feishu_doc` 的 `upload_file` 动作：

```json
{
  "action": "upload_file",
  "doc_token": "临时文档token",
  "file_path": "/本地文件路径/xxx.zip",
  "filename": "上传后的文件名.zip"
}
```

**重要**：需要先创建一个临时文档来存放文件：

```json
{
  "action": "create",
  "title": "temp-upload-container",
  "owner_open_id": "ou_15e92b9af898346b135de2d06eae50d5"
}
```

### 步骤 2：获取上传后的 file_token

`upload_file` 返回的响应包含：
- `file_token`: 上传后的文件 token
- `file_name`: 文件名
- `size`: 文件大小

### 步骤 3：移动文件到目标目录（可选）

如果目标目录不是文档所在目录，需要移动文件：

```json
{
  "action": "move",
  "file_token": "文件token",
  "type": "file",
  "folder_token": "目标目录token"
}
```

**注意**：如果 move 失败（返回 404 或 not found），可能是因为：
1. 文件不在机器人可访问的范围
2. 权限不足

在这种情况下，可以直接将文件上传到目标文档（见下文"替代方案"）。

## 替代方案：直接上传到目标目录对应的文档

如果无法移动文件，可以直接在目标目录创建文档并上传：

```json
{
  "action": "create",
  "title": "文件名",
  "folder_token": "目标目录token",
  "owner_open_id": "ou_15e92b9af898346b135de2d06eae50d5"
}
```

然后用返回的 `document_id` 作为 `doc_token` 上传文件。

## 各 Agent 云盘目录 Token

| Agent | 目录名 | Token |
|-------|--------|-------|
| 海贼王助手 | 海贼王助手 | `Dj0PfHtTvlri25dBnhgcgbImnjh` |
| 每日资讯 | 每日资讯 | `SwIBf67DClHcSYdSd26cco4Jn6c` |
| 研发君 | 研发君 | `FeFlfRGsmlG8d8djDNkc5e0inqh` |
| 产品君 | 产品君 | `Ewo3fmXONlJuq2dq31tcMlA9nnb` |

## 完整示例：上传 zip 文件到海贼王助手目录

```json
// 第1步：创建临时文档
{
  "action": "create",
  "title": "temp-container",
  "owner_open_id": "ou_15e92b9af898346b135de2d06eae50d5"
}

// 返回: { "document_id": "ThHqdpTXRo4d97xZVs7cCA9gnOe", ... }

// 第2步：上传文件到临时文档
{
  "action": "upload_file",
  "doc_token": "ThHqdpTXRo4d97xZVs7cCA9gnOe",
  "file_path": "/Users/caijinhai/Documents/skills/github-trending.zip",
  "filename": "github-trending.zip"
}

// 返回: { "success": true, "file_token": "A4ExbCY0Yo28EcxZ3Z7caOUGnJh", ... }

// 第3步：移动到目标目录（如果需要）
{
  "action": "move",
  "file_token": "A4ExbCY0Yo28EcxZ3Z7caOUGnJh",
  "type": "file",
  "folder_token": "Dj0PfHtTvlri25dBnhgcgbImnjh"
}
```

## 验证上传结果

上传完成后，列出目标目录确认文件存在：

```json
{
  "action": "list",
  "folder_token": "目标目录token"
}
```

## 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 404 not found | 文件 token 无效或机器人无权访问 | 确认文件是否上传成功 |
| move 失败 | 权限不足或目录不存在 | 使用替代方案直接上传到目标目录 |
| 文件太大 | 超过 20MB 限制 | 使用飞书分片上传 API |

## 权限要求

需要飞书应用具有以下权限：
- `drive:file` - 云盘文件管理
- `drive:file:upload` - 上传文件
- `docx:document` - 文档创建
- `docx:document:create` - 创建文档

## 安全约束 ⚠️

**禁止上传包含敏感凭证的文件到飞书！**

上传前必须检查文件内容，**不能包含**以下敏感信息：
- `access_token`、`tenant_access_token`
- `app_id`、`app_secret`
- `api_key`、`apikey`
- `sk-`、`sk_`（OpenAI API Key 等）
- `secret`、`password`、`token`
- 任何以 `cli_` 开头的 ID
- `.env` 文件
- AWS keys、数据库连接字符串等

**如果需要上传配置文件，必须先脱敏**（用占位符替换真实凭证）。
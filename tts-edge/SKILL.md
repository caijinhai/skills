---
name: tts-edge
description: |
  文本转语音（TTS）skill。使用 Microsoft Edge TTS (edge-tts) 生成语音。
  语音自然度高，支持多种中文语音。当用户说"生成语音"、"文字转语音"、"TTS"时激活。
---

# Edge TTS (Microsoft)

本 skill 使用 Microsoft Edge 的 TTS 服务，生成自然的中文语音。

## 安装

```bash
pip3 install edge-tts requests --break-system-packages
```

## 可用语音

| 语音 ID | 说明 |
|---------|------|
| zh-CN-XiaoxiaoNeural | 晓晓（女声）- 默认 |
| zh-CN-YunxiNeural | 云希（男声） |
| zh-CN-YunyangNeural | 云扬（男声） |
| zh-CN-XiaoyouNeural | 晓悠（女声/年轻） |

完整列表请查看：https://speech.microsoft.com/portal

## 使用方法

### 生成语音文件

```bash
# 基本用法
python3 -c "
import asyncio
import edge_tts

async def main():
    tts = edge_tts.Communicate('你好，我是海贼王助手', 'zh-CN-XiaoxiaoNeural')
    await tts.save('/tmp/test.mp3')

asyncio.run(main())
"
```

### 发送语音到飞书

脚本已包含：`~/.openclaw/skills/tts-edge/send_voice.py`

```bash
# 发送语音
python3 ~/.openclaw/skills/tts-edge/send_voice.py "文本内容" "接收者ID" [语音]

# 示例
python3 ~/.openclaw/skills/tts-edge/send_voice.py "你好，我是海贼王" "ou_xxx"
python3 ~/.openclaw/skills/tts-edge/send_voice.py "你好" "ou_xxx" "zh-CN-YunxiNeural"
```

### Python 调用示例

```python
import asyncio
import edge_tts
import subprocess
import requests
import json

FEISHU_APP_ID = "cli_xxx"
FEISHU_APP_SECRET = "xxx"

def get_token():
    resp = requests.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
                        json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET})
    return resp.json()["tenant_access_token"]

async def text_to_opus(text, voice="zh-CN-XiaoxiaoNeural"):
    mp3 = "/tmp/temp.mp3"
    opus = "/tmp/voice.opus"
    
    # edge-tts -> MP3
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(mp3)
    
    # ffmpeg -> OPUS
    subprocess.run(["ffmpeg", "-i", mp3, "-c:a", "libopus", "-b:a", "24k", "-y", opus],
                  check=True, capture_output=True)
    
    import os
    os.remove(mp3)
    return opus

def upload_file(token, opus_path):
    url = "https://open.feishu.cn/open-apis/im/v1/files"
    headers = {"Authorization": f"Bearer {token}"}
    with open(opus_path, "rb") as f:
        resp = requests.post(url, headers=headers,
                           files={"file": f},
                           data={"file_type": "opus", "name": "voice.opus"})
    return resp.json()["data"]["file_key"]

def send_voice(token, receive_id, file_key):
    url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"receive_id": receive_id, "msg_type": "audio",
               "content": json.dumps({"file_key": file_key})}
    requests.post(url, headers=headers, json=payload)

# 使用
async def send():
    opus = await text_to_opus("你好")
    token = get_token()
    file_key = upload_file(token, opus)
    send_voice(token, "ou_xxx", file_key)

asyncio.run(send())
```

## 飞书语音发送流程

```
文本 → edge-tts → MP3 → ffmpeg → OPUS → 飞书上传 → 发送消息
```

## 注意事项

- 需要网络访问 edge-tts 服务
- 生成的 MP3 需要转为 OPUS 才能在飞书发送
- 飞书语音消息只能发送，不能下载（限制）
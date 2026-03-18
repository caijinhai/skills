#!/usr/bin/env python3
"""
飞书语音消息发送工具 - tts-edge
使用 Microsoft Edge TTS 生成语音

用法: python3 send_voice.py <文本> <接收者ID> [语音]
示例: python3 send_voice.py "你好" "ou_xxx" "zh-CN-XiaoxiaoNeural"
"""
import os
import sys
import asyncio
import edge_tts
import subprocess
import requests
import json

# 飞书配置
FEISHU_APP_ID = "YOUR_FEISHU_APP_ID"
FEISHU_APP_SECRET = "YOUR_FEISHU_APP_SECRET"
PROXY = {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}

def get_token():
    """获取飞书 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET
    }, proxies=PROXY)
    data = resp.json()
    if "tenant_access_token" not in data:
        print(f"获取 token 失败: {data}")
        sys.exit(1)
    return data["tenant_access_token"]

async def text_to_opus(text, voice="zh-CN-XiaoxiaoNeural"):
    """使用 edge-tts 生成 OPUS 文件"""
    mp3 = "/tmp/tts_edge.mp3"
    opus = "/tmp/tts_edge.opus"
    
    # edge-tts -> MP3
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(mp3)
    
    # ffmpeg -> OPUS
    subprocess.run([
        "ffmpeg", "-i", mp3, "-c:a", "libopus", "-b:a", "24k", "-y", opus
    ], check=True, capture_output=True)
    
    os.remove(mp3)
    return opus

def upload_file(token, opus_path):
    """上传 OPUS 到飞书"""
    url = "https://open.feishu.cn/open-apis/im/v1/files"
    headers = {"Authorization": f"Bearer {token}"}
    with open(opus_path, "rb") as f:
        resp = requests.post(url, headers=headers,
                           files={"file": f},
                           data={"file_type": "opus", "name": "voice.opus"},
                           proxies=PROXY)
    result = resp.json()
    if "data" not in result or "file_key" not in result.get("data", {}):
        print(f"上传失败: {result}")
        sys.exit(1)
    return result["data"]["file_key"]

def send_voice(token, receive_id, file_key):
    """发送语音消息"""
    url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "receive_id": receive_id,
        "msg_type": "audio",
        "content": json.dumps({"file_key": file_key})
    }
    resp = requests.post(url, headers=headers, json=payload, proxies=PROXY)
    result = resp.json()
    print(f"发送结果: {result}")
    return result

async def main_async(text, receive_id, voice):
    print(f"生成语音: {text[:20]}... (voice: {voice})")
    opus = await text_to_opus(text, voice)
    
    print("获取飞书 token...")
    token = get_token()
    
    print("上传到飞书...")
    file_key = upload_file(token, opus)
    
    print("发送语音消息...")
    send_voice(token, receive_id, file_key)
    
    os.remove(opus)
    print("完成！")

def main():
    if len(sys.argv) < 3:
        print("用法: python3 send_voice.py <文本> <接收者ID> [语音]")
        print("示例: python3 send_voice.py '你好' 'ou_xxx'")
        print("      python3 send_voice.py '你好' 'ou_xxx' 'zh-CN-YunxiNeural'")
        sys.exit(1)
    
    text = sys.argv[1]
    receive_id = sys.argv[2]
    voice = sys.argv[3] if len(sys.argv) > 3 else "zh-CN-XiaoxiaoNeural"
    
    asyncio.run(main_async(text, receive_id, voice))

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
飞书语音消息发送工具 - tts-apple
使用 macOS say 命令生成语音

用法: python3 send_voice.py <文本> <接收者ID> [语音名称]
示例: python3 send_voice.py "你好" "ou_xxx" "Ting-Ting"
"""
import os
import sys
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

def say_to_opus(text, voice="Ting-Ting"):
    """使用 say 命令生成 OPUS 文件"""
    m4a = "/tmp/tts_apple.m4a"
    opus = "/tmp/tts_apple.opus"
    
    # 生成 M4A
    cmd = ["say", "-v", voice, "-o", m4a, text]
    subprocess.run(cmd, check=True, capture_output=True)
    
    # 转 OPUS
    subprocess.run([
        "ffmpeg", "-i", m4a, "-c:a", "libopus", "-b:a", "24k", "-y", opus
    ], check=True, capture_output=True)
    
    os.remove(m4a)
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

def main():
    if len(sys.argv) < 3:
        print("用法: python3 send_voice.py <文本> <接收者ID> [语音]")
        print("示例: python3 send_voice.py '你好' 'ou_xxx' 'Ting-Ting'")
        sys.exit(1)
    
    text = sys.argv[1]
    receive_id = sys.argv[2]
    voice = sys.argv[3] if len(sys.argv) > 3 else "Ting-Ting"
    
    print(f"生成语音: {text[:20]}... (voice: {voice})")
    opus = say_to_opus(text, voice)
    
    print("获取飞书 token...")
    token = get_token()
    
    print("上传到飞书...")
    file_key = upload_file(token, opus)
    
    print("发送语音消息...")
    send_voice(token, receive_id, file_key)
    
    os.remove(opus)
    print("完成！")

if __name__ == "__main__":
    main()
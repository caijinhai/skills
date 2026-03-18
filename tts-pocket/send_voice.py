#!/usr/bin/env python3
"""
发送语音消息到飞书
依赖: edge-tts, ffmpeg, requests
安装: pip3 install edge-tts requests --break-system-packages
"""
import os
import asyncio
import edge_tts
import subprocess
import requests
import json
import sys

# ============= 配置 =============
# 飞书 Bot 凭证 (海贼王助手)
FEISHU_APP_ID = os.getenv("FEISHU_APP_ID", "")
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")

# 代理设置 (如需要)
PROXY = {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}

# ============= 飞书 API =============
def get_feishu_token():
    """获取 tenant_access_token"""
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

async def text_to_opus(text, voice="zh-CN-XiaoxiaoNeural", output="temp.opus"):
    """文本 -> MP3 -> OPUS"""
    mp3 = output.replace(".opus", ".mp3")
    
    # edge-tts 生成 MP3
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(mp3)
    
    # ffmpeg 转 OPUS
    subprocess.run([
        "ffmpeg", "-i", mp3, "-c:a", "libopus", "-b:a", "24k", "-y", output
    ], check=True, capture_output=True)
    
    os.remove(mp3)
    return output

def upload_feishu_file(token, opus_path):
    """上传 OPUS 文件到飞书，返回 file_key"""
    url = "https://open.feishu.cn/open-apis/im/v1/files"
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(opus_path, "rb") as f:
        files = {"file": f}
        data = {"file_type": "opus", "name": os.path.basename(opus_path)}
        resp = requests.post(url, headers=headers, files=files, data=data, proxies=PROXY)
    
    result = resp.json()
    if "data" not in result or "file_key" not in result.get("data", {}):
        print(f"上传失败: {result}")
        sys.exit(1)
    return result["data"]["file_key"]

def send_feishu_voice(token, receive_id, file_key):
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

# ============= 主函数 =============
async def send_voice(text, receive_id, voice="zh-CN-XiaoxiaoNeural"):
    """发送语音消息的主函数"""
    opus_file = "/tmp/voice.opus"
    
    print(f"生成语音: {text[:20]}...")
    opus_file = await text_to_opus(text, voice, opus_file)
    
    print("获取飞书 token...")
    token = get_feishu_token()
    
    print("上传到飞书...")
    file_key = upload_feishu_file(token, opus_file)
    
    print("发送语音消息...")
    result = send_feishu_voice(token, receive_id, file_key)
    
    # 清理
    os.remove(opus_file)
    return result

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python3 send_voice.py <文本> <接收者ID> [语音]")
        print("示例: python3 send_voice.py '你好' ou_xxx")
        sys.exit(1)
    
    text = sys.argv[1]
    receive_id = sys.argv[2]
    voice = sys.argv[3] if len(sys.argv) > 3 else "zh-CN-XiaoxiaoNeural"
    
    if not FEISHU_APP_ID or not FEISHU_APP_SECRET:
        print("错误: 请设置 FEISHU_APP_ID 和 FEISHU_APP_SECRET 环境变量")
        sys.exit(1)
    
    asyncio.run(send_voice(text, receive_id, voice))
